# TACATDP Reporting Projection Plug-in

This package contains the asynchronous Dataverse plug-in that refreshes derived reporting rows when an `mp_submissionversion` row is created.

The package does not register itself. Review `registration-contract.json`, configure the dedicated least-privilege execution user in the target environment, register the documented asynchronous PostOperation step and post image, and add the assembly/type/step/image to `tacatdp_prototype` through normal solution ALM.

Do not run the step as the Power Pages caller. Do not include source-environment user identifiers or credentials in the package.
