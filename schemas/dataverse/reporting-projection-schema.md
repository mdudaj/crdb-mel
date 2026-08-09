# Reporting Projection Dataverse Schema

Status: review-ready, no environment write.

This schema adds derived reporting tables for the Monitoring Tool Data, Exports, and Power BI surfaces. It does not replace canonical ODK-style storage. `Submissions`, `SubmissionVersions`, submitted XML, and JSON payload metadata remain the source of truth.

## Tables

### SubmissionReportRows

One current reporting row per submitted ODK instance for table browsing, root CSV export, and Power BI root facts.

Primary name column: `ReportKey`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `ReportKey` | `Text` | Yes | Stable key: formVersionId:instanceId. |
| `Project` | `Lookup:Projects` | No | Project snapshot for filtering and future multi-project reporting. |
| `Form` | `Lookup:Forms` | No | Form identity snapshot for project dashboards. |
| `FormVersion` | `Lookup:FormVersions` | Yes | Source form version used by the submitted payload. |
| `Submission` | `Lookup:Submissions` | Yes | Canonical submission header. |
| `SubmissionVersion` | `Lookup:SubmissionVersions` | Yes | Current source submission version used to build the projection. |
| `InstanceId` | `Text` | Yes | ODK instanceId. |
| `DisplayName` | `Text` | No | Computed XLSForm instance_name or fallback display title. |
| `UserEmail` | `Text` | No | Submitter email snapshot. |
| `SubmittedAt` | `DateTime` | No | Submission timestamp. |
| `UpdatedAt` | `DateTime` | No | Latest canonical submission update timestamp. |
| `VersionNumber` | `WholeNumber` | Yes | Current source submission version number. |
| `LifecycleStatus` | `Choice` | No | Draft/Submitted/Locked. |
| `ReviewState` | `Choice` | No | Received/Edited/HasIssues/Rejected/Approved. |
| `ProjectionStatus` | `Choice` | Yes | Ready/Stale/Failed. |
| `ProjectedAt` | `DateTime` | No | Projection build timestamp. |
| `ProjectionError` | `MultilineText` | No | Last projection error if status is Failed. |
| `RootAnswersJson` | `MultilineText` | No | Compact root-level answer map for prototype table/detail UX. Not canonical. |

### SubmissionRepeatRows

One reporting row per repeat group instance, related to the root report row for XLSX sheets and Power BI repeat facts.

Primary name column: `RepeatRowKey`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `RepeatRowKey` | `Text` | Yes | Stable key: formVersionId:instanceId:repeatPath:parentPath:rowIndex. |
| `SubmissionReportRow` | `Lookup:SubmissionReportRows` | Yes | Root reporting row. |
| `SubmissionVersion` | `Lookup:SubmissionVersions` | Yes | Current source submission version used to build this repeat row. |
| `InstanceId` | `Text` | Yes | ODK instanceId snapshot. |
| `RepeatPath` | `Text` | Yes | XForm repeat path. |
| `ParentPath` | `Text` | No | Parent repeat/root path for nested repeat joins. |
| `ParentRepeatRowKey` | `Text` | No | Parent repeat row key for nested repeats. |
| `RowIndex` | `WholeNumber` | Yes | Zero-based repeat instance index under the parent. |
| `AnswersJson` | `MultilineText` | No | Compact answer map for this repeat row. |
| `ProjectedAt` | `DateTime` | No | Projection build timestamp. |

### SubmissionAnswers

One field answer per root or repeat context for flexible filtering, field-level audit, and Power BI long-format analysis.

Primary name column: `AnswerKey`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `AnswerKey` | `Text` | Yes | Stable key: formVersionId:instanceId:repeatRowKey:fieldPath. |
| `SubmissionReportRow` | `Lookup:SubmissionReportRows` | Yes | Root reporting row. |
| `SubmissionRepeatRow` | `Lookup:SubmissionRepeatRows` | No | Repeat row context when answer belongs to a repeat group. |
| `SubmissionVersion` | `Lookup:SubmissionVersions` | Yes | Current source submission version used to build this answer. |
| `InstanceId` | `Text` | Yes | ODK instanceId snapshot. |
| `FieldPath` | `Text` | Yes | XForm field path. |
| `FieldName` | `Text` | No | Leaf field name for display and exports. |
| `FieldLabel` | `Text` | No | Resolved label for the selected export language when available. |
| `ValueText` | `MultilineText` | No | Text representation of the answer. |
| `ValueDecimal` | `Decimal` | No | Numeric decimal projection when parseable. |
| `ValueDate` | `DateTime` | No | Date/dateTime projection when parseable. |
| `ValueBoolean` | `Boolean` | No | Boolean projection when parseable. |
| `ValueJson` | `MultilineText` | No | Structured value snapshot for select-many, geopoint, or future compound values. |
| `ProjectedAt` | `DateTime` | No | Projection build timestamp. |

### ExportSettings

Named user/admin export configurations for repeatable CSV/XLSX downloads and Power BI guidance.

Primary name column: `Name`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `ExportKey` | `Text` | Yes | Stable key: projectCode:formId:name. |
| `Name` | `Text` | Yes | Export configuration display name. |
| `Project` | `Lookup:Projects` | No | Project scope. |
| `Form` | `Lookup:Forms` | No | Form scope. |
| `FormVersion` | `Lookup:FormVersions` | No | Optional version-specific export scope. |
| `Format` | `Choice` | Yes | CSV/XLSX. |
| `Scope` | `Choice` | Yes | CurrentFilters/AllSubmitted/SelectedRecords. |
| `IncludeRepeats` | `Boolean` | No | True for XLSX exports that include repeat sheets. |
| `UseLabels` | `Boolean` | No | True to use labels instead of XML field names where available. |
| `Language` | `Text` | No | Preferred label language, for example en or sw. |
| `IncludeMediaLinks` | `Boolean` | No | Whether export output includes attachment/media links. |
| `FilterJson` | `MultilineText` | No | Saved filters for date, submitter, status, review state, or project-specific fields. |
| `ColumnJson` | `MultilineText` | No | Saved selected/exported columns. |
| `CreatedByEmail` | `Text` | No | Creator email snapshot for support. |
| `CreatedAt` | `DateTime` | No | Export setting creation timestamp. |
| `UpdatedAt` | `DateTime` | No | Export setting update timestamp. |

## Alternate Keys

| Table | Key | Columns | Purpose |
| --- | --- | --- | --- |
| `SubmissionReportRows` | `ak_submission_report_root` | `ReportKey` | Stable text key for idempotent root projection upserts. |
| `SubmissionRepeatRows` | `ak_submission_repeat_row` | `RepeatRowKey` | Stable text key for idempotent repeat-row projection upserts. |
| `SubmissionAnswers` | `ak_submission_answer` | `AnswerKey` | Stable text key for idempotent long-answer projection upserts, including root answers without a repeat lookup. |
| `ExportSettings` | `ak_export_setting` | `ExportKey` | Stable named export configuration. |

## Import Position

Create this schema after the ODK Central-inspired MVP schema exists:

1. `Projects`
2. `Forms`
3. `FormVersions`
4. `Submissions`
5. `SubmissionVersions`
6. reporting projection tables in this file
7. reporting table permissions and Power Pages Web API settings after approval

## Verification Before Environment Write

- Run `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/reporting-projection-schema.json`.
- Confirm the plan is additive only.
- Confirm alternate keys do not exceed target Dataverse constraints.
- Confirm Power BI users will receive read access to reporting tables, not canonical XML payload tables by default.
- Confirm export generation mechanism before creating export-related automation.
