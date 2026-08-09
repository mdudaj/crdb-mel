# Access Onboarding UX Cleanup Accessibility Checklist - 2026-07-28

Status: checked against source implementation.

## Checklist

- The User & Access route keeps semantic tabs for primary sections.
- The Add User stepper remains a named navigation landmark with `aria-current="step"` on the active step.
- Step buttons remain keyboard reachable and preserve clear visible active/completed states.
- Inputs retain visible labels; placeholders are not the only labels.
- Form controls retain at least 48px target height and 16px input text.
- Result messages use `role="status"` and `aria-live="polite"`.
- Error messages use `role="alert"` where submission fails.
- The wizard keeps a confirmation/review step before mutation.
- Long generated payload text is removed from the main workflow to reduce screen-reader noise.
- Raw invitation codes and links remain absent from the portal UX.

## Residual Risk

No browser screenshot was captured in this slice. Visual behavior is verified by source review, typecheck, and build validation. Browser screenshot should be captured before CRDB production smoke sign-off.
