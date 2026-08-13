using System;

namespace Tacatdp.DeploymentPackage
{
    internal static class SeedManifest
    {
        internal static readonly Guid ProjectId = new Guid("1bb217ce-b07b-f111-ab0e-7c1e523612eb");
        internal static readonly Guid FormId = new Guid("896d52d5-b07b-f111-ab0e-7c1e523612eb");
        internal static readonly Guid FormVersionId = new Guid("0e024e5c-607f-f111-ab0e-7ced8d41fa2d");
        internal static readonly Guid FormAttachmentId = new Guid("11024e5c-607f-f111-ab0e-7ced8d41fa2d");

        internal static readonly Tuple<Guid, string>[] FormAssignments =
        {
            Tuple.Create(new Guid("5f36a0d7-6957-4508-9201-af99f1556d26"), "Denis.Muroba@crdbbank.co.tz"),
            Tuple.Create(new Guid("fd1f0397-b827-429d-90de-77434df37a49"), "Hailo.Kibiki@crdbbank.co.tz"),
            Tuple.Create(new Guid("b0266afc-0677-4992-9509-1e757ab0a759"), "hkibiki@crdbbank.co.tz")
        };

        internal const string FormVersion = "2608130924";
        internal const string XFormFileName = "tacatdp_impact_evaluation-2608130924.xml";
        internal const string XFormSha256 = "1fa53c3517f63dac748c777616c322a9be4da8b70b89e5e3a21a61d6619d8b51";
        internal const string BaselineBridgeFileName = "tacatdp-baseline-bridge-import.json";
    }
}
