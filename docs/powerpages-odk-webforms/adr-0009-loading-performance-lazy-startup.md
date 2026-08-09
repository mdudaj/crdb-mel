# ADR 0009: Lazy Startup For Loading Performance

## Status

Proposed - 2026-07-29

## Context

The TACATDP Power Pages SPA currently loads assignments, drafts, and submitted
record summaries during initial mount. Submitted record loading can request up
to 5,000 records and then issue one latest-version lookup per record. This
causes slow content availability after the portal shell loads, especially in the
CRDB environment.

Microsoft Power Pages guidance confirms that Web API calls benefit from
server-side caching, but cache clears cause temporary slowness. Microsoft Site
Checker guidance also flags unnecessary home-page web files and large web-file
footprints as performance risks. Production Power Pages sites can use CDN for
static assets, subject to administrator approval.

## Decision

Adopt lazy startup:

- Initial mount loads only authenticated session context, assigned forms, and
  local drafts.
- Data and Reporting load only when the user opens those views.
- Submission lists use paginated projection data instead of `mp_submissions`
  plus per-record latest-version lookups.
- ODK Web Forms runtime loads only when Collect starts.
- Datepicker runtime is not preloaded for default Dashboard/Projects startup.
- Lightweight admin/debug timing marks are added to compare Mshirika and CRDB.

## Alternatives Considered

### Keep Current Startup And Add Better Spinner

Rejected. It improves perceived feedback slightly but keeps the expensive
startup behavior.

### Enable CDN First

Deferred. CDN can help static files on production Power Pages sites, but it does
not fix the current Web API waterfall and requires CRDB administrator approval.

### Broaden Power Pages Cache Or Disable OData Filtering

Rejected for this slice. It can have security/performance side effects and does
not address the root cause of loading unnecessary data.

### Server-Side Aggregation First

Deferred. Useful later for dashboards, but the first improvement should remove
unnecessary startup calls and prove timing impact.

## Consequences

Positive:

- Faster initial shell/dashboard availability.
- Lower Dataverse/Power Pages Web API load at startup.
- Better CRDB performance profile under authenticated use.
- Clearer timing evidence for future optimization.

Tradeoffs:

- Data and Reporting tabs will show their own loading states when first opened.
- Implementation must carefully preserve route restoration and after-submit
  outcome handling.
- Tests must verify that lazy-loaded views still fetch data at the right time.

## References

- `loading-performance-investigation-20260729.md`
- Microsoft Learn: Configure a site with Content Delivery Network.
- Microsoft Learn: Site Checker performance.
- Microsoft Learn: How server-side caching works in Power Pages.
- Microsoft Learn: Portals Web API overview.
