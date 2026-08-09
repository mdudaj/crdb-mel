# Automatic Projection Refresh Definition of Done

- ADR 0004 is approved.
- Pure C# projection core passes shared Python/C# fixtures.
- Plug-in is stateless and contains no secrets, payload logging, parallelism, or batch request messages.
- Create/PostOperation/asynchronous step and post image match the documented registration contract.
- Dedicated execution user has reviewed least-privilege access.
- New submit creates a Ready projection automatically without browser projection writes.
- Edit updates the same root to N+1 and removes obsolete answer/repeat rows.
- Duplicate and out-of-order events are idempotent/no-op as appropriate.
- Malformed payload and transient/unexpected failure paths are observable without rolling back canonical data.
- Python one-instance/full rebuild remains passing and repairs a failed projection.
- Assembly, type, step, and image are included in `tacatdp_prototype` and verified in exported solution source.
- Unit, adapter, integration, static/source, solution, and existing SPA/projection validators pass.
- Deployment and rollback evidence identifies target environment, solution version, step id/name, execution user/role, verification results, and remaining risk.
