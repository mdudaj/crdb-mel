using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml;
using System.Xml.Linq;

namespace Tacatdp.ReportingProjection.Plugin
{
    public static class ProjectionCore
    {
        private static readonly Regex NumericPattern = new Regex(@"^-?\d+(\.\d+)?$", RegexOptions.Compiled);
        private static readonly Regex DatePattern = new Regex(@"^\d{4}-\d{2}-\d{2}(t.*)?$", RegexOptions.Compiled | RegexOptions.IgnoreCase);
        private static readonly Regex WhitespacePattern = new Regex(@"\s+", RegexOptions.Compiled);
        private static readonly Regex InvalidKeyPattern = new Regex(@"[^0-9A-Za-z_.:-]+", RegexOptions.Compiled);

        public static ProjectionResult Build(ProjectionSource source, DateTime projectedAt)
        {
            if (source == null)
            {
                throw new ArgumentNullException(nameof(source));
            }

            var instanceId = source.InstanceId ?? string.Empty;
            var formKey = source.FormVersionId.HasValue
                ? source.FormVersionId.Value.ToString("D")
                : source.XmlFormId ?? "unknown_form";
            var reportKey = SanitizeKeyPart(formKey) + ":" + SanitizeKeyPart(instanceId);
            var report = new ReportProjection
            {
                ReportKey = reportKey,
                InstanceId = instanceId,
                DisplayName = string.IsNullOrWhiteSpace(source.InstanceName) ? instanceId : source.InstanceName,
                UserEmail = source.UserEmail,
                SubmittedAt = source.SubmittedAt,
                UpdatedAt = source.UpdatedAt,
                VersionNumber = source.VersionNumber <= 0 ? 1 : source.VersionNumber,
                LifecycleStatus = source.LifecycleStatus == 0 ? ProjectionStatuses.LifecycleSubmitted : source.LifecycleStatus,
                ReviewState = source.ReviewState == 0 ? ProjectionStatuses.ReviewReceived : source.ReviewState,
                ProjectionStatus = ProjectionStatuses.Ready,
                ProjectedAt = projectedAt,
                RootAnswersJson = "{}",
                SubmissionId = source.SubmissionId,
                SubmissionVersionId = source.SubmissionVersionId,
                FormVersionId = source.FormVersionId,
            };
            var result = new ProjectionResult(report);

            XDocument document;
            try
            {
                document = XDocument.Parse(source.SubmissionXml ?? string.Empty, LoadOptions.None);
            }
            catch (XmlException)
            {
                report.ProjectionStatus = ProjectionStatuses.Failed;
                report.ProjectionError = "Malformed XForm submission XML.";
                return result;
            }

            if (document.Root == null)
            {
                report.ProjectionStatus = ProjectionStatuses.Failed;
                report.ProjectionError = "XForm submission XML has no root element.";
                return result;
            }

            var rootAnswers = new SortedDictionary<string, string>(StringComparer.Ordinal);
            var repeatAnswers = new Dictionary<string, SortedDictionary<string, string>>(StringComparer.Ordinal);
            var repeatsByKey = new Dictionary<string, RepeatProjection>(StringComparer.Ordinal);
            var rootPath = new List<string> { document.Root.Name.LocalName };
            VisitChildren(document.Root, rootPath, null, reportKey, projectedAt, source.SubmissionVersionId, source.RepeatPaths, result, rootAnswers, repeatAnswers, repeatsByKey);

            foreach (var repeat in result.RepeatRows)
            {
                repeat.AnswersJson = SerializeMap(repeatAnswers[repeat.RepeatRowKey]);
            }

            report.RootAnswersJson = SerializeMap(rootAnswers);
            return result;
        }

        public static bool ShouldProcess(Guid triggerVersionId, Guid latestVersionId)
        {
            return triggerVersionId != Guid.Empty && triggerVersionId == latestVersionId;
        }

        public static ISet<string> FindObsolete(IEnumerable<string> existingKeys, IEnumerable<string> expectedKeys)
        {
            var expected = new HashSet<string>(expectedKeys ?? Enumerable.Empty<string>(), StringComparer.Ordinal);
            return new HashSet<string>((existingKeys ?? Enumerable.Empty<string>()).Where(key => !expected.Contains(key)), StringComparer.Ordinal);
        }

        public static string SanitizeKeyPart(object value)
        {
            var text = Convert.ToString(value, CultureInfo.InvariantCulture) ?? string.Empty;
            text = WhitespacePattern.Replace(text.Trim(), "_");
            text = InvalidKeyPattern.Replace(text, "_").Trim('_');
            return text.Length == 0 ? "blank" : text;
        }

