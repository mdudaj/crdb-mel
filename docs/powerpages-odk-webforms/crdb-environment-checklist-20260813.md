# CRDB environment checklist

Date: 2026-08-13

## Purpose

Simple checklist of the current missing permissions and access items needed to make CRDB development easier, especially for Denis Muroba and Hailo Kibiki, and to prepare for future continuous deployment from GitHub.

This is a checklist only. It does not change permissions, deploy code, create users, or create service principals.

## Current CRDB environment

| Item | Current value |
|---|---|
| Power Platform environment | `TACATDP-CRDB-Dev` |
| Environment URL | `https://org5eb0379b.crm4.dynamics.com/` |
| PAC profile | `tacatdp-crdb` |
| Current PAC user/profile | `dmuroba@CRDBBANK.CO.TZ` |
| Known SFU/CRDB reviewers | `Denis.Muroba@crdbbank.co.tz`, `Hailo.Kibiki@crdbbank.co.tz` |
| GitHub repository | `https://github.com/mdudaj/crdb-mel.git` |

## Current blocker found

The current CRDB PAC profile exists and is named `tacatdp-crdb`, but it cannot connect now because the delegated `dmuroba@CRDBBANK.CO.TZ` token expired under CRDB Conditional Access sign-in frequency.

Observed error on 2026-08-13:

```text
AADSTS70043: The refresh token has expired or is invalid due to sign-in frequency checks by conditional access.
```

This means daily/manual re-authentication may be required unless CRDB provides a stable deployment identity.

## Simple missing-permissions checklist

| Area | Missing / needed permission | Who needs it | Why it matters |
|---|---|---|---|
| CRDB PAC access | Refresh/recreate working PAC authentication for `TACATDP-CRDB-Dev`. | Denis Muroba profile or another approved CRDB deployment user. | We cannot reliably upload/check the CRDB Power Pages site when the token expires. |
| Stable deployment identity | CRDB-approved service principal/application user or approved deployment account for development deployments. | Delivery/deployment process. | Avoids depending on Denis/Hailo personal interactive tokens for continuous deployment. |
| GitHub repository access | Grant CRDB-approved deployment user/service account access to `mdudaj/crdb-mel` or move/fork repo under a CRDB-approved GitHub organization. | Denis/Hailo if they review code; deployment identity if CI/CD is used. | Required before GitHub-based continuous deployment can be configured. |
| GitHub Actions / CI permission | Allow repository workflow setup and secrets/variables configuration for development deployment. | Repo admin plus CRDB-approved deployment owner. | Needed to automate build, validation, packaging, and deployment to `TACATDP-CRDB-Dev`. |
| Power Platform environment maker/admin | Environment Maker/System Customizer or equivalent in `TACATDP-CRDB-Dev`. | Approved delivery maker/admin; possibly Denis/Hailo if they will administer. | Needed for solution import/export, configuration, schema review, and app updates. |
| Dataverse System Administrator | Dataverse `System Administrator` in `TACATDP-CRDB-Dev`. | Named CRDB platform owner/admin. | Needed to manage table permissions, roles, site settings, solution imports, diagnostics, and access fixes. |
| Power Pages site admin | Power Pages site owner/admin rights for the CRDB development site. | Named CRDB platform owner/admin and approved delivery admin if allowed. | Needed to update site content, purge/restart cache, manage site visibility, and configure security. |
| Power Pages site visibility | Grant site visibility access if the CRDB development site is private. | Denis, Hailo, SFU reviewers, delivery testers. | Prevents “sign-in successful but no access to this resource” before portal roles are evaluated. |
| Power Pages Contact/external identity | Confirm Contact and external identity records exist after sign-in/invitation. | Denis and Hailo. | Microsoft sign-in alone is not sufficient; the portal must link sign-in to the Contact. |
| Power Pages web role | Assign `Platform Administrator` or agreed reviewer/admin role. | Denis and Hailo. | Earlier evidence showed User & Access can be hidden when only `Authenticated Users` is present. |
| Page permissions | Enable page access for dashboard, projects/forms, saved records, beneficiaries, reporting, user/access, and admin review routes. | Denis and Hailo roles; SFU reviewer roles as needed. | Allows reviewers to see the full development prototype. |
| Table permissions | Enable required table permissions for project/form/form version/assignment/submission/reporting/access tables. | Denis/Hailo roles; reviewer/test collector roles. | Required for Power Pages `/_api` reads/writes and portal screens. |
| Power Pages Web API settings | Enable Web API site settings for required tables and fields. | Portal app roles/users through Power Pages security. | The SPA uses `/_api`; missing settings block reads/writes even when sign-in works. |
| Hailo assignment lifecycle | Ensure Hailo has an active form assignment row. | Hailo Kibiki. | Prior CRDB issue: Hailo had role access but could not see projects/forms because assignment lifecycle was missing/inactive. |
| Invitation/mailbox sending | Approve a CRDB shared sender mailbox such as `noreply@crdbbank.co.tz`. | CRDB Exchange/Global Admin or delegated mailbox approver. | Personal Denis/Hailo mailbox approval failed; governed invitations/notifications need an approved sender. |
| Flow owner / connectors | Assign CRDB-owned Power Automate connection owner/service identity for notifications and access workflows. | CRDB platform owner or service account. | Avoids flows breaking when personal users lose access or tokens expire. |
| DLP connector allowance | Confirm Dataverse, Power Pages, Power Automate, Power BI/Fabric, SharePoint/OneDrive, GitHub/Azure DevOps if used, and approved Azure connectors are allowed in development. | Power Platform admin/security owner. | CI/CD, reporting, notifications, and storage may fail if connectors are blocked. |
| Power BI/Fabric review access | Create or assign development reporting workspace if SFU needs reporting review now. | SFU reviewers, BI/report authors. | Enables continuous review of reporting direction without waiting for production. |
| Managed web-file cleanup authority | Confirm who can manage/repair duplicate managed Power Pages web-file components. | CRDB Power Platform admin/solution owner. | CRDB has managed duplicate web files that cannot be safely deleted ad hoc. |

