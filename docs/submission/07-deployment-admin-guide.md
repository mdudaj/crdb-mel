# Sustainable Finance MEL Platform Deployment and Administration Guide

## Purpose

This guide explains the deployment and administration considerations for the Sustainable Finance MEL Platform prototype. The current proof of concept uses TACATDP monitoring, Power Pages, and Dataverse.

## Current Prototype Architecture

```text
Power Pages portal
  -> Power Pages Web API
  -> Dataverse tables/entities
  -> Portal KPI dashboard
```

## Administrator Responsibilities

- Confirm the correct Power Platform environment.
- Verify the Power Pages site is connected to the expected Dataverse environment.
- Manage user access, site visibility, portal roles, and active assignments.
- Verify deployment state after changes.
- Avoid committing or exposing secrets.
- Document all environment-specific steps.

## Environment Verification

Use Power Platform CLI where available:

```bash
pac auth list
pac pages list
```

When PAC access fails, prefer verified Maker Portal environment IDs over guessed Dataverse organization URLs.

## Authentication Notes

- Do not assume Azure service principal or managed identity authentication unless explicitly approved and verified.
- Historical CRDB deployment work used device-code authentication with the delegated `dmuroba@crdb.co.tz` profile.
- Mshirika access must be verified against the correct tenant account and Power Pages environment.
- If sign-in succeeds but resource access fails, check tenant/environment permissions before diagnosing application code.

## User Access Checklist

For a non-admin user:

1. Confirm the user exists or can authenticate in the relevant tenant.
2. Confirm Power Pages site visibility access where the site is private.
3. Confirm the Power Pages contact exists.
4. Confirm the correct web role is linked.
5. Confirm the relevant form/project assignment exists.
6. Confirm assignment lifecycle/status is active.
7. Ask the user to sign out/in and retest.

## Deployment Verification Checklist

After deployment or configuration changes:

1. Confirm the portal loads.
2. Confirm the correct site/environment is being inspected.
3. Confirm latest web assets are active.
4. Confirm Dataverse records needed by the portal exist.
5. Confirm assigned users can see their form/project.
6. Submit or inspect a test record where approved.
7. Verify portal KPI dashboard renders expected values.
8. Record screenshots and command output for the testing report.

## Safety Rules

- Do not deploy to production without explicit approval.
- Do not print or commit secrets, tokens, `.env` values, authorization headers, or private keys.
- Do not commit raw Power Pages exports containing secret-bearing site settings.
- Do not modify production data without explicit approval.
- Do not rename deployed Dataverse tables/columns/forms without migration review.

## Troubleshooting

| Symptom | Check |
|---|---|
| User signs in but has no access | Site visibility, contact, web role, assignment, tenant permissions |
| User sees no project/form | Active assignment and lifecycle status |
| Portal still shows old UI | Cache purge, localized page content, asset references |
| PAC cannot list site | Correct auth profile, environment ID, tenant access |
| Dataverse write fails | Web API permissions, table permissions, choice values, required fields |

## Future Production Administration

The production platform should add formal:

- environment strategy;
- release management;
- backup and recovery;
- monitoring and observability;
- incident response;
- access review;
- data retention and privacy controls.
