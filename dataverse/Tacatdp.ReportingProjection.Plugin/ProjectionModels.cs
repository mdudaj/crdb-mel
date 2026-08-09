using System;
using System.Collections.Generic;

namespace Tacatdp.ReportingProjection.Plugin
{
    public static class ProjectionStatuses
    {
        public const int Ready = 100000000;
        public const int Stale = 100000001;
        public const int Failed = 100000002;
        public const int LifecycleSubmitted = 100000001;
        public const int ReviewReceived = 100000000;
    }

    public sealed class ProjectionSource
    {
        public ProjectionSource()
        {
            RepeatPaths = new HashSet<string>(StringComparer.Ordinal);
        }

        public Guid SubmissionId { get; set; }
        public Guid SubmissionVersionId { get; set; }
        public Guid? FormVersionId { get; set; }
        public string InstanceId { get; set; }
        public string XmlFormId { get; set; }
        public string InstanceName { get; set; }
        public string UserEmail { get; set; }
        public DateTime? SubmittedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public int VersionNumber { get; set; }
        public int LifecycleStatus { get; set; }
        public int ReviewState { get; set; }
        public string SubmissionXml { get; set; }
        public ISet<string> RepeatPaths { get; set; }
    }

    public sealed class ReportProjection
    {
        public string ReportKey { get; set; }
        public string InstanceId { get; set; }
        public string DisplayName { get; set; }
        public string UserEmail { get; set; }
        public DateTime? SubmittedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public int VersionNumber { get; set; }
        public int LifecycleStatus { get; set; }
        public int ReviewState { get; set; }
        public int ProjectionStatus { get; set; }
        public DateTime ProjectedAt { get; set; }
        public string ProjectionError { get; set; }
        public string RootAnswersJson { get; set; }
        public Guid SubmissionId { get; set; }
        public Guid SubmissionVersionId { get; set; }
        public Guid? FormVersionId { get; set; }
    }

    public sealed class RepeatProjection
    {
        public string RepeatRowKey { get; set; }
        public string InstanceId { get; set; }
        public string RepeatPath { get; set; }
        public string ParentPath { get; set; }
        public string ParentRepeatRowKey { get; set; }
        public int RowIndex { get; set; }
        public string AnswersJson { get; set; }
        public DateTime ProjectedAt { get; set; }
        public Guid SubmissionVersionId { get; set; }
    }

    public sealed class AnswerProjection
    {
        public string AnswerKey { get; set; }
        public string RepeatRowKey { get; set; }
        public string InstanceId { get; set; }
        public string FieldPath { get; set; }
        public string FieldName { get; set; }
        public string ValueText { get; set; }
        public decimal? ValueDecimal { get; set; }
        public DateTime? ValueDate { get; set; }
        public bool? ValueBoolean { get; set; }
        public string ValueJson { get; set; }
        public DateTime ProjectedAt { get; set; }
        public Guid SubmissionVersionId { get; set; }
    }

    public sealed class ProjectionResult
    {
        public ProjectionResult(ReportProjection report)
        {
            Report = report;
            RepeatRows = new List<RepeatProjection>();
            AnswerRows = new List<AnswerProjection>();
        }

        public ReportProjection Report { get; }
        public IList<RepeatProjection> RepeatRows { get; }
        public IList<AnswerProjection> AnswerRows { get; }
        public bool Failed => Report.ProjectionStatus == ProjectionStatuses.Failed;
    }
}
