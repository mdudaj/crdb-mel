# Report with all system stages details

Date: 2026-08-27

System: TACATDP Integrated M&E System and Monitoring Tool

## 1. Executive summary

The current prototype demonstrates a Microsoft-hosted monitoring, evaluation, and reporting workflow for TACATDP. It includes an authenticated Power Pages portal, Dataverse-backed form and submission storage, a baseline import workflow, a beneficiary registry view, dashboard visualisation, reporting/export pathways, and role-based administration screens.

The cleaned TACATDP baseline dataset has been successfully imported through the prototype import workflow. The CRDB development environment has also been updated with the latest working portal build. The remaining CRDB-side activities are operational: seed or confirm the latest form version, import the cleaned baseline dataset through the portal, and verify CRDB permissions for the relevant user roles.

An important change was received from CRDB ICT on Tuesday: ICT is recommending a CRDB-hosted deployment strategy instead of continuing with the Microsoft Power Pages and Dataverse environment. That change affects the future production architecture. A rebuild has already started around the proposed CRDB-hosted strategy so that a working system can be ready when CRDB’s environment is available.

## 2. Development stages completed

| Stage | Status | Details |
|---|---|---|
| Requirements discovery | Completed for prototype; revised for future deployment | TACATDP was treated as the first programme configuration for a broader MEL capability. |
| Prototype architecture | Completed | Power Pages hosts the app shell and authentication. Dataverse stores forms, submissions, baseline projections, beneficiary profiles, and configuration records. |
| Application shell | Completed | CRDB-branded navigation, top bar, content area, route separation, and footer are implemented. |
| Form runtime | Completed for prototype | The tool uses an XForms/web forms runtime to render the TACATDP form from a stored form version. |
| Latest form version | Implemented | Version `2608130924` is the expected active form version for baseline import and future data updates. |
| Baseline import | Completed for prototype | Cleaned baseline data was imported through the portal import workflow. The same import path is available in CRDB subject to user permissions. |
| Beneficiary registry | Implemented for prototype | Imported baseline data is projected into beneficiary-facing records and detail views. |
| Dashboard visualisation | Implemented for prototype | Dashboard cards use live baseline projections where the imported data supports the metric. Unsupported metrics remain explicitly pending. |
| Reporting/export | Implemented for prototype | Reporting rows and export pathways exist for imported submissions and projected baseline data. |
| User and access management | Implemented for prototype | User, role, access, and assignment concepts are represented. Automation depends on CRDB permissions and ownership. |
| CRDB environment update | Completed | Latest working Power Pages build was deployed to the CRDB development environment. |
| Production hardening | Pending | Depends on final deployment strategy, CRDB infrastructure, security review, and integration permissions. |

## 3. Current environment state

### Prototype baseline validation

The cleaned baseline data has been imported through the portal workflow and used to validate dashboard, beneficiary, reporting, and import behavior.

### CRDB development environment

The CRDB development environment has been updated with the latest tested Power Pages build.

Known CRDB environment details:

| Item | Value |
|---|---|
| Environment | `TACATDP-CRDB-Dev` |
| Environment URL | `https://org5eb0379b.crm4.dynamics.com/` |
| Portal URL | `https://tacatdp-crdb.powerappsportals.com/` |
| Website | `TACATDP Monitoring Tool` |
| Website ID | `fccc0cc6-7f5e-4885-aeb8-2272e68130a3` |
| Current form version | `2608130924` |

## 4. Baseline data status

The cleaned baseline dataset was prepared from the shared TACATDP DAP dataset folder.

Current cleaned-data profile:

| Item | Count |
|---|---:|
| Root beneficiary baseline rows | 1,246 |
| Loan/value-chain child rows | 1,484 |
| Value-chain cost rows | 7,585 |
| GPS rows | 1,246 |
| Regions | 29 |
| Districts | 130 |
| Wards | 415 |
| Total reported loan amount in baseline | TZS 51.6B |

The import treats each row as a form submission. This preserves the field-data lineage and keeps the platform ready for future follow-up data collection.

## 5. Dashboard status

The dashboard uses baseline-derived values only where the imported data supports the calculation.

| Dashboard area | Current data source | Status |
|---|---|---|
| Beneficiary count | Imported baseline registry/projection | Available after import |
| Report rows | Imported submission report rows | Available after import |
| Reported loan amount | Baseline `total_loan_amount` and loan repeat data | Available after import |
| Regional map | Baseline region and amount fields | Available after import |
| Financed technologies/practices | Baseline technology fields and value-chain stage fallback | Available where source fields exist |
| Training metrics | Baseline training fields | Available where source fields exist |
| Climate outcome estimates | Baseline-supported calculations only | Available where source fields support a defensible calculation |
| Loan performance | Core banking/repayment feed | Pending |
| Monthly disbursement trend | Dated loan repeat records | Pending unless dated loan records are exposed to the dashboard projection |

The dashboard does not present unsupported figures as official values. If a feed is missing, the UI shows a pending or unavailable state.

## 6. User roles represented in the prototype

| Role | Prototype responsibility |
|---|---|
| Platform Administrator | Manage form version seed, baseline import, user/access setup, and environment checks. |
| M&E Manager | Review dashboard, reporting outputs, SOPs, and system readiness. |
| MEL Officer | Review dashboard, beneficiary records, submissions, and monitoring outputs. |
| Data Collector / Field Officer | Complete assigned TACATDP forms. |
| Reviewer / Approver | Review submitted data and verify reporting outputs. |
| ICT / System Administrator | Manage environment, permissions, deployment, hosting, and integration readiness. |

## 7. Known limitations

- The prototype is not yet a full production system.
- CRDB permissions still control whether CRDB users can import, read, or update all required records.
- Power BI plugin/report creation depends on CRDB Power BI permissions.
- Mailbox-based notifications depend on an approved sender mailbox and Power Automate ownership.
- The proposed CRDB-hosted deployment strategy requires architectural rework away from the current Microsoft Power Pages/Dataverse-specific implementation.

## 8. Deployment strategy change

CRDB ICT has recommended moving toward CRDB-hosted infrastructure instead of continuing only with Microsoft Power Pages and Dataverse. This changes the production direction.

Implications:

- Authentication, hosting, database, workflow automation, deployment, and reporting integration must be revised.
- The current prototype remains valuable as a functional proof and requirements reference.
- Future implementation should be rebuilt around the approved CRDB-hosted environment.
- The client should sign off system requirements and system design documents before major implementation work starts.

## 9. Immediate next actions

1. Capture final dashboard screenshots after CRDB baseline import verification.
2. Seed or confirm latest form version `2608130924` in the CRDB environment.
3. Import the cleaned baseline dataset into the CRDB environment.
4. Verify CRDB user permissions for baseline import, dashboard read, beneficiary read, and reporting read.
5. Deliver the documentation pack and annexes.
6. Continue rebuilding the future system around the CRDB-hosted deployment strategy.