## Minimum action list for Denis and Hailo

- [ ] Re-authenticate or recreate the CRDB PAC profile for `dmuroba@CRDBBANK.CO.TZ`, or provide another approved deployment user.
- [ ] Grant Denis and Hailo private-site visibility access if the CRDB Power Pages site is private.
- [ ] Confirm Denis and Hailo have active Power Pages Contact records.
- [ ] Confirm Denis and Hailo have external identity records after sign-in.
- [ ] Assign Denis and Hailo to `Platform Administrator` or the agreed admin/reviewer web role.
- [ ] Confirm Denis and Hailo can see User & Access where their role requires it.
- [ ] Confirm Hailo has an active TACATDP form assignment.
- [ ] Confirm Denis and Hailo can open dashboard, projects/forms, saved records, beneficiaries, reporting, and user/access routes.
- [ ] Confirm browser `/_api` read succeeds for their role.

## Minimum action list for continuous deployment

- [ ] Decide whether CI/CD will use GitHub Actions or a CRDB-approved Azure DevOps/Power Platform pipeline.
- [ ] Grant the deployment automation identity access to the repository or move the repository under a CRDB-approved organization.
- [ ] Create a CRDB-approved deployment identity for `TACATDP-CRDB-Dev`.
- [ ] Assign that identity least-privilege Dataverse/Power Pages permissions needed to import solutions and upload/update the development site.
- [ ] Store deployment configuration as approved CI/CD secrets or environment variables, not in source.
- [ ] Allow required connectors/pipeline permissions under CRDB DLP/security policy.
- [ ] Keep manual Denis/Hailo PAC login as fallback only, not as the main continuous deployment path.

## What CRDB should confirm back

- [ ] Which account should be used for CRDB development deployment now.
- [ ] Whether Denis profile remains the approved delegated deployment profile.
- [ ] Whether Hailo also needs maker/admin deployment access or reviewer-only access.
- [ ] Whether GitHub access is allowed for CRDB users/service identity.
- [ ] Whether CI/CD should be GitHub Actions, Azure DevOps, or Power Platform pipelines.
- [ ] Who can approve the shared mailbox for invitations/notifications.
- [ ] Who owns Power Pages table permissions, site visibility, and Web API settings.
- [ ] Who owns DLP connector approval for development.

## Evidence used

- `scripts/use-powerplatform-env.sh` records CRDB target `TACATDP-CRDB-Dev`, `https://org5eb0379b.crm4.dynamics.com/`, and PAC profile `tacatdp-crdb`.
- CRDB PAC check on 2026-08-13 confirmed `dmuroba@CRDBBANK.CO.TZ` profile exists but cannot connect because the refresh token expired under Conditional Access sign-in frequency.
- `powerpages-role-membership-investigation-20260728.md` documents Denis/Hailo Contacts, missing administrator web-role symptom, and mailbox approval blocker.
- `access-assignment-lifecycle-fix-20260804.md` documents Hailo's assignment lifecycle issue.
- `crdb-first-delivery-update-20260804.md` documents CRDB post-update checks for Denis/Hailo and private-site visibility for non-admin testers.
- `crdb-duplicate-webfile-ownership-classification-20260811.md` documents managed duplicate web-file cleanup constraints.
