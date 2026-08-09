# Loading Performance Investigation - 2026-07-29

## Purpose

Investigate why the TACATDP Power Pages portal feels slow to load in Mshirika and
slower in CRDB, and define a safe improvement plan before further UX polishing.

## Current User-Observed Problem

- `https://tacatdp.powerappsportals.com/` takes noticeable time before the whole
  portal is available.
- After the shell loads, content loading still takes additional time.
- The same pattern is worse in the CRDB environment.

## Evidence Collected

### Live Mshirika Anonymous Timing

From the Linux environment:

```text
curl -L https://tacatdp.powerappsportals.com/
home dns=0.409672 connect=0.999317 tls=2.793524 starttransfer=3.936152 total=4.141154 size=48521
```

This measured the redirect/sign-in path rather than authenticated portal runtime,
because anonymous access redirects to Microsoft sign-in. It still shows that the
first navigation can spend several seconds before the SPA assets or authenticated
data calls are involved.

### Static Asset Footprint

Current source web-file payload includes:

| Asset | Approx size |
| --- | ---: |
| `MapBlock-BTX9u64V-CNidbrSB.mjs` | 475 KB |
| `vendor-datepicker-B-UpImsy.mjs` | 283 KB |
| `vue-konva-D0sZ6RWk-De_G96cE.mjs` | 186 KB |
| `index-00W4I3DT.mjs` | 131 KB |
| `index-0EKo1gv8.mjs` | 124 KB |
| `runtime-core.esm-bundler-sjoBfEhY.mjs` | 66 KB |
| `index-CfUxfRBd.css` | 54 KB |
| `index-DrXUV5Mx.css` | 53 KB |
| `vendor-datepicker-D7vsgEFT.css` | 23 KB |

The upload package also carries older generated web files and portal template
CSS assets. The current Home page references only the newer `index-0EKo1gv8.mjs`
and `index-CfUxfRBd.css`, but stale active web-file records can still increase
site startup/configuration overhead and should be cleaned up.

### Current Home Page Asset Loading

The Home page explicitly preloads datepicker and icons:

```html
<link rel="modulepreload" crossorigin href="/assets/vendor-datepicker-B-UpImsy.mjs?...">
<link rel="modulepreload" crossorigin href="/assets/vendor-icons-DA7Dp-7A.mjs?...">
<link rel="stylesheet" crossorigin href="/assets/vendor-datepicker-D7vsgEFT.css?...">
<link rel="stylesheet" crossorigin href="/assets/index-CfUxfRBd.css?...">
<script type="module" crossorigin src="/assets/index-0EKo1gv8.mjs?..."></script>
```

This means the reporting datepicker is prioritized during initial portal load
even though most users first land on Dashboard/Projects.

### Startup Data Loading

`AssignedFormsView.vue` calls `loadWorkspace()` on mount. That currently loads:

```typescript
await Promise.all([
  api.listAssignedForms(),
  api.listSavedSubmissions(),
  refreshLocalDrafts(),
]);
```

`listSavedSubmissions()` calls:

```text
/_api/mp_submissions?$select=...&$filter=mp_lifecyclestatus eq submitted&$orderby=mp_updatedat desc&$top=5000
```

Then it performs a latest-version lookup for each returned submission:

```typescript
return Promise.all(submissions.value.map(async (submission) => {
  const latestVersion = await this.getLatestSubmissionVersionByInstanceId(submission.mp_instanceid);
  ...
}));
```

This creates a high-cost startup pattern:

- Fetch up to 5,000 submitted records before initial content is complete.
- Run one additional Web API call per submission.
- Load shared submission data even when the first useful view is Dashboard or
  Projects.

This is the strongest code-level explanation for "shell loads, then content
loading takes more time", especially in CRDB where Dataverse/Power Pages latency
and cache warmth may differ from Mshirika.

### ODK Runtime Loading

`main.ts` dynamically imports `@getodk/web-forms` unless
`VITE_TACATDP_ODK_RUNTIME_ENABLED=false`:

```typescript
if (import.meta.env.VITE_TACATDP_ODK_RUNTIME_ENABLED === 'false') {
  app.mount('#app');
} else {
  const { webFormsPlugin } = await import('@getodk/web-forms');
  app.use(webFormsPlugin).mount('#app');
}
```

The Mshirika access build script currently disables this runtime, but generic
builds can block app mounting on the ODK import. The ODK runtime should be loaded
only when the user opens Collect, not before the shell renders.

## Microsoft Power Pages Guidance

Microsoft documents that Power Pages uses server-side caching for Dataverse data
and website metadata; Web API calls benefit from that cache, but clearing cache
causes temporary performance degradation. Frequent cache clearing should be
avoided on live sites.

Microsoft Site Checker performance guidance highlights:

- Disabled header/footer output caching can affect performance.
- A large number of active web files can slow site startup.
- Web files not needed on the home page should not be loaded with the home page.
- Too many web roles can affect performance, though TACATDP currently has a very
  small role count.

Microsoft also documents that Power Pages CDN can improve performance by serving
static content from edge servers. CDN is available for production websites, but
not trial websites.

Sources:

- Microsoft Learn: Configure a site with Content Delivery Network.
- Microsoft Learn: Site Checker performance.
- Microsoft Learn: How server-side caching works in Power Pages.
- Microsoft Learn: Portals Web API overview.

