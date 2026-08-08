# Agent Instructions

This repository is the Sustainable Finance MEL Platform project.

## Project Identity

- Project ID: `crdb-mel`
- Product name: Sustainable Finance MEL Platform
- Proof-of-concept use case: TACATDP monitoring
- Historical/source workstream name: TACATDP
- Repository: `mdudaj/crdb-mel`

Use `Sustainable Finance MEL Platform` for the current product/system name, documentation pack, and future product vision. Keep `TACATDP` where it refers to the original programme, existing XLSForm labels, deployed list/schema names, generated artifacts, or historical implementation context.

Do not blindly replace every `TACATDP` reference. Many existing Microsoft Lists, files, controls, form labels, and generated schemas intentionally use `TACATDP_*`.

Position TACATDP monitoring as a proof of concept, not the full product boundary. The platform is intended to support multiple Sustainable Finance Unit programmes/projects and operational impact use cases.

## Current Prototype Scope

The current prototype supports beneficiary baseline data collection through a deployed Power Pages/Power Platform form. The documentation and next prototype revisions should position it as:

- baseline data collection from beneficiaries;
- beneficiary-linked monitoring records;
- a lightweight beneficiary entity model suitable for prototype tracking;
- direct portal KPI visualisation for demonstration and monitoring where Power BI access is not yet available.

## Future Product Scope

If the prototype is accepted, the target product should be documented as a more scalable and robust Sustainable Finance MEL Platform. Future-product scope may include:

- centrally governed beneficiary master data;
- configurable programme/project templates;
- stronger role-based access control and audit trails;
- Power BI or semantic-model analytics;
- integration with enterprise CRDB systems where approved;
- production-grade data governance, backup, monitoring, and support.

Future use cases should be described broadly as Sustainable Finance Unit programmes, projects, facilities, operational processes, resources, activities, indicators, evidence, and institutional impact initiatives. Do not list sensitive or speculative example initiatives unless the user explicitly asks for them in the final submission text.

Keep prototype claims separate from future-product claims.

## Documentation Gate

Before implementation work, create or update documentation artifacts under `docs/submission/`.

Required submission artifacts:

- documentation plan and scope;
- prototype overview and scope;
- requirements specification;
- current architecture;
- user manual;
- testing and validation report;
- deployment/admin guide;
- known limitations;
- future product vision and roadmap;
- traceability matrix.

## Power Platform Rules

- Use Power Platform CLI (`pac`) for environment/site inspection when possible.
- Prefer Maker Portal environment IDs over guessed Dataverse organization URLs when PAC auth or site listing fails.
- Do not assume Azure service principal or managed identity auth unless explicitly approved and verified.
- For CRDB environment deployment, historical workflow used device-code auth with the delegated `dmuroba@crdb.co.tz` profile; do not treat that as a service principal.
- For Mshirika, use the tenant account and environment context confirmed during deployment checks.

## Safety Rules

- Do not deploy without explicit approval.
- Do not print secrets, tokens, `.env` contents, authorization headers, or private key material.
- Do not modify production data without explicit approval.
- Do not rename deployed Power Platform tables/lists/forms unless the migration impact is reviewed.
- Prefer documentation and reviewable branches before production changes.

## Recommended Verification

- `git status -sb`
- Review changed documentation for prototype/future-product separation.
- Validate any generated schema or app artifacts with existing project scripts before deployment.
- Verify live portal state with PAC before claiming deployed behavior.
