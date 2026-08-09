# Automatic Projection Refresh Traceability

| Requirement | Stories | Acceptance | Implementation surface | Verification |
| --- | --- | --- | --- | --- |
| APR-RQ-01, APR-RQ-02 | APR-US-01, APR-US-04 | APR-AC-01, APR-AC-10 | Async Create step | Dev submit/System Job |
| APR-RQ-03, APR-RQ-04 | APR-US-01, APR-US-02 | APR-AC-01, APR-AC-02, APR-AC-09 | Pure core, root upsert | Shared fixture parity |
| APR-RQ-05, APR-RQ-06 | APR-US-02, APR-US-05 | APR-AC-04, APR-AC-05 | Latest guard, alternate keys | Duplicate/out-of-order tests |
| APR-RQ-07 | APR-US-03 | APR-AC-03 | Child reconciliation | Removed answer/repeat test |
| APR-RQ-08, APR-RQ-12 | APR-US-04, APR-US-05 | APR-AC-06, APR-AC-07, APR-AC-08 | Failure classifier, async job | Malformed/transient tests |
| APR-RQ-09, APR-RQ-10 | APR-US-06 | APR-AC-10, APR-AC-11, APR-AC-12 | Execution user, solution | Role and component inventory |
| APR-RQ-11 | APR-US-05 | APR-AC-08 | `ITracingService` | Trace content assertions |
| APR-RQ-13, APR-RQ-14 | APR-US-05 | APR-AC-08, APR-AC-09 | Python repair + fixtures | One-instance rebuild parity |
| APR-RQ-15 | APR-US-01, APR-US-02 | APR-AC-13 | Async service | Dev latency evidence |
| APR-RQ-16 | APR-US-05, APR-US-06 | APR-AC-14 | Plug-in source | Static/source checks |
