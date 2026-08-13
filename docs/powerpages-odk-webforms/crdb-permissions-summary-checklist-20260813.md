# CRDB permissions summary checklist

Date: 2026-08-13

## Current access status

| Item | Status |
|---|---|
| CRDB environment | `TACATDP-CRDB-Dev` |
| Environment URL | `https://org5eb0379b.crm4.dynamics.com/` |
| PAC profile | `tacatdp-crdb` |
| PAC user | `dmuroba@CRDBBANK.CO.TZ` |
| Power Pages site | `TACATDP Monitoring Tool` |
| Website ID | `fccc0cc6-7f5e-4885-aeb8-2272e68130a3` |
| Verification | `pac pages list` now succeeds after Denis device-code login |

Note: PAC authentication succeeded, then PAC crashed once during connection validation with `System.ArgumentOutOfRangeException`, but the profile was saved and subsequent `pac pages list` succeeded.

## Permissions to enable or confirm

- [ ] **Azure CLI access**
  - Allow Denis/deployment user to sign in to the CRDB tenant from Azure CLI where needed.
  - Needed for environment/session checks and future automation support.

- [ ] **PAC CLI access**
  - Keep `dmuroba@CRDBBANK.CO.TZ` or another approved deployment user able to authenticate to `TACATDP-CRDB-Dev`.
  - Needed for `pac auth who`, `pac pages list`, Power Pages download/upload, and deployment checks.

- [ ] **Stable deployment identity**
  - Provide a CRDB-approved service principal, application user, or dedicated deployment account for development deployments.
  - Needed because personal/device-code login is affected by Conditional Access token expiry.

- [ ] **Dataverse environment role**
  - Assign `System Administrator` to the named CRDB platform owner/admin.
  - Assign `System Customizer` or maker permission to approved delivery makers if they are expected to configure solutions.

- [ ] **Power Pages site admin**
  - Give the approved site admin permission to manage the CRDB development Power Pages site.
  - Needed for site upload, cache purge/restart, site settings, site visibility, web roles, page permissions, table permissions, and Web API settings.

- [ ] **Power Pages site visibility**
  - If the site is private, grant visibility access to Denis, Hailo, SFU reviewers, and delivery testers.
  - Needed to avoid “sign-in successful but no access” before app roles are evaluated.

- [ ] **Power Pages Contact and external identity**
  - Confirm Denis and Hailo have Contact records and external identity records after sign-in.
  - Needed because Microsoft sign-in alone does not grant portal access.

- [ ] **Power Pages web roles**
  - Assign Denis and Hailo to `Platform Administrator` or the agreed admin/reviewer role.
  - Needed for admin routes such as User & Access and full prototype review.

- [ ] **Power Pages page permissions**
  - Enable page access for dashboard, projects/forms, saved records, beneficiaries, reporting, and user/access routes.
  - Needed for SFU and admin review.

- [ ] **Power Pages table permissions**
  - Enable required table permissions for project, form, form version, assignment, submission, reporting, beneficiary, contact/access, and audit tables.
  - Needed for portal data reads/writes.

- [ ] **Power Pages Web API settings**
  - Enable Web API site settings for only the required development tables and fields.
  - Needed because the SPA uses Power Pages `/_api`.

- [ ] **Hailo active assignment**
  - Confirm Hailo has an active TACATDP form assignment.
  - Needed because a prior CRDB issue showed Hailo had role access but could not see projects/forms due to assignment lifecycle.

- [ ] **Shared sender mailbox**
  - Approve/configure a CRDB shared mailbox, for example `noreply@crdbbank.co.tz`.
  - Requires Global Administrator, Exchange Administrator, or Delegated Mailbox Approver.
  - Needed for invitations and assignment notifications.

- [ ] **Power Automate owner/connections**
  - Assign a CRDB-owned flow owner or service account for onboarding, invitations, notifications, and access workflows.
  - Needed to avoid flows depending on personal user tokens.

- [ ] **DLP connector allowance**
  - Confirm required development connectors are allowed: Dataverse, Power Pages, Power Automate, Power BI/Fabric, SharePoint/OneDrive, GitHub or Azure DevOps if used, and approved Azure services.
  - Needed so app, flow, reporting, and CI/CD work are not blocked by policy.

- [ ] **GitHub repository access**
  - Grant approved CRDB users or deployment identity access to `https://github.com/mdudaj/crdb-mel.git`, or move/fork under a CRDB-approved organization.
  - Needed for code review and continuous deployment.

- [ ] **GitHub Actions / CI-CD permission**
  - Allow workflow setup and repository secrets/variables if GitHub Actions will deploy to CRDB development.
  - Alternative: confirm Azure DevOps or Power Platform pipelines instead.

- [ ] **Power BI/Fabric workspace access**
  - If SFU needs reporting review now, create or assign a development Power BI/Fabric workspace and viewer access.

- [ ] **Managed Power Pages component cleanup authority**
  - Confirm who can manage/repair managed duplicate Power Pages web-file components.
  - Needed because CRDB has managed duplicate web files that should not be deleted ad hoc.

## Do not share

Do not send passwords, client secrets, API keys, connection strings, bearer tokens, private keys, or `.env` contents.
