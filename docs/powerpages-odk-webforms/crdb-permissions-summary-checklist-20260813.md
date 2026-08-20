# CRDB environment permissions checklist

Date: 2026-08-13

Purpose: simple administrator checklist for enabling smooth development, review, and deployment for the CRDB MEL prototype environment.

## Current environment

| Item | Current value |
|---|---|
| Environment | `TACATDP-CRDB-Dev` |
| Environment URL | `https://org5eb0379b.crm4.dynamics.com/` |
| PAC profile | `tacatdp-crdb` |
| Current PAC user | `dmuroba@CRDBBANK.CO.TZ` |
| Current user display name | Denis Muroba |
| Power Pages site | `TACATDP Monitoring Tool` |
| Website ID | `fccc0cc6-7f5e-4885-aeb8-2272e68130a3` |

## Current verified access for Denis

| Capability | Status | Evidence |
|---|---|---|
| PAC authentication | Enabled | `pac auth who` returns Denis in `TACATDP-CRDB-Dev`. |
| Power Pages site visibility | Enabled | `pac pages list` returns `TACATDP Monitoring Tool`. |
| Solution visibility | Enabled | `pac solution list` returns CRDB environment solutions including `tacatdp_prototype` and `TACATDPMonitoringTool`. |
| Dataverse user account | Enabled | Dataverse `systemuser` record is active for `dmuroba@CRDBBANK.CO.TZ`. |
| Dataverse roles | Enabled | Denis has `Basic User` and `System Administrator`. |
| Power Pages contact | Enabled | Contact record for Denis is active. |
| Power Pages web role | Enabled | Denis has `Platform Administrator Web Role`. |
| TACATDP assignment | Enabled | Denis has an active form assignment record. |
| Azure CLI | Installed, login not verified | `az --version` returns Azure CLI `2.89.1`; `az account show` returns `Please run 'az login' to setup account.` |
| Git/GitHub access | Not verified from tenant | Repository access and CI/CD permissions are outside PAC/Dataverse and must be confirmed separately. |

## Permissions to enable or confirm

- [ ] **Git/GitHub access**
  - Grant Denis, Hailo, or the agreed CRDB development identity access to the repository: `https://github.com/mdudaj/crdb-mel.git`.
  - Allow pull, push, branch creation, and pull request review for approved developers.
  - If CRDB policy disallows this GitHub location, move or mirror the repository under a CRDB-approved GitHub organization or Azure DevOps project.

- [ ] **Continuous deployment permission**
  - Approve the deployment route: GitHub Actions, Azure DevOps, or Power Platform pipelines.
  - Allow the selected runner to use PAC CLI or Power Platform Build Tools.
  - Allow repository/environment secrets or secure variables for deployment configuration.

- [ ] **Stable deployment identity**
  - Provide a CRDB-owned deployment account, service principal, or approved application user.
  - Avoid depending only on personal device-code sessions because Conditional Access and token expiry can interrupt deployments.

- [ ] **Azure CLI tenant login**
  - Azure CLI is now installed locally.
  - Confirm Denis or the agreed CRDB development identity can sign in with `az login` and access the required CRDB tenant/subscription scope if Azure checks or Azure-backed automation are required.
  - Current local finding: `az account show` reports no Azure account is logged in.

- [ ] **PAC CLI / Power Platform access**
  - Keep Denis and the deployment identity able to authenticate to `TACATDP-CRDB-Dev`.
  - Required for Power Pages listing, upload/download, solution checks, and deployment diagnostics.

- [ ] **Power Pages site administration**
  - Keep Denis or the CRDB platform owner as Power Pages site admin.
  - Required for uploads, cache purge/restart, site settings, page permissions, web roles, table permissions, and Web API settings.

- [ ] **Power Pages reviewer access**
  - Confirm Hailo and SFU reviewers can sign in to the portal and view the prototype.
  - Ensure each reviewer has the required Contact record, web role, page permissions, and active assignment where applicable.

- [ ] **Power Pages table permissions and Web API settings**
  - Confirm table permissions and Web API site settings are enabled for the prototype tables used by the SPA.
  - Required for forms, submissions, beneficiaries, users/access, projects, reports, and dashboard data.

- [ ] **Shared sender mailbox**
  - Approve and configure a CRDB mailbox for system messages, for example `noreply@crdbbank.co.tz`.
  - Requires the appropriate Exchange/Microsoft 365 administrator approval.
  - Required for invitations, assignment notifications, and workflow messages.

- [ ] **Power Automate ownership and connections**
  - Assign flows to a CRDB-owned owner or service account.
  - Avoid personal user tokens for onboarding, notifications, assignment, and access workflows.

- [ ] **DLP connector allowance**
  - Confirm the environment policy allows the connectors needed for development:
    - Dataverse
    - Power Pages
    - Power Automate
    - Power BI/Fabric, if reporting review is required
    - SharePoint/OneDrive, if document or export storage is required
    - GitHub or Azure DevOps, depending on the approved CI/CD route

- [ ] **Managed Power Pages component cleanup authority**
  - Confirm who is allowed to repair or clean managed duplicate Power Pages web-file components.
  - Do not delete managed components ad hoc.

## Minimum admin action list

For immediate smooth development and SFU review, enable or confirm these first:

1. Git/GitHub or Azure DevOps access for the approved development identity.
2. CI/CD runner permission and secure variables/secrets storage.
3. Stable deployment identity for PAC/Power Platform deployments.
4. Hailo and SFU reviewer portal access.
5. Shared sender mailbox for invitations and notifications.
6. Power Automate service ownership.
7. DLP allowance for the selected Microsoft development and deployment path.

## Do not share

Do not send passwords, client secrets, API keys, connection strings, bearer tokens, private keys, or `.env` contents.