## Working Hypotheses

1. **Initial navigation/auth overhead**: first load includes Power Pages and
   Microsoft identity redirects. This is mostly platform/tenant dependent.
2. **Static asset overhead**: the home page preloads datepicker assets that are
   not needed for the initial Dashboard/Projects experience.
3. **Stale web-file footprint**: older hashed bundles remain as active web files.
   They are not directly referenced by Home, but Microsoft flags large web-file
   footprint as a startup risk.
4. **Startup API waterfall**: `listSavedSubmissions()` loads all submitted
   records and performs per-submission latest-version lookups during first
   workspace load.
5. **Cache state**: after deployments, cache purges, restarts, or table changes,
   Power Pages server-side cache is cold and content loading is expected to be
   slower for a period.
6. **CRDB environment factors**: CRDB may add conditional access, tenant policy,
   Exchange/identity checks, or Dataverse latency that Mshirika does not have.

## Recommended Improvement Plan

### Slice 1 - Instrument Before Changing UX

Add lightweight client-side performance marks visible only to admins or console:

- `portal-html-ready`
- `spa-main-loaded`
- `app-mounted`
- `assignments-loaded`
- `submissions-loaded`
- `reporting-loaded`
- `access-users-loaded`

Log API durations for:

- `listAssignedForms`
- `listSavedSubmissions`
- `listSubmissionReportRows`
- `listAccessUsers`

Acceptance:

- We can compare Mshirika and CRDB with real timings from the same browser path.
- No secrets, tokens, or payload bodies are logged.

### Slice 2 - Improve Perceived Loading UX

Render the shell immediately with stable skeleton states:

- Left nav, top bar, and footer render before data finishes.
- Dashboard shows "Loading assigned projects" skeleton.
- Project/Data tabs load their own content lazily.
- Keep current page visible while refreshes run.
- Use clear bank-appropriate messages: "Loading assigned projects", "Loading data
  page", "Preparing form".

Acceptance:

- User sees the managed shell quickly even if data takes time.
- Slow API calls do not leave a blank or frozen portal.

### Slice 3 - Remove Startup Submission Load

Change startup from:

```text
assignments + all submissions + drafts
```

to:

```text
assignments + drafts only
```

Load submissions only when:

- User opens a project Data tab.
- User opens Reporting.
- User requests refresh.

Use existing reporting projection table for paginated data instead of loading
`mp_submissions` + latest versions on startup.

Acceptance:

- Initial workspace load does not call `listSavedSubmissions()`.
- Data tab loads one page at a time.
- Reporting uses server-side pagination and filters.

### Slice 4 - Replace Per-Record Latest-Version Lookups

Avoid one Web API call per submission. Preferred options:

1. Use `mp_submissionreportrow` projection as the default list source.
2. Add required display fields to the projection if missing.
3. For detail view, fetch a single record's full answers/versions only when the
   user clicks View.

Acceptance:

- Listing 100 records does not create 101+ API calls.
- Data list remains fast in CRDB.

### Slice 5 - Lazy Load Heavy UI Dependencies

Move datepicker and ODK runtime out of initial route:

- Import datepicker only when Reporting/Data filters render.
- Import `@getodk/web-forms` only when Collect opens.
- Remove Home page `modulepreload` for datepicker unless Reporting is the initial
  route.
- Keep icons lightweight or ensure only used icons are bundled.

Acceptance:

- Initial JS/CSS payload is smaller.
- Dashboard/Projects do not download datepicker runtime.
- Collect still loads the ODK runtime when needed.

### Slice 6 - Clean Stale Web Files

Remove or deactivate old hashed bundles and obsolete CSS from the site package:

- Keep only current referenced assets.
- Confirm old files are not referenced by Home, templates, snippets, or web-file
  metadata.
- Re-upload package and restart/purge cache once.

Acceptance:

- Power Pages web-file list contains only current required SPA assets and platform
  files.
- No 404s in browser Network tab.

### Slice 7 - CRDB Platform Settings

Ask CRDB admins to run Power Pages Site Checker and confirm:

- Header output cache enabled.
- Footer output cache enabled.
- Sign-in tracking disabled or not applicable.
- No excessive active web files.
- CDN enabled if this is a production Power Pages site and CRDB policy allows it.

Acceptance:

- Site Checker performance warnings are reviewed.
- CDN decision is documented. CDN is not available for trial sites and requires a
  production website administrator.

## Proposed Priority

Do first:

1. Instrument timings.
2. Remove startup submission load.
3. Lazy load datepicker/ODK runtime.
4. Add skeleton loading states.

Do next:

5. Clean stale web files.
6. CRDB Site Checker/CDN review.

Do later:

7. Deeper reporting projection optimization and server-side aggregation.

## Risks and Notes

- Avoid frequent cache purges during live review; Microsoft notes that clearing
  Power Pages cache can temporarily degrade performance.
- Do not enable CDN without CRDB admin approval and policy review.
- Avoid hiding slow operations behind generic spinners. The bank-user UX should
  show stable shell, task-specific loading labels, and recoverable retry actions.
- Do not optimize by broadening table permissions or disabling OData filters
  unless there is a measured and reviewed reason; broader security changes can
  create data exposure risk.
