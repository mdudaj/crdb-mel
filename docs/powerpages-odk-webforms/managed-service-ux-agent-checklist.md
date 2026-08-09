# TACATDP Managed Service UX Agent Checklist

Use this checklist before and after every TACATDP portal UI change.

## Before Editing

- [ ] Read `managed-service-ux-governance.md`.
- [ ] Read `managed-portal-route-content-model.md`.
- [ ] Read `monitoring-tool-ux-design-system.md`.
- [ ] Read the feature-specific requirements/ADR for the slice.
- [ ] Confirm the target user role.
- [ ] Confirm the business entity being changed.
- [ ] Confirm data visibility scope.
- [ ] Confirm whether the flow is read-only or writes data.
- [ ] Confirm whether the write affects access, reporting, published forms, or
      customer/project data.
- [ ] Choose the governed pattern: Material tabs, table, drawer, dialog, wizard,
      or ODK runtime boundary.

## Required UX States

- [ ] Loading state.
- [ ] Empty state.
- [ ] No-results state for filtered/search views.
- [ ] Permission-denied state.
- [ ] Validation-error state.
- [ ] Save/submit in-progress state.
- [ ] Success state.
- [ ] Failure state with next action.
- [ ] Offline/degraded state when applicable.

## CRUD Safety

- [ ] Row actions do not directly perform high-impact writes.
- [ ] Detail/edit opens in a drawer or focused form surface.
- [ ] High-impact writes require confirmation.
- [ ] Confirmation copy states affected user/project/form/export.
- [ ] Confirm button uses a specific verb.
- [ ] Destructive/high-impact action is visually distinct.
- [ ] Discarding unsaved changes prompts only when changes exist.
- [ ] Write is idempotent where possible.
- [ ] Audit fields or audit expectation are documented.

## Material / Microsoft Shell

- [ ] Project sections use Material-style tabs with bottom indicator.
- [ ] Authenticated screens follow the shell slot order:
      `managed-side-nav`, `managed-app-content`, `managed-top-bar`,
      `managed-workspace-body`, `managed-app-footer`.
- [ ] The shell footer is outside page content and is not inside a hero, card,
      tab panel, table, drawer, or form runtime.
- [ ] The top bar contains one hamburger shell switcher at far left.
- [ ] Authenticated route content uses compact route anatomy: route header,
      optional status strip, primary content, contextual drawer/dialog, and
      route-level states.
- [ ] Dashboard is the default post-login route; project tabs stay inside the
      project route.
- [ ] Global Reporting opens a reporting route, not a side effect that jumps
      into a project tab.
- [ ] Side navigation separates top operational destinations from a bottom
      admin/configuration group.
- [ ] `User & Access`, configuration, settings, and security-sensitive items
      are in the bottom side-nav group and are role-gated.
- [ ] Dense record/user lists use tables on desktop/tablet.
- [ ] Mobile fallback uses cards with preserved labels.
- [ ] Drawer is right-side on desktop and full-screen on phone.
- [ ] Dialogs are used sparingly and only for focused decisions.
- [ ] No marketing hero, decorative blob, or oversized explanatory card is added
      to operational screens.

## Accessibility

- [ ] Icon-only actions have `aria-label`.
- [ ] Icon-only actions have tooltip or equivalent hover/focus label.
- [ ] Focus order is toolbar, table/list, row action, drawer/dialog.
- [ ] Drawer/dialog returns focus to triggering control.
- [ ] Status updates use visible text and `aria-live` where appropriate.
- [ ] State is not communicated by color alone.

## Verification

- [ ] `npm run build`
- [ ] `python3 scripts/validate-webforms-spa-foundation.py`
- [ ] Desktop visual check.
- [ ] Phone visual check.
- [ ] Hosted Power Pages check after upload when deployed.
- [ ] Handoff records changed UX rules, verification, and remaining risks.
