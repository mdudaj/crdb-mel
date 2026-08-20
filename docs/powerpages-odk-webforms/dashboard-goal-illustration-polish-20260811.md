# Dashboard Goal Illustration Polish — 2026-08-11

## Scope

Polished the `Program Impact Goal` card on the TACATDP dashboard.

The change is limited to the card illustration treatment:

- keep the supplied farmer image acting as the full-card background;
- avoid cropping the top or right of the image;
- keep the body copy on the upper-left of the card;
- preserve readable text over the illustration.

## Implementation

Updated `TacatdpDashboardPage.vue`:

- changed `.goal-illustration` from `object-fit: cover`/`contain` to `object-fit: fill`;
- kept `object-position: center center`;
- increased illustration opacity;
- added a subtle left-to-right white scrim behind `.programme-goal-copy`.

Updated `validate-dashboard-visual-spacing.mjs`:

- fails if the goal illustration returns to `object-fit: cover`;
- verifies full-card background fill rather than contained/small rendering;
- verifies center anchoring;
- verifies the text readability scrim remains.

## Verification

Local:

```bash
npm run test:material
npm run test:powerpages-assets
npm run build:mshirika-runtime
node --check powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files/index-DipH1t7d.mjs
```

Mshirika deployment:

- Fresh Mshirika package downloaded before staging.
- Current SPA build staged and package hygiene validated.
- Full `pac pages upload --modelVersion Enhanced` succeeded in 59.22 seconds.

Post-upload:

- Live Mshirika package downloaded.
- `node scripts/verify-powerpages-spa-assets.mjs` passed against the live web-files.
- `scripts/validate-powerpages-package-hygiene.py --environment-url https://orga3cf4b37.crm4.dynamics.com/` passed.
- Home root and localized Home reference:
  - `/assets/index-DipH1t7d.mjs`
  - `/assets/index-DO53UQ7f.css`
  - marker `beneficiary-schema-align-20260811-021`

## Remaining gate

Manual browser review on Mshirika is required for final visual acceptance.

CRDB was not updated in this slice because the user could not review CRDB at the
time.
