# Add User Material Control Sizing - 2026-07-22

Status: implemented for the User & Access Add User workflow.

## Requirement

The Add User workflow must use consistent Material-style form controls. Text typed into full name, email, role, project, and business reason controls must be comfortably legible for bank staff on desktop and mobile.

## UX Rules

- Field labels remain visible above controls.
- Single-line inputs and selects use 16px input text with 24px line height.
- Single-line controls have a minimum 48px height.
- Textareas use the same 16px input text and a larger minimum height for business reasons.
- Focus states use the established shell focus ring and primary border color.
- Checkbox inputs use the platform primary accent and a larger visible hit target.
- Stepper buttons use at least a 48px height.

## Evidence

- Material text-field guidance treats 16sp input text as the standard legible field size.
- Material accessibility guidance recommends 48dp touch targets for interactive controls.
- The existing portal shell remains quiet and operational; this change affects control sizing, not navigation or workflow semantics.

## Acceptance Criteria

- Add User full-name and email typed text is visibly larger than the previous compact filter-field style.
- Role and project selects match the same control height and text size as inputs.
- Business reason textarea uses the same input text size and has enough height for multi-line review text.
- Tab order, visible labels, helper text, and focus states remain intact.

## Verification

- `npm --prefix powerpages/webforms-spa run typecheck`
- `python3 scripts/validate-access-create-invite-assign-ux.py`
- `python3 scripts/validate-webforms-spa-foundation.py`
- Browser/render review of User & Access > Add User after the next portal upload.
