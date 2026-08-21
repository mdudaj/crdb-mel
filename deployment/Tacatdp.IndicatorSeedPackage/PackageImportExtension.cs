using System;
using System.ComponentModel.Composition;
using System.Diagnostics;
using System.IO;
using Microsoft.Xrm.Tooling.PackageDeployment.CrmPackageExtentionBase;

namespace Tacatdp.IndicatorSeedPackage
{
    [Export(typeof(IImportExtensions))]
    public class PackageImportExtension : ImportExtension
    {
        public override string GetImportPackageDataFolderName => "PkgAssets";

        public override string GetNameOfImport(bool plural) => plural ? "TACATDP indicator seed packages" : "TACATDP indicator seed package";

        public override string GetLongNameOfImport => "TACATDP Indicator Definition Seed 1.0.0";

        public override string GetImportPackageDescriptionText =>
            "Idempotently seeds TACATDP indicator definitions and data-source mappings only.";

        public override void InitializeCustomExtension()
        {
        }

        public override bool BeforeImportStage()
        {
            return true;
        }

        public override bool AfterPrimaryImport()
        {
            if (CrmSvc == null || !CrmSvc.IsReady)
            {
                throw new InvalidOperationException("The Package Deployer Dataverse connection is not ready.");
            }

            var packageRoot = Path.GetDirectoryName(typeof(PackageImportExtension).Assembly.Location);
            if (string.IsNullOrWhiteSpace(packageRoot))
            {
                throw new InvalidOperationException("Unable to resolve the extracted indicator seed package directory.");
            }

            var seedPath = Path.Combine(packageRoot, "PkgAssets", "Content", IndicatorSeedDeployer.SeedFileName);
            Trace.TraceInformation("TACATDP indicator seed started.");
            new IndicatorSeedDeployer(CrmSvc).Deploy(seedPath);
            Trace.TraceInformation("TACATDP indicator seed completed.");
            return true;
        }
    }
}
