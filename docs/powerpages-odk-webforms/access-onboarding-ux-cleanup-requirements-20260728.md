# Access Onboarding UX Cleanup Requirements - 2026-07-28

Status: implementation-ready for the pre-CRDB update cleanup slice.

## Purpose

Clean the User & Access onboarding surface before the CRDB production update. The page must support a bank administrator who needs to create or assign a user quickly, with clear confirmation and without internal implementation clutter.

## Research Basis

- Material Design steppers show progress through a logical numbered sequence and are appropriate when later fields depend on earlier fields.
- GOV.UK task-list guidance says to simplify the service before adding more task structure and to keep task labels short.
- GOV.UK step-by-step guidance says ordered journeys should follow the sequence users need to complete.
- Power Pages invitation guidance confirms invitations are sent through the native Send Invitation workflow to the invited contact primary email address.

References:

- https://m1.material.io/components/steppers.html
- https://design-system.service.gov.uk/components/task-list/
- https://design-system.service.gov.uk/patterns/step-by-step-navigation/
- https://learn.microsoft.com/en-us/power-pages/security/invite-contacts

## UX Description

The User & Access workspace should feel like an internal banking operations tool:

- quiet, dense, and predictable;
- few primary tabs;
- short labels;
- no long implementation paragraphs in the main task path;
- visible confirmation before mutation;
- status feedback after submit that remains visible and actionable.

The Add User workflow uses four ordered steps:

1. User: name and Microsoft account email.
2. Role: select the business role.
3. Access: choose project and form scope.
4. Review: provide business reason and queue the request.

The onboarding path is shown as a compact status card after the email is entered. It must not be a separate explanatory step.

## Functional Requirements

- The primary access navigation must expose only `Users`, `Add user`, and `Status`.
- The Add User workflow must be a four-step linear wizard.
- The review step must show user, role, project, forms, reason, workflow, and delivery path.
- Submit must remain disabled until required data and business reason are present.
- Successful submit must show a persistent queue result panel.
- The queue result must use concise labels: request id, queue status, delivery path, and processor responsibility.
- If onboarding is disabled, the UI must say no records are created until the queue is enabled.
- Detailed activation gates must live under `Status`, not inside the primary Add User flow.

## Look And Feel Requirements

- Stepper labels must be one or two words.
- Stepper state must be visible by numbered circles and connector line, not long instructions.
- Inputs must retain 48px minimum height and 16px text.
- The header must state the task plainly: `Create users, assign forms, and review access status.`
- Use restrained status chips and panels; avoid stacked advisory cards inside the wizard.

## Acceptance Criteria

- `vue-tsc --noEmit` passes.
- The User & Access tabs are reduced to `Users`, `Add user`, and `Status`.
- The Add User stepper renders four steps: `User`, `Role`, `Access`, `Review`.
- The old standalone `Onboarding path` step is removed.
- The review step no longer displays generated audit/mutation payload details.
- The disabled state uses the short message `No records are created until the onboarding queue is enabled.`
- The validator enforces the four-step Material-style stepper and compact onboarding status card.
