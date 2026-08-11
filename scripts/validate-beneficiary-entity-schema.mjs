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
];

for (const table of requiredTables) {
  assert(tableNames.has(table), `Missing required beneficiary extension table: ${table}`);
}

assert(!tableNames.has('mp_beneficiary') && !tableNames.has('mp_Beneficiary'), 'Schema must not introduce a TACATDP-only beneficiary identity table.');
assertIncludes(schemaSource, 'mp_TrackedEntity', 'Beneficiary schema must use mp_TrackedEntity as the central identity.');
assertIncludes(schemaSource, 'Lookup:mp_Project', 'Beneficiary extension rows must stay project-scoped.');
assertIncludes(schemaSource, 'Lookup:mp_Submission', 'Beneficiary extension rows must preserve source submission lineage.');
assertIncludes(schemaSource, 'Lookup:mp_VocabularyTerm', 'Technology/training values must support governed vocabulary lookups.');

for (const table of schema.tables) {
  assert(table.primary_name_column, `${table.name} must define a primary_name_column.`);
  assert(table.ownership === 'UserOrTeam', `${table.name} must use UserOrTeam ownership for project-scoped access.`);
  assert(Array.isArray(table.columns) && table.columns.length > 0, `${table.name} must define columns.`);
  assert(table.columns.some((column) => column.name === table.primary_name_column), `${table.name} must include its primary name column.`);
  assert(table.columns.some((column) => column.name === 'mp_project') || table.name === 'mp_BeneficiarySubmissionLink', `${table.name} must be project scoped or derive scope through submission.`);
}

const relationshipTargets = new Set(schema.relationships.map((relationship) => `${relationship.referenced_table}->${relationship.referencing_table}.${relationship.lookup_column}`));
for (const table of requiredTables) {
  if (table === 'mp_BeneficiarySubmissionLink') continue;
  assert(
    relationshipTargets.has(`mp_TrackedEntity->${table}.mp_trackedentity`),
    `${table} must relate back to mp_TrackedEntity.`,
  );
}
assert(relationshipTargets.has('mp_Submission->mp_BeneficiarySubmissionLink.mp_submission'), 'Submission link must relate to mp_Submission.');

assertIncludes(planSource, 'Use the existing generic `mp_TrackedEntity`', 'Plan must document the tracked-entity identity decision.');
assertIncludes(planSource, 'No Dataverse environment write', 'Plan must state no environment write is authorized.');
assertIncludes(planSource, 'Prototype-to-Dataverse mapping', 'Plan must include prototype-to-schema mapping.');
assertIncludes(planSource, 'Open questions before environment write', 'Plan must record pre-write open questions.');
assertIncludes(planSource, 'Do not run `dataverse-schema-deploy.py`', 'Plan must preserve the deployment approval gate.');

assertIncludes(prototypeSource, "table: 'mp_TrackedEntity + beneficiary extension tables'", 'Prototype mapping must point to the tracked-entity extension plan.');
assert(!prototypeSource.includes("table: 'mp_beneficiary'"), 'Prototype mapping must not continue to point to mp_beneficiary.');

console.log('Beneficiary entity schema validation passed.');
