# CRDB Access Readiness Render Evidence - 2026-07-22

Status: local render/build evidence captured from the Power Pages SPA source.

## Rendered Surfaces

- User & Access > Configuration renders `CRDB update package`.
- The readiness section renders `User management and assignment readiness`.
- Readiness cards render `User & Access UI`, `AssignForm service path`, `AccessAuditLogs schema`, `Portal permissions`, and `Activation smoke tests`.
- User & Access > Create, invite and assign > Review renders `Business reason`.
- The confirmation step renders `Onboarding activation` and the onboarding activation gates from `getUserOnboardingReadiness()`.
- The confirmation step renders `Access creation results` after an enabled AssignForm write returns.
- The final Add User action remains `Create, invite and assign disabled`.

## Build Evidence

`npm --prefix powerpages/webforms-spa run build` completed successfully and produced:

- `dist/index.html`
- Default build: `dist/assets/index-C1ahOxBL.mjs`
- Mshirika access test build: `dist/assets/index-LYSO0-2P.mjs`
- Mshirika access test vendor chunks: `dist/assets/vendor-datepicker-B-UpImsy.mjs`, `dist/assets/vendor-icons-DA7Dp-7A.mjs`
- Mshirika access stylesheets: `dist/assets/index-TPIRZmo9.css`, `dist/assets/vendor-datepicker-D7vsgEFT.css`
- Upload package Home references use cache buster `mshirika-access-20260722-002`.

Known non-blocking build warnings remain from the upstream `@getodk/web-forms` bundle using direct `eval` and large chunks.
