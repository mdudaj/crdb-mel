using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;
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

        internal void Deploy(string xformPath, string baselineBridgePath)
        {
            ValidateXForm(xformPath);
            UpsertProject();
            UpsertForm();
            UpsertFormVersion();
            UpsertFormAssignments();
            UpsertFormAttachment();
            UploadFile(xformPath);
            DeployBaselineBridge(baselineBridgePath);
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
                ["mp_hash"] = "xlsform-2608130924-1fa53c3517f6",
                ["mp_xformxml"] = "dataverse-file:" + SeedManifest.XFormFileName,
                ["mp_webformsenabled"] = true,
                ["mp_lifecyclestatus"] = new OptionSetValue(100000001),
                ["mp_publishedat"] = new DateTime(2026, 8, 13, 9, 24, 0, DateTimeKind.Utc)
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

        private void DeployBaselineBridge(string baselineBridgePath)
        {
            if (string.IsNullOrWhiteSpace(baselineBridgePath) || !File.Exists(baselineBridgePath))
            {
                Trace.TraceInformation("No TACATDP baseline bridge import asset found; skipping baseline bridge import.");
                return;
            }

            var serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue, RecursionLimit = 256 };
            var asset = serializer.Deserialize<Dictionary<string, object>>(File.ReadAllText(baselineBridgePath, Encoding.UTF8));
            var formVersion = GetString(asset, "formVersion");
            if (!string.Equals(formVersion, SeedManifest.FormVersion, StringComparison.Ordinal))
            {
                throw new InvalidDataException("Baseline bridge asset form version does not match the packaged XForm version.");
            }

            var rows = asset.ContainsKey("rows") ? asset["rows"] as IEnumerable : null;
            if (rows == null)
            {
                throw new InvalidDataException("Baseline bridge asset has no rows array.");
            }

            var projectId = RequireId(
                "mp_project",
                new ConditionExpression("mp_projectcode", ConditionOperator.Equal, "TACATDP"));
            var formVersionId = RequireId(
                "mp_formversion",
                new ConditionExpression("mp_version", ConditionOperator.Equal, SeedManifest.FormVersion));

            var imported = 0;
            var identifierCount = 0;
            foreach (var item in rows)
            {
                var row = item as Dictionary<string, object>;
                if (row == null)
                {
                    throw new InvalidDataException("Baseline bridge asset contains an invalid row.");
                }

                UpsertBaselineRow(row, projectId, formVersionId, ref identifierCount);
                imported++;
                if (imported % 100 == 0)
                {
                    Trace.TraceInformation("TACATDP baseline bridge import progress: " + imported + " rows.");
                }
            }

            Trace.TraceInformation("TACATDP baseline bridge import completed. Rows: " + imported + ", identifiers: " + identifierCount + ".");
        }

        private void UpsertBaselineRow(Dictionary<string, object> row, Guid projectId, Guid formVersionId, ref int identifierCount)
        {
            var rowNumber = GetString(row, "rowNumber");
            var uuid = GetString(row, "uuid");
            var customerId = GetString(row, "customerId");
            var customerName = GetString(row, "customerName");
            var phone = GetString(row, "phone");
            var region = GetString(row, "region");
            var district = GetString(row, "district");
            var sourceKey = GetString(row, "sourceKey");
            var instanceId = GetString(row, "instanceId");
            var versionKey = GetString(row, "versionKey");
            var linkKey = GetString(row, "linkKey");
            var submissionJson = GetString(row, "submissionJson");
            var xformXml = GetString(row, "xformXml");
            var displayName = string.IsNullOrWhiteSpace(customerName) ? "Beneficiary " + rowNumber : customerName;
            var now = DateTime.UtcNow;

            var submission = new Entity("mp_submission")
            {
                ["mp_instanceid"] = instanceId,
                ["mp_formversion"] = new EntityReference("mp_formversion", formVersionId),
                ["mp_lifecyclestatus"] = new OptionSetValue(100000001),
                ["mp_reviewstate"] = new OptionSetValue(100000000),
                ["mp_updatedat"] = now
            };
            SetDateIfPresent(submission, "mp_startedat", GetString(row, "startedAt"));
            SetDateIfPresent(submission, "mp_submittedat", GetString(row, "submittedAt"));
            if (!submission.Attributes.Contains("mp_submittedat"))
            {
                submission["mp_submittedat"] = now;
            }
            var submissionId = UpsertBy(
                submission,
                new ConditionExpression("mp_instanceid", ConditionOperator.Equal, instanceId));

            var submissionVersion = new Entity("mp_submissionversion")
            {
                ["mp_versionkey"] = versionKey,
                ["mp_submission"] = new EntityReference("mp_submission", submissionId),
                ["mp_instanceid"] = instanceId,
                ["mp_versionnumber"] = 1,
                ["mp_current"] = true,
                ["mp_createdat"] = now,
                ["mp_xformsubmissionxml"] = xformXml,
                ["mp_submissionjson"] = submissionJson
            };
            UpsertBy(submissionVersion, new ConditionExpression("mp_versionkey", ConditionOperator.Equal, versionKey));

            var tracked = new Entity("mp_trackedentity")
            {
                ["mp_project"] = new EntityReference("mp_project", projectId),
                ["mp_entitytype"] = new OptionSetValue(100000000),
                ["mp_entitykey"] = sourceKey,
                ["mp_displayname"] = displayName,
                ["mp_status"] = new OptionSetValue(100000000)
            };
            var trackedId = UpsertBy(
                tracked,
                new ConditionExpression("mp_project", ConditionOperator.Equal, projectId),
                new ConditionExpression("mp_entitytype", ConditionOperator.Equal, 100000000),
                new ConditionExpression("mp_entitykey", ConditionOperator.Equal, sourceKey));

            EnsureIdentifier(trackedId, 100000000, uuid, ref identifierCount);
            EnsureIdentifier(trackedId, 100000006, customerId, ref identifierCount);
            EnsureIdentifier(trackedId, 100000002, phone, ref identifierCount);

            var profile = new Entity("mp_beneficiaryprofile")
            {
                ["mp_name"] = displayName,
                ["mp_trackedentity"] = new EntityReference("mp_trackedentity", trackedId),
                ["mp_project"] = new EntityReference("mp_project", projectId),
                ["mp_beneficiarycategory"] = new OptionSetValue(100000000),
                ["mp_verificationstatus"] = new OptionSetValue(100000000),
                ["mp_datasource"] = "Kobo baseline import",
                ["mp_lastupdatedat"] = now
            };
            SetStringIfPresent(profile, "mp_region", region);
            SetStringIfPresent(profile, "mp_district", district);
            UpsertBy(profile, new ConditionExpression("mp_trackedentity", ConditionOperator.Equal, trackedId));

            var link = new Entity("mp_beneficiarysubmissionlink")
            {
                ["mp_linkkey"] = linkKey,
                ["mp_trackedentity"] = new EntityReference("mp_trackedentity", trackedId),
                ["mp_submission"] = new EntityReference("mp_submission", submissionId),
                ["mp_relationshiptype"] = new OptionSetValue(100000000),
                ["mp_completeness"] = 100,
                ["mp_reviewstatus"] = new OptionSetValue(100000000)
            };
            UpsertBy(link, new ConditionExpression("mp_linkkey", ConditionOperator.Equal, linkKey));
        }

        private void EnsureIdentifier(Guid trackedId, int identifierType, string value, ref int identifierCount)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return;
            }

            var identifier = new Entity("mp_entityidentifier")
            {
                ["mp_trackedentity"] = new EntityReference("mp_trackedentity", trackedId),
                ["mp_identifiertype"] = new OptionSetValue(identifierType),
                ["mp_identifiervalue"] = value,
                ["mp_status"] = new OptionSetValue(100000000)
            };
            UpsertBy(
                identifier,
                new ConditionExpression("mp_trackedentity", ConditionOperator.Equal, trackedId),
                new ConditionExpression("mp_identifiertype", ConditionOperator.Equal, identifierType),
                new ConditionExpression("mp_identifiervalue", ConditionOperator.Equal, value));
            identifierCount++;
        }

        private Guid UpsertBy(Entity entity, params ConditionExpression[] conditions)
        {
            var id = FindId(entity.LogicalName, conditions);
            if (id.HasValue)
            {
                entity.Id = id.Value;
                service.Update(entity);
                return id.Value;
            }

            return service.Create(entity);
        }

        private Guid RequireId(string logicalName, params ConditionExpression[] conditions)
        {
            var id = FindId(logicalName, conditions);
            if (!id.HasValue)
            {
                throw new InvalidOperationException("Required Dataverse row not found: " + logicalName);
            }

            return id.Value;
        }

        private Guid? FindId(string logicalName, params ConditionExpression[] conditions)
        {
            var query = new QueryExpression(logicalName)
            {
                ColumnSet = new ColumnSet(false),
                TopCount = 1
            };
            foreach (var condition in conditions)
            {
                query.Criteria.AddCondition(condition);
            }

            var rows = service.RetrieveMultiple(query).Entities;
            return rows.Count == 0 ? (Guid?)null : rows[0].Id;
        }

        private static string GetString(Dictionary<string, object> source, string key)
        {
            if (!source.ContainsKey(key) || source[key] == null)
            {
                return string.Empty;
            }

            return Convert.ToString(source[key]) ?? string.Empty;
        }

        private static void SetStringIfPresent(Entity entity, string attribute, string value)
        {
            if (!string.IsNullOrWhiteSpace(value))
            {
                entity[attribute] = value;
            }
        }

        private static void SetDateIfPresent(Entity entity, string attribute, string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return;
            }

            if (DateTime.TryParse(value, out var parsed))
            {
                entity[attribute] = parsed.ToUniversalTime();
            }
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
