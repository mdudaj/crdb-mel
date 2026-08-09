# User & Access Write Preview UI - 2026-07-21

Status: implemented without enabling Dataverse writes.

## Scope

Wire the User & Access confirmation flows to the disabled write service shell so administrators can inspect the exact audit and future mutation payloads before the write path is approved.

## UX Behavior

- Change role, suspend, and reactivate confirmations now generate an access write preview from the selected user, action, reason, current state, and proposed state.
- Add user confirmation now generates one `AssignForm` preview per selected form version.
- Each preview shows request id, audit key or action, affected user, actor/status, and expandable JSON for:
  - audit payload;
  - future mutation payload.
- The UI continues to show `Write actions disabled` from the centralized service readiness gate.
- The final action buttons remain disabled.

## Safety Boundary

- No audit rows are created.
- No assignment rows are created or updated.
- No contact rows are created or updated.
- The only generated data is a browser-side preview derived from current UI state.

## Verification

```bash
python3 scripts/validate-access-write-preview-ui.py
python3 scripts/validate-access-write-service-shell.py
npm --prefix powerpages/webforms-spa run typecheck
npm --prefix powerpages/webforms-spa run build
python3 scripts/validate-webforms-spa-foundation.py
git diff --check
```
