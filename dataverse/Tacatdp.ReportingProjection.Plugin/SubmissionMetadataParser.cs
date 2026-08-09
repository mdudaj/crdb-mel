using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Text;

namespace Tacatdp.ReportingProjection.Plugin
{
    [DataContract]
    internal sealed class SubmissionMetadataPayload
    {
        [DataMember(Name = "formVersionId")]
        public string FormVersionId { get; set; }

        [DataMember(Name = "xmlFormId")]
        public string XmlFormId { get; set; }

        [DataMember(Name = "instanceName")]
        public string InstanceName { get; set; }

        [DataMember(Name = "repeatPaths")]
        public string[] RepeatPaths { get; set; }
    }

    internal sealed class SubmissionMetadata
    {
        public SubmissionMetadata()
        {
            RepeatPaths = new HashSet<string>(StringComparer.Ordinal);
        }

        public Guid? FormVersionId { get; set; }
        public string XmlFormId { get; set; }
        public string InstanceName { get; set; }
        public ISet<string> RepeatPaths { get; }
    }

    internal static class SubmissionMetadataParser
    {
        public static SubmissionMetadata Parse(string json)
        {
            var result = new SubmissionMetadata();
            if (string.IsNullOrWhiteSpace(json))
            {
                return result;
            }

            try
            {
                var serializer = new DataContractJsonSerializer(typeof(SubmissionMetadataPayload));
                SubmissionMetadataPayload payload;
                using (var stream = new MemoryStream(Encoding.UTF8.GetBytes(json)))
                {
                    payload = (SubmissionMetadataPayload)serializer.ReadObject(stream);
                }
                if (payload == null)
                {
                    return result;
                }

                Guid formVersionId;
                if (Guid.TryParse(payload.FormVersionId, out formVersionId))
                {
                    result.FormVersionId = formVersionId;
                }
                result.XmlFormId = payload.XmlFormId;
                result.InstanceName = payload.InstanceName;
                foreach (var path in payload.RepeatPaths ?? Array.Empty<string>())
                {
                    if (!string.IsNullOrWhiteSpace(path) && path.StartsWith("/", StringComparison.Ordinal))
                    {
                        result.RepeatPaths.Add(path);
                    }
                }
            }
            catch (SerializationException)
            {
                // Metadata is optional; canonical XML remains the projection source.
            }
            catch (InvalidCastException)
            {
                // Metadata is optional; canonical XML remains the projection source.
            }

            return result;
        }
    }
}
