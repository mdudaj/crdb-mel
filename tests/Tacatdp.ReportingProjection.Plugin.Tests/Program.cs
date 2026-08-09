using System.Text.Json;
using Tacatdp.ReportingProjection.Plugin;

if (args.Length < 1 || args.Length > 2)
{
    throw new InvalidOperationException("Pass the shared reporting projection fixture path.");
}

var fixture = JsonSerializer.Deserialize<Fixture>(File.ReadAllText(args[0]), new JsonSerializerOptions
{
    PropertyNameCaseInsensitive = true,
}) ?? throw new InvalidOperationException("Fixture could not be parsed.");
var source = new ProjectionSource
{
    SubmissionId = fixture.SubmissionId,
    SubmissionVersionId = fixture.SubmissionVersionId,
    FormVersionId = fixture.FormVersionId,
    InstanceId = fixture.InstanceId,
    XmlFormId = fixture.XmlFormId,
    InstanceName = fixture.InstanceName,
    UserEmail = fixture.UserEmail,
    SubmittedAt = fixture.SubmittedAt,
    UpdatedAt = fixture.UpdatedAt,
    VersionNumber = fixture.VersionNumber,
    LifecycleStatus = fixture.LifecycleStatus,
    ReviewState = fixture.ReviewState,
    SubmissionXml = fixture.SubmissionXml,
    RepeatPaths = new HashSet<string>(fixture.RepeatPaths, StringComparer.Ordinal),
};
var projection = ProjectionCore.Build(source, fixture.ProjectedAt);
var metadata = SubmissionMetadataParser.Parse(JsonSerializer.Serialize(new
{
    formVersionId = fixture.FormVersionId,
    xmlFormId = fixture.XmlFormId,
    instanceName = fixture.InstanceName,
    repeatPaths = fixture.RepeatPaths,
}));

AssertEqual(fixture.Expected.ReportKey, projection.Report.ReportKey, "report key");
AssertEqual(fixture.Expected.RepeatCount, projection.RepeatRows.Count, "repeat count");
AssertEqual(fixture.Expected.AnswerCount, projection.AnswerRows.Count, "answer count");
AssertEqual(fixture.Expected.HouseholdRepeatCount, projection.RepeatRows.Count(row => row.RepeatPath == "/data/household"), "household repeat count");
AssertEqual(fixture.Expected.MemberRepeatCount, projection.RepeatRows.Count(row => row.RepeatPath == "/data/household/member"), "singleton/nested member repeat count");
AssertEqual(fixture.Expected.RootAnswerCount, projection.AnswerRows.Count(row => row.RepeatRowKey == null), "root answer count");
AssertEqual(fixture.FormVersionId, metadata.FormVersionId, "metadata form version");
Assert(metadata.RepeatPaths.SetEquals(fixture.RepeatPaths), "metadata repeat paths");
Assert(projection.AnswerRows.Single(row => row.FieldPath == "/data/active").ValueBoolean == true, "boolean coercion");
Assert(projection.AnswerRows.Single(row => row.FieldPath == "/data/amount").ValueDecimal == 12.50m, "decimal coercion");
Assert(projection.AnswerRows.Single(row => row.FieldPath == "/data/visit_date").ValueDate.HasValue, "date coercion");
Assert(projection.AnswerRows.Single(row => row.FieldPath == "/data/geo").ValueJson != null, "JSON coercion");
Assert(!projection.AnswerRows.Any(row => row.FieldPath == "/data/empty"), "empty values must not project");

var malformed = new ProjectionSource
{
    SubmissionId = fixture.SubmissionId,
    SubmissionVersionId = fixture.SubmissionVersionId,
    FormVersionId = fixture.FormVersionId,
    InstanceId = fixture.InstanceId,
    SubmissionXml = "<data><broken></data>",
};
var failed = ProjectionCore.Build(malformed, fixture.ProjectedAt);
Assert(failed.Failed, "malformed XML must produce Failed status");
AssertEqual("Malformed XForm submission XML.", failed.Report.ProjectionError, "sanitized parse error");
Assert(!failed.Report.ProjectionError.Contains("<data>", StringComparison.Ordinal), "parse error must not contain XML");

Assert(ProjectionCore.ShouldProcess(fixture.SubmissionVersionId, fixture.SubmissionVersionId), "current trigger should process");
Assert(!ProjectionCore.ShouldProcess(Guid.NewGuid(), fixture.SubmissionVersionId), "superseded trigger should no-op");
var obsolete = ProjectionCore.FindObsolete(new[] { "keep", "remove" }, new[] { "keep", "new" });
Assert(obsolete.SetEquals(new[] { "remove" }), "obsolete child reconciliation");

if (args.Length == 2 && args[1] == "--json")
{
    Console.WriteLine(JsonSerializer.Serialize(new
    {
        report = new
        {
            key = projection.Report.ReportKey,
            status = projection.Report.ProjectionStatus,
            rootAnswersJson = projection.Report.RootAnswersJson,
        },
        repeats = projection.RepeatRows.OrderBy(row => row.RepeatRowKey, StringComparer.Ordinal).Select(row => new
        {
            key = row.RepeatRowKey,
            path = row.RepeatPath,
            parentPath = row.ParentPath,
            parentKey = row.ParentRepeatRowKey,
            index = row.RowIndex,
            answersJson = row.AnswersJson,
        }),
        answers = projection.AnswerRows.OrderBy(row => row.AnswerKey, StringComparer.Ordinal).Select(row => new
        {
            key = row.AnswerKey,
            repeatKey = row.RepeatRowKey,
            path = row.FieldPath,
            valueText = row.ValueText,
            valueDecimal = row.ValueDecimal,
            valueDate = row.ValueDate?.ToString("yyyy-MM-dd"),
            valueBoolean = row.ValueBoolean,
            valueJson = row.ValueJson,
        }),
    }));
}
else
{
    Console.WriteLine("TACATDP reporting projection C# validation passed");
}

static void Assert(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException("Assertion failed: " + message);
    }
}

static void AssertEqual<T>(T expected, T actual, string message)
{
    if (!EqualityComparer<T>.Default.Equals(expected, actual))
    {
        throw new InvalidOperationException($"Assertion failed: {message}; expected={expected}; actual={actual}");
    }
}

internal sealed class Fixture
{
    public Guid SubmissionId { get; set; }
    public Guid SubmissionVersionId { get; set; }
    public Guid FormVersionId { get; set; }
    public string InstanceId { get; set; }
    public string XmlFormId { get; set; }
    public string InstanceName { get; set; }
    public string UserEmail { get; set; }
    public DateTime SubmittedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public int VersionNumber { get; set; }
    public int LifecycleStatus { get; set; }
    public int ReviewState { get; set; }
    public DateTime ProjectedAt { get; set; }
    public string[] RepeatPaths { get; set; }
    public string SubmissionXml { get; set; }
    public Expected Expected { get; set; }
}

internal sealed class Expected
{
    public string ReportKey { get; set; }
    public int RepeatCount { get; set; }
    public int AnswerCount { get; set; }
    public int RootAnswerCount { get; set; }
    public int HouseholdRepeatCount { get; set; }
    public int MemberRepeatCount { get; set; }
}
