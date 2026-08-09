# Loading Performance Architecture - 2026-07-29

## Current Architecture

```text
Power Pages Home page
  -> preload datepicker/icon assets
  -> load SPA main module
  -> mount Vue app
  -> loadWorkspace()
       -> listAssignedForms()
       -> listSavedSubmissions()
            -> GET up to 5000 submissions
            -> GET latest version per submission
       -> refreshLocalDrafts()
  -> render selected workspace
```

This makes initial UX dependent on submitted-record volume and Dataverse latency.

## Target Architecture

```text
Power Pages Home page
  -> load critical shell CSS + SPA main module
  -> mount Vue app
  -> render managed shell
  -> loadWorkspaceLight()
       -> listAssignedForms()
       -> refreshLocalDrafts()
  -> render Dashboard/Projects

On Data tab open
  -> load paginated report rows
  -> fetch details only on View

On Reporting tab open
  -> lazy import datepicker if needed
  -> load reporting rows with server filters

On Collect action
  -> lazy import ODK Web Forms runtime
  -> fetch selected form version/XML
  -> render form runtime

On User & Access open
  -> load users/access rows
```

## Client State Boundaries

| State | Startup | Lazy trigger |
| --- | --- | --- |
| Session/user roles | yes | none |
| Assigned forms | yes | refresh |
| Local drafts | yes | refresh/sync |
| Submitted records | no | Data tab |
| Reporting rows | no | Reporting tab |
| Access users | no | User & Access tab |
| ODK runtime | no | Collect/Edit |
| Datepicker | no | Reporting/Data filters |

## API Strategy

- Use `mp_formassignments` only for startup assignment visibility.
- Use `mp_submissionreportrows` for list pages.
- Fetch full answers/versions only after explicit user action.
- Preserve server-side pagination and FetchXML count behavior already proven to
  avoid unsupported `$skip`.

## UX Strategy

- Shell renders before data.
- Each panel owns its loading/empty/error/retry state.
- Avoid full-page loading screens after authentication.
- Keep previous content visible during refresh where possible.

## Performance Instrumentation

Use browser Performance API:

```typescript
performance.mark('tacatdp:app-mounted');
performance.measure('tacatdp:listAssignedForms', start, end);
```

Expose a small admin/debug summary in console only. Do not log tokens, request
bodies, response bodies, or personal data beyond route/action labels.

## Deployment Architecture

1. Build SPA.
2. Upload to Mshirika.
3. Measure browser timings.
4. Upload to CRDB after approval.
5. Measure browser timings.
6. Document before/after numbers.
