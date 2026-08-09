# Reporting Power Pages Permissions: 2026-07-14

## Target

- Environment: `https://orga3cf4b37.crm4.dynamics.com`
- Site: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Web role: `Authenticated Users`

## Configured Tables

Power Pages Web API site settings and table permissions were added for:

- `mp_submissionreportrow`
- `mp_submissionrepeatrow`
- `mp_submissionanswer`
- `mp_exportsetting`

## Permission Shape

- `mp_submissionreportrow`: global read-only for authenticated users.
- `mp_submissionrepeatrow`: global read-only for authenticated users.
- `mp_submissionanswer`: global read-only for authenticated users.
- `mp_exportsetting`: global read/create/write/append/append-to for authenticated users; delete remains disabled.

## Commands

Dry-run:

```bash
python3 scripts/powerpages-configure-webapi.py \
  --website-id fccc0cc6-7f5e-4885-aeb8-2272e68130a3
```

Execute:

```bash
python3 scripts/powerpages-configure-webapi.py \
  --website-id fccc0cc6-7f5e-4885-aeb8-2272e68130a3 \
  --execute
```

Verify:

```bash
python3 scripts/verify-powerpages-api-smoke-hosted.py \
  --website-id fccc0cc6-7f5e-4885-aeb8-2272e68130a3 \
  --site-name "TACATDP Monitoring Tool"
```

## Verification Result

Hosted verifier passed after configuration:

- Entity sets matched for all 12 configured Dataverse tables.
- Web API settings count: 24 of 24.
- Table permission count: 12 of 12.
- Reporting tables are read-only for authenticated users.
- Export settings table has create/write/append/append-to and delete disabled.
- Existing API smoke, contact role, assignment, form version, and XForm checks still pass.

## Remaining Step

The portal can now read reporting projection tables through `/_api` once the UI is wired to those entity sets. The Exports and Power BI tabs still need implementation; this slice only configured the backend Power Pages access prerequisites.
