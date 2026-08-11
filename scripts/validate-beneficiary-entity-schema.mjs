#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');

const schemaPath = resolve(repoRoot, 'schemas/dataverse/beneficiary-entity-extension-schema.json');
const planPath = resolve(repoRoot, 'docs/powerpages-odk-webforms/beneficiary-dataverse-schema-plan-20260811.md');
const prototypePath = resolve(repoRoot, 'powerpages/webforms-spa/src/prototype/beneficiaries.ts');

const schemaSource = readFileSync(schemaPath, 'utf8');
const planSource = readFileSync(planPath, 'utf8');
const prototypeSource = readFileSync(prototypePath, 'utf8');
const schema = JSON.parse(schemaSource);

function fail(message) {
  throw new Error(message);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function assertIncludes(source, fragment, message) {
  assert(source.includes(fragment), message);
}

assert(schema.generated_for_review_only === true, 'Beneficiary schema must be marked review-only.');
assert(schema.environment_write === false, 'Beneficiary schema must explicitly deny environment writes.');
assert(schema.schema_name === 'beneficiary_entity_extension', 'Unexpected beneficiary schema name.');

const tableNames = new Set(schema.tables.map((table) => table.name));
const requiredTables = [
  'mp_BeneficiaryProfile',
  'mp_BeneficiaryProgrammeParticipation',
  'mp_BeneficiaryFinanceLink',
  'mp_BeneficiaryTechnologyAdoption',
  'mp_BeneficiaryTrainingParticipation',
  'mp_BeneficiaryOutcomeSnapshot',
  'mp_BeneficiarySubmissionLink',
  'mp_BeneficiaryIdentityMatch',
  'mp_BeneficiaryGroupMembership',
  'mp_BeneficiaryLocationHistory',
];

for (const table of requiredTables) {
  assert(tableNames.has(table), `Missing required beneficiary extension table: ${table}`);
}

assert(!tableNames.has('mp_beneficiary') && !tableNames.has('mp_Beneficiary'), 'Schema must not introduce a TACATDP-only beneficiary identity table.');
assertIncludes(schemaSource, 'mp_TrackedEntity', 'Beneficiary schema must use mp_TrackedEntity as the central identity.');
assertIncludes(schemaSource, 'Lookup:mp_Project', 'Beneficiary extension rows must stay project-scoped.');
assertIncludes(schemaSource, 'Lookup:mp_Submission', 'Beneficiary extension rows must preserve source submission lineage.');
assertIncludes(schemaSource, 'Lookup:mp_VocabularyTerm', 'Technology/training values must support governed vocabulary lookups.');
assertIncludes(schemaSource, 'mp_BeneficiaryIdentityMatch', 'Beneficiary schema must include an identity match review table.');
assertIncludes(schemaSource, 'mp_BeneficiaryGroupMembership', 'Beneficiary schema must include group membership relationships.');
assertIncludes(schemaSource, 'mp_BeneficiaryLocationHistory', 'Beneficiary schema must include location history.');
assertIncludes(schemaSource, 'Lookup:mp_VillageReference', 'Location history must support governed village references.');
assertIncludes(schemaSource, 'must not auto-merge records without review', 'Identity matching must not allow silent fuzzy-match merges.');

for (const table of schema.tables) {
  assert(table.primary_name_column, `${table.name} must define a primary_name_column.`);
  assert(table.ownership === 'UserOrTeam', `${table.name} must use UserOrTeam ownership for project-scoped access.`);
  assert(Array.isArray(table.columns) && table.columns.length > 0, `${table.name} must define columns.`);
  assert(table.columns.some((column) => column.name === table.primary_name_column), `${table.name} must include its primary name column.`);
  assert(table.columns.some((column) => column.name === 'mp_project') || table.name === 'mp_BeneficiarySubmissionLink', `${table.name} must be project scoped or derive scope through submission.`);
}

const relationshipTargets = new Set(schema.relationships.map((relationship) => `${relationship.referenced_table}->${relationship.referencing_table}.${relationship.lookup_column}`));
const directTrackedEntityTables = [
  'mp_BeneficiaryProfile',
  'mp_BeneficiaryProgrammeParticipation',
  'mp_BeneficiaryFinanceLink',
  'mp_BeneficiaryTechnologyAdoption',
  'mp_BeneficiaryTrainingParticipation',
  'mp_BeneficiaryOutcomeSnapshot',
  'mp_BeneficiaryLocationHistory',
];

for (const table of directTrackedEntityTables) {
  assert(
    relationshipTargets.has(`mp_TrackedEntity->${table}.mp_trackedentity`),
    `${table} must relate back to mp_TrackedEntity.`,
  );
}
assert(relationshipTargets.has('mp_Submission->mp_BeneficiarySubmissionLink.mp_submission'), 'Submission link must relate to mp_Submission.');
assert(relationshipTargets.has('mp_Submission->mp_BeneficiaryIdentityMatch.mp_sourcesubmission'), 'Identity match must relate to the source submission.');
assert(relationshipTargets.has('mp_TrackedEntity->mp_BeneficiaryIdentityMatch.mp_candidateentity'), 'Identity match must relate to a candidate tracked entity.');
assert(relationshipTargets.has('mp_TrackedEntity->mp_BeneficiaryGroupMembership.mp_groupentity'), 'Group membership must relate to the group tracked entity.');
assert(relationshipTargets.has('mp_TrackedEntity->mp_BeneficiaryGroupMembership.mp_memberentity'), 'Group membership must relate to the member tracked entity.');
assert(relationshipTargets.has('mp_VillageReference->mp_BeneficiaryLocationHistory.mp_villagereference'), 'Location history must relate to village reference data.');

assertIncludes(planSource, 'Use the existing generic `mp_TrackedEntity`', 'Plan must document the tracked-entity identity decision.');
assertIncludes(planSource, 'No Dataverse environment write', 'Plan must state no environment write is authorized.');
assertIncludes(planSource, 'Prototype-to-Dataverse mapping', 'Plan must include prototype-to-schema mapping.');
assertIncludes(planSource, 'Prototype-to-product boundaries', 'Plan must document prototype-to-product boundaries.');
assertIncludes(planSource, 'mp_BeneficiaryIdentityMatch', 'Plan must document identity match review.');
assertIncludes(planSource, 'mp_BeneficiaryGroupMembership', 'Plan must document group membership modeling.');
assertIncludes(planSource, 'mp_BeneficiaryLocationHistory', 'Plan must document location history modeling.');
assertIncludes(planSource, 'Do not auto-merge beneficiary records from fuzzy matching alone', 'Plan must reject silent fuzzy-match merging.');
assertIncludes(planSource, 'Open questions before environment write', 'Plan must record pre-write open questions.');
assertIncludes(planSource, 'Do not run `dataverse-schema-deploy.py`', 'Plan must preserve the deployment approval gate.');

assertIncludes(prototypeSource, "table: 'mp_TrackedEntity + beneficiary extension tables'", 'Prototype mapping must point to the tracked-entity extension plan.');
assert(!prototypeSource.includes("table: 'mp_beneficiary'"), 'Prototype mapping must not continue to point to mp_beneficiary.');

console.log('Beneficiary entity schema validation passed.');
