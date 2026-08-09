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

        internal const string FormVersion = "20260714000200000";
        internal const string XFormFileName = "tacatdp_impact_evaluation-20260714000200000.xml";
        internal const string XFormSha256 = "12b955fcf42330dbfb8051cbd6d5130a6c0128d78825d7e7b899c901a17f4c28";
    }
}
