using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Messages;
using Microsoft.Xrm.Sdk.Query;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Tacatdp.ReportingProjection.Plugin
{
    internal sealed class ProjectionApplyResult
    {
        public int RepeatCount { get; set; }
        public int AnswerCount { get; set; }
        public int DeletedRepeatCount { get; set; }
        public int DeletedAnswerCount { get; set; }
    }

    internal sealed class DataverseProjectionRepository
    {
        private const string SubmissionVersionTable = "mp_submissionversion";
        private const string SubmissionTable = "mp_submission";
        private const string ReportTable = "mp_submissionreportrow";
        private const string RepeatTable = "mp_submissionrepeatrow";
        private const string AnswerTable = "mp_submissionanswer";

        private readonly IOrganizationService service;

        public DataverseProjectionRepository(IOrganizationService service)
        {
            this.service = service ?? throw new ArgumentNullException(nameof(service));
        }

        public Entity GetLatestVersionIdentity(string instanceId)
        {
            var query = new QueryExpression(SubmissionVersionTable)
            {
                ColumnSet = new ColumnSet(
                    "mp_submissionversionid",
                    "mp_versionnumber"),
                TopCount = 1,
            };
            query.Criteria.AddCondition("mp_instanceid", ConditionOperator.Equal, instanceId);
            query.Orders.Add(new OrderExpression("mp_versionnumber", OrderType.Descending));
            query.Orders.Add(new OrderExpression("createdon", OrderType.Descending));
            return service.RetrieveMultiple(query).Entities.FirstOrDefault();
        }

        public Entity GetVersion(Guid versionId)
        {
            return service.Retrieve(
                SubmissionVersionTable,
                versionId,
                new ColumnSet(
                    "mp_submissionversionid",
                    "mp_submission",
                    "mp_versionnumber",
                    "mp_instanceid",
                    "mp_xformsubmissionxml",
                    "mp_submissionjson",
                    "mp_createdat",
                    "createdon"));
        }

        public ProjectionSource LoadSource(Entity version)
        {
            if (version == null)
            {
                throw new InvalidPluginExecutionException("Projection source version was not found.");
            }

            var submissionReference = version.GetAttributeValue<EntityReference>("mp_submission");
            if (submissionReference == null || submissionReference.Id == Guid.Empty)
            {
                throw new InvalidPluginExecutionException("SubmissionVersion is missing its Submission lookup.");
            }

            var submission = service.Retrieve(
                SubmissionTable,
                submissionReference.Id,
                new ColumnSet(
                    "mp_submissionid",
                    "mp_instanceid",
                    "mp_useremail",
                    "mp_submittedat",
                    "mp_lifecyclestatus",
                    "mp_reviewstate"));
            var metadata = SubmissionMetadataParser.Parse(version.GetAttributeValue<string>("mp_submissionjson"));
            var instanceId = submission.GetAttributeValue<string>("mp_instanceid")
                ?? version.GetAttributeValue<string>("mp_instanceid")
                ?? string.Empty;
            var createdAt = version.GetAttributeValue<DateTime?>("mp_createdat")
                ?? version.GetAttributeValue<DateTime?>("createdon");

            return new ProjectionSource
            {
                SubmissionId = submission.Id,
                SubmissionVersionId = version.Id,
                FormVersionId = metadata.FormVersionId,
                InstanceId = instanceId,
                XmlFormId = metadata.XmlFormId,
                InstanceName = metadata.InstanceName,
                UserEmail = submission.GetAttributeValue<string>("mp_useremail"),
                SubmittedAt = submission.GetAttributeValue<DateTime?>("mp_submittedat"),
                UpdatedAt = createdAt,
                VersionNumber = version.GetAttributeValue<int?>("mp_versionnumber") ?? 1,
                LifecycleStatus = GetOptionValue(submission, "mp_lifecyclestatus", ProjectionStatuses.LifecycleSubmitted),
                ReviewState = GetOptionValue(submission, "mp_reviewstate", ProjectionStatuses.ReviewReceived),
                SubmissionXml = version.GetAttributeValue<string>("mp_xformsubmissionxml") ?? string.Empty,
                RepeatPaths = metadata.RepeatPaths,
            };
        }

        public ProjectionApplyResult Apply(ProjectionResult projection)
        {
            if (projection == null)
            {
                throw new ArgumentNullException(nameof(projection));
            }

            var rootId = UpsertReport(projection.Report, projection.Failed ? ProjectionStatuses.Failed : ProjectionStatuses.Stale);
            if (projection.Failed)
            {
                var failedAnswerDeletes = DeleteObsoleteChildren(AnswerTable, "mp_answerkey", rootId, new HashSet<string>(StringComparer.Ordinal));
                var failedRepeatDeletes = DeleteObsoleteChildren(RepeatTable, "mp_repeatrowkey", rootId, new HashSet<string>(StringComparer.Ordinal));
                return new ProjectionApplyResult
                {
                    DeletedAnswerCount = failedAnswerDeletes,
                    DeletedRepeatCount = failedRepeatDeletes,
                };
            }

            var repeatIds = new Dictionary<string, Guid>(StringComparer.Ordinal);
            foreach (var repeat in projection.RepeatRows)
            {
                repeatIds[repeat.RepeatRowKey] = UpsertRepeat(repeat, rootId);
            }

            foreach (var answer in projection.AnswerRows)
            {
                Guid repeatId = Guid.Empty;
                if (answer.RepeatRowKey != null && !repeatIds.TryGetValue(answer.RepeatRowKey, out repeatId))
                {
                    throw new InvalidPluginExecutionException("Projection answer references an unknown repeat row.");
                }
                UpsertAnswer(answer, rootId, repeatId);
            }

            var expectedAnswers = new HashSet<string>(projection.AnswerRows.Select(row => row.AnswerKey), StringComparer.Ordinal);
            var expectedRepeats = new HashSet<string>(projection.RepeatRows.Select(row => row.RepeatRowKey), StringComparer.Ordinal);
            var deletedAnswers = DeleteObsoleteChildren(AnswerTable, "mp_answerkey", rootId, expectedAnswers);
            var deletedRepeats = DeleteObsoleteChildren(RepeatTable, "mp_repeatrowkey", rootId, expectedRepeats);

            var ready = new Entity(ReportTable, rootId);
            SetReportAttributes(ready, projection.Report, ProjectionStatuses.Ready);
            service.Update(ready);
            return new ProjectionApplyResult
            {
                RepeatCount = projection.RepeatRows.Count,
                AnswerCount = projection.AnswerRows.Count,
                DeletedAnswerCount = deletedAnswers,
                DeletedRepeatCount = deletedRepeats,
            };
        }

        private Guid UpsertReport(ReportProjection report, int status)
        {
            var target = new Entity(ReportTable, "mp_reportkey", report.ReportKey);
            SetReportAttributes(target, report, status);
            return ExecuteUpsert(target);
        }

        private void SetReportAttributes(Entity target, ReportProjection report, int status)
        {
            target["mp_instanceid"] = report.InstanceId;
            target["mp_displayname"] = report.DisplayName;
            target["mp_useremail"] = report.UserEmail;
            target["mp_submittedat"] = report.SubmittedAt;
            target["mp_updatedat"] = report.UpdatedAt;
            target["mp_versionnumber"] = report.VersionNumber;
            target["mp_lifecyclestatus"] = new OptionSetValue(report.LifecycleStatus);
            target["mp_reviewstate"] = new OptionSetValue(report.ReviewState);
            target["mp_projectionstatus"] = new OptionSetValue(status);
            target["mp_projectedat"] = status == ProjectionStatuses.Stale ? null : (object)report.ProjectedAt;
            target["mp_projectionerror"] = status == ProjectionStatuses.Failed ? report.ProjectionError : null;
            target["mp_rootanswersjson"] = status == ProjectionStatuses.Ready ? report.RootAnswersJson : "{}";
            target["mp_submission"] = new EntityReference(SubmissionTable, report.SubmissionId);
            target["mp_submissionversion"] = new EntityReference(SubmissionVersionTable, report.SubmissionVersionId);
            target["mp_formversion"] = report.FormVersionId.HasValue
                ? (object)new EntityReference("mp_formversion", report.FormVersionId.Value)
                : null;
        }

        private Guid UpsertRepeat(RepeatProjection repeat, Guid rootId)
        {
            var target = new Entity(RepeatTable, "mp_repeatrowkey", repeat.RepeatRowKey)
            {
                ["mp_instanceid"] = repeat.InstanceId,
                ["mp_repeatpath"] = repeat.RepeatPath,
                ["mp_parentpath"] = repeat.ParentPath,
                ["mp_parentrepeatrowkey"] = repeat.ParentRepeatRowKey,
                ["mp_rowindex"] = repeat.RowIndex,
                ["mp_answersjson"] = repeat.AnswersJson,
                ["mp_projectedat"] = repeat.ProjectedAt,
                ["mp_submissionreportrow"] = new EntityReference(ReportTable, rootId),
                ["mp_submissionversion"] = new EntityReference(SubmissionVersionTable, repeat.SubmissionVersionId),
            };
            return ExecuteUpsert(target);
        }

        private void UpsertAnswer(AnswerProjection answer, Guid rootId, Guid repeatId)
        {
            var target = new Entity(AnswerTable, "mp_answerkey", answer.AnswerKey)
            {
                ["mp_instanceid"] = answer.InstanceId,
                ["mp_fieldpath"] = answer.FieldPath,
                ["mp_fieldname"] = answer.FieldName,
                ["mp_valuetext"] = answer.ValueText,
                ["mp_valuedecimal"] = answer.ValueDecimal.HasValue ? (object)answer.ValueDecimal.Value : null,
                ["mp_valuedate"] = answer.ValueDate.HasValue ? (object)answer.ValueDate.Value : null,
                ["mp_valueboolean"] = answer.ValueBoolean.HasValue ? (object)answer.ValueBoolean.Value : null,
                ["mp_valuejson"] = answer.ValueJson,
                ["mp_projectedat"] = answer.ProjectedAt,
                ["mp_submissionreportrow"] = new EntityReference(ReportTable, rootId),
                ["mp_submissionversion"] = new EntityReference(SubmissionVersionTable, answer.SubmissionVersionId),
                ["mp_submissionrepeatrow"] = repeatId == Guid.Empty ? null : (object)new EntityReference(RepeatTable, repeatId),
            };
            ExecuteUpsert(target);
        }

        private Guid ExecuteUpsert(Entity target)
        {
            var response = (UpsertResponse)service.Execute(new UpsertRequest { Target = target });
            if (response.Target != null && response.Target.Id != Guid.Empty)
            {
                return response.Target.Id;
            }

            var key = target.KeyAttributes.Single();
            var query = new QueryExpression(target.LogicalName)
            {
                ColumnSet = new ColumnSet(false),
                TopCount = 1,
            };
            query.Criteria.AddCondition(key.Key, ConditionOperator.Equal, key.Value);
            var row = service.RetrieveMultiple(query).Entities.SingleOrDefault();
            if (row == null)
            {
                throw new InvalidPluginExecutionException("Upsert completed without returning a target row.");
            }
            return row.Id;
        }

        private int DeleteObsoleteChildren(string table, string keyColumn, Guid rootId, ISet<string> expectedKeys)
        {
            var query = new QueryExpression(table)
            {
                ColumnSet = new ColumnSet(keyColumn),
            };
            query.Criteria.AddCondition("mp_submissionreportrow", ConditionOperator.Equal, rootId);
            var existing = service.RetrieveMultiple(query).Entities;
            var obsolete = ProjectionCore.FindObsolete(existing.Select(row => row.GetAttributeValue<string>(keyColumn)), expectedKeys);
            var deleted = 0;
            foreach (var row in existing.Where(row => obsolete.Contains(row.GetAttributeValue<string>(keyColumn))))
            {
                service.Delete(table, row.Id);
                deleted++;
            }
            return deleted;
        }

        private static int GetOptionValue(Entity entity, string attributeName, int fallback)
        {
            var value = entity.GetAttributeValue<OptionSetValue>(attributeName);
            return value == null ? fallback : value.Value;
        }
    }
}