        private static void VisitChildren(
            XElement parent,
            IList<string> path,
            string currentRepeatKey,
            string reportKey,
            DateTime projectedAt,
            Guid submissionVersionId,
            ISet<string> knownRepeatPaths,
            ProjectionResult result,
            SortedDictionary<string, string> rootAnswers,
            IDictionary<string, SortedDictionary<string, string>> repeatAnswers,
            IDictionary<string, RepeatProjection> repeatsByKey)
        {
            var children = parent.Elements().ToList();
            var counts = children.GroupBy(child => child.Name.LocalName).ToDictionary(group => group.Key, group => group.Count(), StringComparer.Ordinal);
            var seen = new Dictionary<string, int>(StringComparer.Ordinal);

            foreach (var child in children)
            {
                var name = child.Name.LocalName;
                var childPath = path.Concat(new[] { name }).ToList();
                if (!child.Elements().Any())
                {
                    var text = (child.Value ?? string.Empty).Trim();
                    if (text.Length > 0)
                    {
                        AddAnswer("/" + string.Join("/", childPath), text, currentRepeatKey, reportKey, projectedAt, submissionVersionId, result, rootAnswers, repeatAnswers);
                    }
                    continue;
                }

                seen[name] = seen.ContainsKey(name) ? seen[name] + 1 : 1;
                var repeatPath = "/" + string.Join("/", childPath);
                if (counts[name] > 1 || (knownRepeatPaths != null && knownRepeatPaths.Contains(repeatPath)))
                {
                    var rowIndex = seen[name] - 1;
                    var repeatKey = string.Join(":", new[]
                    {
                        SanitizeKeyPart(reportKey),
                        SanitizeKeyPart(repeatPath),
                        SanitizeKeyPart(currentRepeatKey ?? "root"),
                        SanitizeKeyPart(rowIndex),
                    });
                    var repeat = new RepeatProjection
                    {
                        RepeatRowKey = repeatKey,
                        InstanceId = result.Report.InstanceId,
                        RepeatPath = repeatPath,
                        ParentPath = path.Count == 0 ? "/" : "/" + string.Join("/", path),
                        ParentRepeatRowKey = currentRepeatKey,
                        RowIndex = rowIndex,
                        ProjectedAt = projectedAt,
                        SubmissionVersionId = submissionVersionId,
                    };
                    result.RepeatRows.Add(repeat);
                    repeatsByKey[repeatKey] = repeat;
                    repeatAnswers[repeatKey] = new SortedDictionary<string, string>(StringComparer.Ordinal);
                    VisitChildren(child, childPath, repeatKey, reportKey, projectedAt, submissionVersionId, knownRepeatPaths, result, rootAnswers, repeatAnswers, repeatsByKey);
                }
                else
                {
                    VisitChildren(child, childPath, currentRepeatKey, reportKey, projectedAt, submissionVersionId, knownRepeatPaths, result, rootAnswers, repeatAnswers, repeatsByKey);
                }
            }
        }

        private static void AddAnswer(
            string fieldPath,
            string text,
            string repeatRowKey,
            string reportKey,
            DateTime projectedAt,
            Guid submissionVersionId,
            ProjectionResult result,
            IDictionary<string, string> rootAnswers,
            IDictionary<string, SortedDictionary<string, string>> repeatAnswers)
        {
            if (repeatRowKey == null)
            {
                rootAnswers[fieldPath] = text;
            }
            else
            {
                repeatAnswers[repeatRowKey][fieldPath.TrimStart('/')] = text;
            }

            var answer = new AnswerProjection
            {
                AnswerKey = string.Join(":", new[]
                {
                    SanitizeKeyPart(reportKey),
                    SanitizeKeyPart(repeatRowKey ?? "root"),
                    SanitizeKeyPart(fieldPath),
                }),
                RepeatRowKey = repeatRowKey,
                InstanceId = result.Report.InstanceId,
                FieldPath = fieldPath,
                FieldName = fieldPath.Substring(fieldPath.LastIndexOf('/') + 1),
                ValueText = text,
                ProjectedAt = projectedAt,
                SubmissionVersionId = submissionVersionId,
            };
            CoerceValue(answer);
            result.AnswerRows.Add(answer);
        }

        private static void CoerceValue(AnswerProjection answer)
        {
            var text = answer.ValueText;
            bool boolean;
            if (bool.TryParse(text, out boolean))
            {
                answer.ValueBoolean = boolean;
            }

            decimal number;
            if (NumericPattern.IsMatch(text) && decimal.TryParse(text, NumberStyles.Number, CultureInfo.InvariantCulture, out number))
            {
                answer.ValueDecimal = number;
            }

            DateTime date;
            if (DatePattern.IsMatch(text) && DateTime.TryParse(text, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out date))
            {
                answer.ValueDate = date.Kind == DateTimeKind.Unspecified ? DateTime.SpecifyKind(date, DateTimeKind.Utc) : date.ToUniversalTime();
            }

            if (text.StartsWith("{", StringComparison.Ordinal) || text.StartsWith("[", StringComparison.Ordinal))
            {
                answer.ValueJson = text;
            }
        }

        private static string SerializeMap(IEnumerable<KeyValuePair<string, string>> values)
        {
            return "{" + string.Join(", ", values.Select(pair => Quote(pair.Key) + ": " + Quote(pair.Value))) + "}";
        }

        private static string Quote(string value)
        {
            var result = new StringBuilder("\"");
            foreach (var character in value ?? string.Empty)
            {
                switch (character)
                {
                    case '\"': result.Append("\\\""); break;
                    case '\\': result.Append("\\\\"); break;
                    case '\b': result.Append("\\b"); break;
                    case '\f': result.Append("\\f"); break;
                    case '\n': result.Append("\\n"); break;
                    case '\r': result.Append("\\r"); break;
                    case '\t': result.Append("\\t"); break;
                    default:
                        if (character < 0x20 || character > 0x7e)
                        {
                            result.Append("\\u").Append(((int)character).ToString("x4", CultureInfo.InvariantCulture));
                        }
                        else
                        {
                            result.Append(character);
                        }
                        break;
                }
            }
            return result.Append('"').ToString();
        }
    }
}
