# CRDB development environment admin checklist

Date: 2026-08-13

## Purpose

This is a short checklist for CRDB administrators to enable the Microsoft resources and permissions needed for the delivery team to continue building the Sustainable Finance MEL Platform and for the Sustainable Finance Unit to review it continuously.

This checklist is for the **development environment only**. It does not request production deployment or production data access.

## Current environment reference

The current working preview environment we have been using successfully is:

| Item | Current working value |
|---|---|
| Tenant/context | Mshirika development tenant |
| Power Platform environment | `PowerPagesDeveloper-070926-125720` |
| Environment URL | `https://orga3cf4b37.crm4.dynamics.com/` |
| Power Pages site | `TACATDP Monitoring Tool` |
| Website ID | `fccc0cc6-7f5e-4885-aeb8-2272e68130a3` |
| Working PAC profile | `tacatdp-mshirika` |

The CRDB development environment recorded for the target setup is:

| Item | CRDB development target |
|---|---|
| Tenant/context | CRDB Microsoft tenant |
| Power Platform environment | `TACATDP-CRDB-Dev` |
| Environment URL | `https://org5eb0379b.crm4.dynamics.com/` |
| Working PAC profile name | `tacatdp-crdb` |

The immediate request is to make the CRDB development environment work like the current Mshirika review environment: buildable by the delivery team and continuously reviewable by SFU users.

## Admin checklist

| App capability | Microsoft ecosystem resource | Enterprise MEL use | Permissions/resources to enable |
|---|---|---|---|
| Development workspace | Power Platform environment with Dataverse | Gives the delivery team one CRDB-owned place to build and test the MEL solution. | Confirm `TACATDP-CRDB-Dev` exists, has Dataverse, has enough capacity, and is accessible to named delivery/admin users. Assign Environment Maker/System Customizer where build work is expected. |
| Environment administration | Dataverse environment roles | Allows schema, solution import/export, Power Pages configuration, and troubleshooting. | Assign Dataverse `System Administrator` to the named CRDB platform owner/admin. Assign `System Customizer` or equivalent to approved delivery makers if they are expected to configure solution components. |
| Solution delivery | Power Platform solution, publisher, environment variables, connection references | Allows repeatable delivery instead of manual one-off edits. | Allow approved makers/admins to import/export unmanaged development solutions and configure development environment variables/connection references. |
| Portal hosting | Power Pages site in the same environment | Hosts the SFU review portal, dashboard, forms, saved records, beneficiary review, and access screens. | Create or confirm the CRDB development Power Pages site connected to `TACATDP-CRDB-Dev`. Give the delivery/site admin permission to update site pages, web files, site settings, and security configuration. |
| SFU reviewer access | Power Pages site visibility and Microsoft sign-in | Allows SFU users to open the development portal repeatedly without access-denied loops. | If the site is private, grant named SFU reviewers site visibility access first. Confirm the Microsoft sign-in path for those users. Successful Microsoft sign-in alone is not enough. |
| Portal user identity | Power Pages Contact and external identity | Links Microsoft sign-in to a portal user record. | Ensure each SFU reviewer/tester has a Contact and external identity after invitation/sign-in. Verify invitation redemption state where invitations are used. |
| Portal roles | Power Pages web roles | Controls whether reviewers, collectors, and admins can see the expected portal routes. | Assign required web roles, at minimum `Authenticated Users` plus project-specific roles such as reviewer/collector/admin as needed. |
| Page access | Power Pages page permissions | Controls which portal pages are visible to each reviewer role. | Enable page permissions for the review routes: dashboard, collect/form, saved records, beneficiaries, reporting, and user/access pages as required for review. |
| Dataverse table access from portal | Power Pages table permissions | Allows portal pages to read/write Dataverse records through Power Pages security. | Configure table permissions for required MEL tables. Minimum review path needs read access to project/form/form-version/assignment/reporting data. Submit path needs create access for submissions/submission versions and required append/append-to permissions. |
| Browser API access | Power Pages Web API `/_api` site settings | Allows the portal SPA to call Dataverse safely through Power Pages authentication. | Enable Web API site settings only for required development tables and fields. Verify browser `/_api` read/write after table permissions are saved. |
| Form collection | Dataverse form, assignment, submission, and submission-version tables | Allows baseline form testing and saved-record review. | Seed or allow creation of one project, one active form version, and active assignments for named reviewers/testers. Enable create/read permissions needed for submission testing. |
| Dashboard review | Portal dashboard and Dataverse reporting/prototype data | Allows SFU to review KPIs and visuals while prototype data is still demonstrative. | Enable reviewer read access to dashboard/reporting projection tables or demo data source used by the portal. Keep prototype figures labelled as demonstration data. |
| Beneficiary review | Dataverse beneficiary/party/intervention tables and portal routes | Allows SFU to review the beneficiary model and details as we refine the prototype. | Enable read access for reviewer roles. Enable write/edit only for approved admin/test roles if needed. |
| Access management testing | Contacts, web roles, assignments, access audit tables | Allows us to test the user onboarding and assignment flow that caused repeated access blockers. | Allow admin/reviewer path to inspect Contact, external identity, web role, assignment, and access-audit status. Enable create/update only for approved admin or automation owner. |
| Workflow/notifications | Power Automate, Dataverse connections, approved mailbox if used | Supports invitations, assignment notifications, review actions, and projection refresh where needed. | Assign a CRDB-owned flow owner or service account. Approve required development connectors and mailbox/notification path. Do not depend on a personal mailbox. |
| Connector governance | Power Platform DLP/data policies | Prevents development flows/apps from using blocked or unapproved connectors. | Confirm Dataverse, Power Pages, Power Automate, Power BI/Fabric, SharePoint/OneDrive, and any approved Azure connectors are allowed in the development policy. |
| Reporting proof | Power BI workspace or development reporting workspace | Allows SFU/BI users to review reporting direction if needed before production. | If Power BI review is required now, create/assign a development workspace and grant report authors Member/Admin and SFU reviewers Viewer access. |
| Evidence files | Dataverse file columns, notes, or approved Microsoft storage | Allows testing photos/files/evidence without unmanaged storage. | Confirm the approved development storage path and permissions. Keep sensitive evidence restricted to named roles. |
| Troubleshooting | Power Platform admin center, Power Pages diagnostics, Dataverse audit, flow run history | Allows quick diagnosis when sign-in, table permission, upload, or flow issues occur. | Name a CRDB admin/support contact who can inspect environment health, Power Pages settings, Dataverse roles, table permissions, and flow runs during review. |

