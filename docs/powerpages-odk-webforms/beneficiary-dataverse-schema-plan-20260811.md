# Beneficiary Dataverse Schema Plan — 2026-08-11

Status: review-only. No Dataverse environment write is authorized or performed by this artifact.

## Artifact gate

- Work type: data/schema planning for the accepted Beneficiaries prototype slice.
- Existing artifacts reused:
  - `docs/app-vision.md`
  - `docs/multi-project-monitoring/data-model.md`
  - `docs/multi-project-monitoring/research.md`
  - `docs/powerpages-odk-webforms/beneficiary-detail-model-slice-20260811.md`
  - `schemas/dataverse/platform-tables.json`
  - `schemas/dataverse/platform-columns.csv`
  - `schemas/dataverse/platform-relationships.csv`
  - `schemas/dataverse/tacatdp-field-definitions.csv`
  - `schemas/dataverse/tacatdp-vocabulary-terms.csv`
  - `powerpages/webforms-spa/src/prototype/beneficiaries.ts`
- New artifacts:
  - `schemas/dataverse/beneficiary-entity-extension-schema.json`
  - `scripts/validate-beneficiary-entity-schema.mjs`
- Implementation boundary: review-only schema and prototype mapping text. No table creation, table permission change, site setting change, or Power Pages upload.
- Verification required:
  - `node scripts/validate-beneficiary-entity-schema.mjs`
  - `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/beneficiary-entity-extension-schema.json`
  - `npm run test:material`

## Decision

Use the existing generic `mp_TrackedEntity` as the central beneficiary identity. Do not create a standalone TACATDP-only `mp_beneficiary` table as the identity source.

Reason:

- The platform vision is reusable across programmes/projects, not only TACATDP.
- Existing schema artifacts already define `mp_TrackedEntity`, `mp_EntityIdentifier`, `mp_Encounter`, `mp_Submission`, and typed answer/projection tables.
- Beneficiaries can be farmers, groups, AMCOS, SACCOS, cooperatives, institutions, or other monitored subjects. A generic tracked-entity identity keeps that extensible.
- Finance, technology, training, and outcome facts are repeated/longitudinal. They should be child records, not flattened into one beneficiary row.

## Proposed additive tables

The schema extension adds current-state and analytics-friendly child tables around `mp_TrackedEntity`.

| Table | Purpose |
| --- | --- |
| `mp_BeneficiaryProfile` | Current profile extension for a beneficiary tracked entity. |
| `mp_BeneficiaryProgrammeParticipation` | Project/programme participation, role, enrolment, and partner context. |
| `mp_BeneficiaryFinanceLink` | Finance/loan snapshot without replacing CRDB core banking records. |
| `mp_BeneficiaryTechnologyAdoption` | Climate-smart technology financed/adopted by a beneficiary. |
| `mp_BeneficiaryTrainingParticipation` | Training/capacity-building participation summary. |
| `mp_BeneficiaryOutcomeSnapshot` | Measured, estimated, or modelled outcome fact for reporting. |
| `mp_BeneficiarySubmissionLink` | Lineage between submissions and the beneficiary records they update. |
| `mp_BeneficiaryIdentityMatch` | Review queue for candidate matches before merging or updating a tracked entity. |
| `mp_BeneficiaryGroupMembership` | Membership between group beneficiaries and individual tracked entities. |
| `mp_BeneficiaryLocationHistory` | Time-bound geography history for beneficiaries whose location changes or is corrected. |

## Relationship model

```text
mp_Project
  ├─ mp_TrackedEntity
  │   ├─ mp_BeneficiaryProfile
  │   ├─ mp_BeneficiaryProgrammeParticipation
  │   ├─ mp_BeneficiaryFinanceLink
  │   ├─ mp_BeneficiaryTechnologyAdoption ── mp_VocabularyTerm
  │   ├─ mp_BeneficiaryTrainingParticipation ── mp_VocabularyTerm
  │   ├─ mp_BeneficiaryOutcomeSnapshot ── mp_Submission / mp_Encounter
  │   ├─ mp_BeneficiarySubmissionLink ── mp_Submission
  │   ├─ mp_BeneficiaryIdentityMatch ── mp_Submission / mp_TrackedEntity(candidate)
  │   ├─ mp_BeneficiaryGroupMembership ── mp_TrackedEntity(member)
  │   └─ mp_BeneficiaryLocationHistory
  └─ mp_Submission
```

`mp_Submission` and the ODK-style submission version tables remain the source of truth for collected payloads. The beneficiary extension tables are derived/current-state surfaces for operational UX, dashboards, and later exports.

## Prototype-to-Dataverse mapping

