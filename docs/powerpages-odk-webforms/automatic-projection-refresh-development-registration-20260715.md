# Automatic Projection Refresh Development Registration

Date: 2026-07-15
Target: current Power Pages development environment
Solution: `tacatdp_prototype`

## Outcome

The signed `Tacatdp.ReportingProjection.Plugin` assembly and its
`ProjectionRefreshPlugin` type were registered successfully. The assembly is
present in the solution as component type 91. No SDK message processing step or
post image was created, so the plug-in cannot execute yet.

On 2026-07-15 the user explicitly deferred execution-user/role provisioning and
step/post-image activation. This is an accepted delivery boundary, not a failed
portal deployment. Until activation, new and edited submissions remain canonical
in Dataverse but reporting projections refresh only when the trusted
`scripts/build-reporting-projections.py --execute` command is run.

The first upload attempt was rejected before component creation because the
unsigned assembly had no public key token. Strong-name signing was added and the
Release artifact was rebuilt successfully before the approved retry.

## Registered Components

- Assembly: `6cfe4209-c97f-f111-ab0e-7ced8d41fa2d`
- Plug-in type: `6ffe4209-c97f-f111-ab0e-7ced8d41fa2d`
- Assembly solution component: `6dfe4209-c97f-f111-ab0e-7ced8d41fa2d`
- Step: not registered
- Post image: not registered

## Activation Prerequisites

1. Create a dedicated Dataverse application user for the projection processor.
2. Create and review security role `TACATDP Projection Processor`.
3. Grant Read and Append To on canonical `mp_submission`,
   `mp_submissionversion`, and `mp_formversion` tables.
4. Grant Create, Read, Write, Delete, Append, and Append To on
   `mp_submissionreportrow`, `mp_submissionrepeatrow`, and
   `mp_submissionanswer` tables.
5. Assign only the reviewed role plus any platform-minimum application-user
   privileges required by Dataverse. Do not assign System Administrator.
6. Record the Dataverse `systemuserid`, not the Entra application ID.

## Registration Command

Inspect ADR 0004, the registration contract, this record, and the plug-in source
before execution. Then run:

```bash
.venv/bin/python scripts/dataverse-register-projection-plugin.py \
  --execution-user-id <dataverse-system-user-guid>

.venv/bin/python scripts/dataverse-register-projection-plugin.py \
  --execution-user-id <dataverse-system-user-guid> \
  --execute
```

The first command is a dry run. The command refuses non-development targets,
the deployment service principal, disabled users, users without the exact
required role, and contracts for another solution.

## Verification

After registration, verify one asynchronous Create/PostOperation step on
`mp_submissionversion`, execution order 20, the fixed execution user, and post
image alias `SubmissionVersionImage` containing only `mp_instanceid`. Confirm
the step and image are in `tacatdp_prototype`, then execute the hosted submit and
edit cases in the delivery plan and inspect System Jobs without exposing payload
values.

## Rollback

Disable the step first. Do not delete canonical or reporting data. If only the
current partial registration must be rolled back, remove the assembly from the
unmanaged solution through the normal solution process; do not delete the
assembly while dependent types or steps exist. Use the Python one-instance
projection builder to repair affected records after diagnosis.

## Protocol Applicability

- UX description: not applicable; this delivery changes Dataverse server-side
  registration only and adds no visible portal behavior while the step is absent.
- Accessibility checklist: not applicable; no user-interface element changed.
- Screenshot or render evidence: not applicable; live verification is the
  Dataverse component inventory and registration dry-run output, not a rendered
  screen.
