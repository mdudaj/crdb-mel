# Reporting, Export, and Power BI Definition of Done

- Requirements, ADR, delivery plan, acceptance criteria, user stories, traceability, readiness, and verification artifacts are present.
- Reporting projection schema JSON and human-readable schema notes are present.
- Reporting schema dry-run includes tables, columns/lookups, relationships, and alternate keys without environment writes.
- Reporting schema changes are additive and reviewed before deployment.
- Reporting projection can be rebuilt from canonical submissions.
- Submit and edit paths refresh projections idempotently.
- Data UX is available to authenticated users and respects Dataverse permissions.
- CSV and XLSX downloads work for the agreed first form.
- Repeat groups are not silently dropped from XLSX exports.
- Power BI can connect to Dataverse reporting tables using an authorized organizational account.
- No secrets or raw Dataverse credentials are present in portal source.
- Automated source validation and build pass.
- Hosted browser smoke confirms Data, export, and Power BI instruction flows.
- Handoff records deployed environment, table names, verification commands, remaining risks, and exact next action.