| Prototype field | Proposed Dataverse target |
| --- | --- |
| `id` | `mp_TrackedEntity.mp_entitykey`; also an `mp_EntityIdentifier` row if external identifiers exist. |
| `name` | `mp_TrackedEntity.mp_displayname` and `mp_BeneficiaryProfile.mp_name`. |
| `category` | `mp_BeneficiaryProfile.mp_beneficiarycategory` and optionally `mp_TrackedEntity.mp_entitytype`. |
| `region`, `district` | `mp_BeneficiaryProfile.mp_region`, `mp_BeneficiaryProfile.mp_district`; later can reference governed geography tables. |
| `verificationStatus` | `mp_BeneficiaryProfile.mp_verificationstatus`. |
| `projectParticipation` | `mp_BeneficiaryProgrammeParticipation`. |
| `finance` | `mp_BeneficiaryFinanceLink`. |
| `technologiesFinanced` | One or more `mp_BeneficiaryTechnologyAdoption` rows. |
| `trainingSummary` | One or more `mp_BeneficiaryTrainingParticipation` rows. |
| `latestSubmission` | `mp_BeneficiarySubmissionLink` plus `mp_Submission`/ODK submission version state. |
| `outcomeSnapshot` | One or more `mp_BeneficiaryOutcomeSnapshot` rows. |
| `futureDataverseMapping` | Prototype-only helper text; should point to `mp_TrackedEntity` plus extension tables. |

## Prototype-to-product boundaries

The prototype can show a beneficiary as a single card or detail drawer, but the product model must keep these concepts separate:

- The raw baseline or monitoring submission remains immutable evidence.
- `mp_TrackedEntity` is the reusable beneficiary identity across reporting cycles.
- `mp_BeneficiaryProfile` is the current operational profile projection.
- `mp_BeneficiaryIdentityMatch` is the deduplication and review queue. It prevents the import path from silently creating duplicate farmers, groups, AMCOS, or SACCOS records when names, phone numbers, locations, or external references are similar.
- `mp_BeneficiaryGroupMembership` represents group-to-member relationships. A farmer group, AMCOS, or SACCOS can be a beneficiary in its own right while still linking to individual farmers when member-level tracking becomes approved.
- `mp_BeneficiaryLocationHistory` records corrected or changed geography over time instead of overwriting the only location evidence.
- Finance snapshots in `mp_BeneficiaryFinanceLink` are reporting/integration references only; they are not a replacement for CRDB core banking systems.

The first implementation should create or update `mp_TrackedEntity` only after the identity match decision is clear. Until then, baseline submissions can remain linked through `mp_BeneficiarySubmissionLink` with `mp_reviewstatus=Under review`.

## Governance rules

- Do not store sensitive core banking identifiers in the portal-facing schema without a security/privacy review.
- Use masked finance references or integration keys until CRDB approves the finance integration boundary.
- Keep source submission lineage for every derived finance, technology, training, and outcome fact where available.
- Do not auto-merge beneficiary records from fuzzy matching alone. Store candidate matches, confidence, matching signals, reviewer decision, and reviewer timestamp.
- Store group membership separately from beneficiary profile data. Do not flatten member farmers into group profile text fields.
- Preserve location history when a beneficiary location changes or is corrected; dashboard filters may use the current profile location, but audit and longitudinal analysis need the historical rows.
- Differentiate measured, estimated, modelled, and awaiting-verification values with `mp_measurementmethod`.
- Keep `mp_Project` required on child tables so the model remains multi-project and delegation-safe.
- Use governed vocabulary terms for TACATDP technology and training categories when importing controlled values.
- Do not make app-visible required XLSForm fields required at Dataverse column level unless the backend write path guarantees all skip-logic conditions.

## Open questions before environment write

1. Should implementation partners use a future organization table instead of text snapshots in this slice?
2. Which finance references can be stored safely in Dataverse and shown in Power Pages?
3. Should beneficiary category be a Dataverse Choice or a `mp_VocabularyTerm` lookup from a governed scheme?
4. Which outcome indicators should be first-class projection rows versus calculated dashboard aggregates?
5. Which identity matching signals are approved for use: name, phone, village, national identifier, group membership, CRDB customer reference, or project-issued beneficiary code?
6. Which user role is allowed to approve a beneficiary merge or identity-link decision?
7. Should group membership be enabled in the prototype seed data now, or kept as schema-only until member-level collection is added?
8. Should current profile geography reference `mp_VillageReference` immediately, or keep text snapshots until the first schema import validates high-volume lookup performance?

## Implementation instructions for the next backend slice

1. Review this plan and `schemas/dataverse/beneficiary-entity-extension-schema.json`.
2. Run:

   ```bash
   node scripts/validate-beneficiary-entity-schema.mjs
   python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/beneficiary-entity-extension-schema.json
   ```

3. Confirm the target environment with:

   ```bash
   source scripts/use-powerplatform-env.sh mshirika
   pac env who
   pac pages list
   ```

4. Do not run `dataverse-schema-deploy.py` until the schema and target environment are explicitly approved.
5. If approved later, deploy additively through a solution-aware schema path, then configure Power Pages Web API and table permissions as a separate approved slice.
