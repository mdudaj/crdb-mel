using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Crm.Sdk.Messages;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;

namespace Tacatdp.DeploymentPackage
{
    internal sealed class SeedDeployer
    {
        private const int BlockSize = 4 * 1024 * 1024;
        private readonly IOrganizationService service;

        internal SeedDeployer(IOrganizationService service)
        {
            this.service = service ?? throw new ArgumentNullException(nameof(service));
        }

        internal void Deploy(string xformPath)
        {
            ValidateXForm(xformPath);
            UpsertProject();
            UpsertForm();
            UpsertFormVersion();
            UpsertFormAssignments();
            UpsertFormAttachment();
            UploadFile(xformPath);
            VerifySeed();
        }

        private void UpsertProject()
        {
            var project = new Entity("mp_project", SeedManifest.ProjectId)
            {
                ["mp_projectcode"] = "TACATDP",
                ["mp_name"] = "TACATDP Impact Monitoring",
                ["mp_description"] = "TACATDP Power Pages ODK Web Forms MVP project.",
                ["mp_lifecyclestatus"] = new OptionSetValue(100000000)
            };
            Upsert(project);
        }

        private void UpsertForm()
        {
            var form = new Entity("mp_form", SeedManifest.FormId)
            {
                ["mp_project"] = new EntityReference("mp_project", SeedManifest.ProjectId),
                ["mp_xmlformid"] = "tacatdp_impact_evaluation",
                ["mp_name"] = "TACATDP Impact Evaluation",
                ["mp_description"] = "TACATDP Impact Evaluation form compiled from XLSForm for ODK Web Forms testing.",
                ["mp_lifecyclestatus"] = new OptionSetValue(100000001)
            };
            Upsert(form);
        }

        private void UpsertFormVersion()
        {
            var version = new Entity("mp_formversion", SeedManifest.FormVersionId)
            {
                ["mp_form"] = new EntityReference("mp_form", SeedManifest.FormId),
                ["mp_version"] = SeedManifest.FormVersion,
                ["mp_hash"] = "xlsform-20260714000200000-12b955fcf423",
                ["mp_xformxml"] = "dataverse-file:" + SeedManifest.XFormFileName,
                ["mp_webformsenabled"] = true,
                ["mp_lifecyclestatus"] = new OptionSetValue(100000001),
                ["mp_publishedat"] = new DateTime(2026, 7, 14, 8, 45, 26, DateTimeKind.Utc)
            };
            Upsert(version);
        }

        private void UpsertFormAttachment()
        {
            var attachment = new Entity("mp_formattachment", SeedManifest.FormAttachmentId)
            {
                ["mp_formversion"] = new EntityReference("mp_formversion", SeedManifest.FormVersionId),
                ["mp_filename"] = SeedManifest.XFormFileName,
                ["mp_mediatype"] = "application/xml"
            };
            Upsert(attachment);
        }

        private void UpsertFormAssignments()
        {
            foreach (var seed in SeedManifest.FormAssignments)
            {
                var assignment = new Entity("mp_formassignment", seed.Item1)
                {
                    ["mp_assignmentkey"] = "tacatdp_impact_evaluation:" + seed.Item2,
                    ["mp_formversion"] = new EntityReference("mp_formversion", SeedManifest.FormVersionId),
                    ["mp_useremail"] = seed.Item2,
                    ["mp_lifecyclestatus"] = new OptionSetValue(100000000)
                };
                Upsert(assignment);
            }
        }

        private void Upsert(Entity entity)
        {
            if (Exists(entity.LogicalName, entity.Id))
            {
                service.Update(entity);
                return;
            }

            service.Create(entity);
        }

        private bool Exists(string logicalName, Guid id)
        {
            var query = new QueryExpression(logicalName)
            {
                ColumnSet = new ColumnSet(false),
                TopCount = 1
            };
            query.Criteria.AddCondition(logicalName + "id", ConditionOperator.Equal, id);
            return service.RetrieveMultiple(query).Entities.Count == 1;
        }

        private void UploadFile(string xformPath)
        {
            var initialize = (InitializeFileBlocksUploadResponse)service.Execute(
                new InitializeFileBlocksUploadRequest
                {
                    Target = new EntityReference("mp_formattachment", SeedManifest.FormAttachmentId),
                    FileAttributeName = "mp_file",
                    FileName = SeedManifest.XFormFileName
                });

            var blockIds = new List<string>();
            using (var stream = File.OpenRead(xformPath))
            {
                var buffer = new byte[BlockSize];
                int bytesRead;
                while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                {
                    var block = new byte[bytesRead];
                    Buffer.BlockCopy(buffer, 0, block, 0, bytesRead);
                    var blockId = Convert.ToBase64String(Encoding.UTF8.GetBytes(Guid.NewGuid().ToString("N")));
                    blockIds.Add(blockId);
                    service.Execute(new UploadBlockRequest
                    {
                        BlockData = block,
                        BlockId = blockId,
                        FileContinuationToken = initialize.FileContinuationToken
                    });
                }
            }

            service.Execute(new CommitFileBlocksUploadRequest
            {
                BlockList = blockIds.ToArray(),
                FileContinuationToken = initialize.FileContinuationToken,
                FileName = SeedManifest.XFormFileName,
                MimeType = "application/xml"
            });
        }

        private void VerifySeed()
        {
            var required = new List<Tuple<string, Guid>>
            {
                Tuple.Create("mp_project", SeedManifest.ProjectId),
                Tuple.Create("mp_form", SeedManifest.FormId),
                Tuple.Create("mp_formversion", SeedManifest.FormVersionId),
                Tuple.Create("mp_formattachment", SeedManifest.FormAttachmentId)
            };
            required.AddRange(SeedManifest.FormAssignments.Select(seed => Tuple.Create("mp_formassignment", seed.Item1)));

            var missing = required.Where(item => !Exists(item.Item1, item.Item2)).Select(item => item.Item1).ToArray();
            if (missing.Length > 0)
            {
                throw new InvalidOperationException("TACATDP seed verification failed for: " + string.Join(", ", missing));
            }

            var attachment = service.Retrieve(
                "mp_formattachment",
                SeedManifest.FormAttachmentId,
                new ColumnSet("mp_file", "mp_filename", "mp_formversion"));
            if (!attachment.Attributes.Contains("mp_file"))
            {
                throw new InvalidOperationException("TACATDP XForm upload did not populate mp_formattachment.mp_file.");
            }
        }

        private static void ValidateXForm(string xformPath)
        {
            if (!File.Exists(xformPath))
            {
                throw new FileNotFoundException("The packaged TACATDP XForm was not found.", xformPath);
            }

            string hash;
            using (var stream = File.OpenRead(xformPath))
            using (var sha256 = SHA256.Create())
            {
                hash = string.Concat(sha256.ComputeHash(stream).Select(value => value.ToString("x2")));
            }

            if (!string.Equals(hash, SeedManifest.XFormSha256, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidDataException("The packaged TACATDP XForm SHA-256 does not match the approved artifact.");
            }
        }
    }
}