## Minimum users/groups to enable

| Group/user type | Needed access |
|---|---|
| CRDB platform owner/admin | Environment admin, Dataverse System Administrator, Power Pages admin/site owner. |
| Delivery maker/admin | Environment Maker/System Customizer as approved, Power Pages update access, solution import/export access. |
| SFU reviewer | Power Pages site visibility if private, Microsoft sign-in, Contact/external identity, reviewer web role, read table permissions. |
| Test collector | Same as SFU reviewer plus assignment access and create permission for submissions/submission versions. |
| Flow/service owner | Approved flow owner or service identity with least-privilege Dataverse permissions and connector ownership. |

## Quick readiness check before sharing the portal link

- [ ] CRDB development environment `TACATDP-CRDB-Dev` is accessible.
- [ ] Dataverse is enabled in that environment.
- [ ] CRDB platform owner/admin has Dataverse `System Administrator`.
- [ ] Delivery maker has required maker/customizer access.
- [ ] Power Pages site exists in the same environment.
- [ ] Site visibility is confirmed.
- [ ] Named SFU reviewers have site visibility access if private.
- [ ] SFU reviewers can sign in with Microsoft.
- [ ] SFU reviewers have Contact/external identity records.
- [ ] SFU reviewers have the required web role.
- [ ] Required page permissions are enabled.
- [ ] Required table permissions are enabled.
- [ ] Required Power Pages Web API site settings are enabled.
- [ ] Browser `/_api` read test passes for an SFU reviewer.
- [ ] Form assignment/read path works.
- [ ] Submission create path works for a test collector.
- [ ] Saved-record read path works.
- [ ] Dashboard/reporting read path works.
- [ ] Flow/notification owner is confirmed if invitations or notifications are used.
- [ ] DLP policy allows the required Microsoft connectors.

## What to send back to the delivery team

CRDB admins can share the following non-secret details:

- environment display name and URL;
- Power Pages site name and website ID;
- site visibility state: private or public;
- named platform owner/admin;
- named delivery maker/admin users;
- named SFU reviewers/testers;
- confirmation of reviewer site visibility access;
- confirmation of web roles/table permissions/Web API settings;
- DLP connector confirmation;
- Power BI workspace details if reporting review is needed now.

Do not send passwords, client secrets, API keys, connection strings, bearer tokens, private keys, or `.env` contents.

## Non-goals

This checklist does not request:

- production deployment;
- production data access;
- broad tenant admin rights for all makers;
- anonymous Dataverse access;
- bypassing Power Pages table permissions;
- secrets in browser code or repository files.

## Microsoft references

- Power Platform environments: <https://learn.microsoft.com/en-us/power-platform/admin/create-environment>
- Dataverse security roles: <https://learn.microsoft.com/en-us/power-platform/admin/database-security>
- Power Pages security: <https://learn.microsoft.com/en-us/power-pages/security/power-pages-security>
- Power Pages table permissions: <https://learn.microsoft.com/en-us/power-pages/security/assign-table-permissions>
- Power Platform data policies: <https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss>
