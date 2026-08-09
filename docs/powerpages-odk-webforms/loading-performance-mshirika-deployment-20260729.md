# Loading Performance Mshirika Deployment Evidence

Date: 2026-07-29

## Task Classification

Deployment smoke slice for TACATDP loading performance slice 1. Environment-changing action; no Dataverse schema or permission changes were made.

## Target

- PAC profile: `tacatdp-powerpages-sp`
- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Site: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Portal URL: `https://tacatdp.powerappsportals.com/`

## Change Summary

Uploaded the prepared Power Pages package from:

```bash
./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool
```

The package contains the optimized SPA entry bundle `index-D8Tmzwaz.mjs`, the new icon chunk `vendor-icons-CVcq-M7M.mjs`, and the lazy datepicker chunk `vendor-datepicker-C8ItObQq.mjs`. Home page fragments reference `loading-performance-20260729-001` cache-busting query strings and no longer preload the datepicker JavaScript chunk.

## Verification Before Upload

Commands run from `/home/jmduda/KodeX.2026/tacatdp`:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-access
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-mshirika-activation.py
git diff --check
pac env who
pac pages list
```

Results:

- `build:mshirika-access`: passed.
- `validate-webforms-spa-foundation.py`: passed.
- `validate-access-mshirika-activation.py`: passed.
- `git diff --check`: passed.
- PAC target confirmed as Mshirika developer environment.
- PAC site list confirmed `TACATDP Monitoring Tool`.

## Upload Command

```bash
pac pages upload \
  --environment "https://orga3cf4b37.crm4.dynamics.com/" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

- Upload succeeded in 58.23 seconds.
- PAC printed several `powerpagecomponent ... Does Not Exist` update warnings during sync, but completed with `Power Pages website upload succeeded`.

## Hosted Check

Unauthenticated `curl` to the portal returns Microsoft sign-in HTML, so it cannot prove the authenticated SPA fragment. Direct asset checks also returned authenticated HTML because the site protects web files behind sign-in.

Uncached sign-in response timing captured:

```text
home dns=0.151470 connect=0.651254 tls=2.478236 starttransfer=4.252736 total=4.560797 size=48527
```

This is not the authenticated SPA timing and should not be treated as final UX performance evidence.

## Manual Review Steps

1. Open `https://tacatdp.powerappsportals.com/` while signed in.
2. If the old bundle is still served, purge site cache and restart/sync the site once from Power Pages admin/preview.
3. In browser DevTools Console, enable timing logs:

```js
localStorage.setItem('TACATDP_DEBUG_PERF', 'true');
location.reload();
```

4. Confirm the console shows `[TACATDP perf]` lines for:
   - `app-mounted`
   - `api:listAssignedForms`
   - `view:loadWorkspace`
5. Confirm initial navigation reaches the dashboard/projects without waiting for saved submission records.
6. Open a project Data tab and confirm reporting rows load there.
7. Open date filters and confirm the calendar still renders.

## Residual Risk

Cache purge/restart was not performed from CLI because PAC 2.9.3 exposes Pages upload/download/list, but not a cache-purge or site-restart command. Manual admin review is still required before timing evidence is considered complete.
