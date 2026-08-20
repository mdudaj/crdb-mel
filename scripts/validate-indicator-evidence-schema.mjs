#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const repoRoot = resolve(import.meta.dirname, '..');
const schemaPath = resolve(repoRoot, 'schemas/dataverse/indicator-evidence-schema.json');
const docPath = resolve(repoRoot, 'schemas/dataverse/indicator-evidence-schema.md');
const modelDocPath = resolve(repoRoot, 'docs/powerpages-odk-webforms/prototype-model-design-20260820.md');
const importOrderPath = resolve(repoRoot, 'schemas/dataverse/import-order.md');

const schemaSource = readFileSync(schemaPath, 'utf8');
const docSource = readFileSync(docPath, 'utf8');
const modelDocSource = readFileSync(modelDocPath, 'utf8');
const importOrderSource = readFileSync(importOrderPath, 'utf8');
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

function table(name) {
  return schema.tables.find((candidate) => candidate.name === name);
}

function column(tableName, columnName) {
  const candidate = table(tableName);
  assert(candidate, `Missing table: ${tableName}`);
  return candidate.columns.find((item) => item.name === columnName);
}

function assertColumn(tableName, columnName) {
  assert(column(tableName, columnName), `Missing column ${tableName}.${columnName}`);
}

function assertRelationship(referencedTable, referencingTable, lookupColumn) {
  assert(
    schema.relationships.some(
      (relationship) =>
        relationship.referenced_table === referencedTable &&
        relationship.referencing_table === referencingTable &&
        relationship.lookup_column === lookupColumn,
    ),
    `Missing relationship ${referencedTable}->${referencingTable}.${lookupColumn}`,
  );
}

function assertAlternateKey(tableName, keyName) {
  assert(
    schema.alternate_keys.some((key) => key.table === tableName && key.name === keyName),
    `Missing alternate key ${tableName}.${keyName}`,
  );
}

assert(schema.schema_name === 'indicator_evidence_schema', 'Unexpected schema_name.');
assert(schema.generated_for_review_only === true, 'Indicator/evidence schema must be marked review-only.');
assert(schema.environment_write === false, 'Indicator/evidence schema must explicitly deny environment writes.');
assert(schema.publisher_prefix_placeholder === 'mp', 'Schema must use the mp publisher-prefix placeholder.');

const requiredTables = [
  'mp_IndicatorDefinition',
  'mp_IndicatorResult',
  'mp_DataSourceMapping',
  'mp_Observation',
  'mp_Evidence',
];

for (const tableName of requiredTables) {
  const currentTable = table(tableName);
  assert(currentTable, `Missing required table: ${tableName}`);
  assert(currentTable.ownership === 'UserOrTeam', `${tableName} must use UserOrTeam ownership.`);
  assert(currentTable.primary_name_column, `${tableName} must define primary_name_column.`);
  assertColumn(tableName, currentTable.primary_name_column);
}

for (const forbidden of ['mp_TACATDPIndicator', 'mp_TACATDPEvidence', 'mp_TACATDPObservation']) {
  assert(!schemaSource.includes(forbidden), `Schema must not introduce TACATDP-only table ${forbidden}.`);
}

for (const [tableName, columns] of Object.entries({
  mp_IndicatorDefinition: [
    'mp_code',
    'mp_name',
    'mp_project',
    'mp_indicatortype',
    'mp_unit',
    'mp_formula',
    'mp_numerator',
    'mp_denominator',
    'mp_reportingfrequency',
    'mp_disaggregationjson',
    'mp_verificationmethod',
    'mp_status',
  ],
  mp_DataSourceMapping: [
    'mp_mappingkey',
    'mp_project',
    'mp_indicatordefinition',
    'mp_sourcetype',
    'mp_sourcetable',
    'mp_sourcecolumn',
    'mp_sourcepath',
    'mp_transformrule',
    'mp_required',
    'mp_active',
  ],
  mp_Observation: [
    'mp_observationkey',
    'mp_project',
    'mp_trackedentity',
    'mp_submission',
    'mp_submissionreportrow',
    'mp_datasourcemapping',
    'mp_valuedecimal',
    'mp_valuetext',
    'mp_method',
    'mp_qualitystatus',
    'mp_disaggregationjson',
  ],
  mp_Evidence: [
    'mp_evidencekey',
    'mp_project',
    'mp_observation',
    'mp_indicatorresult',
    'mp_submission',
    'mp_evidencetype',
    'mp_uriorfilereference',
    'mp_hash',
    'mp_verificationstatus',
  ],
  mp_IndicatorResult: [
    'mp_resultkey',
    'mp_project',
    'mp_indicatordefinition',
    'mp_reportingperiod',
    'mp_geography',
    'mp_trackedentity',
    'mp_value',
    'mp_method',
    'mp_verificationstatus',
    'mp_sourcesummaryjson',
    'mp_calculatedat',
    'mp_status',
  ],
})) {
  for (const columnName of columns) {
    assertColumn(tableName, columnName);
  }
}

assertRelationship('mp_Project', 'mp_IndicatorDefinition', 'mp_project');
assertRelationship('mp_IndicatorDefinition', 'mp_DataSourceMapping', 'mp_indicatordefinition');
assertRelationship('mp_Project', 'mp_Observation', 'mp_project');
assertRelationship('mp_TrackedEntity', 'mp_Observation', 'mp_trackedentity');
assertRelationship('mp_Submission', 'mp_Observation', 'mp_submission');
assertRelationship('mp_SubmissionReportRow', 'mp_Observation', 'mp_submissionreportrow');
assertRelationship('mp_DataSourceMapping', 'mp_Observation', 'mp_datasourcemapping');
assertRelationship('mp_Observation', 'mp_Evidence', 'mp_observation');
assertRelationship('mp_IndicatorResult', 'mp_Evidence', 'mp_indicatorresult');
assertRelationship('mp_IndicatorDefinition', 'mp_IndicatorResult', 'mp_indicatordefinition');
assertRelationship('mp_TrackedEntity', 'mp_IndicatorResult', 'mp_trackedentity');

assertAlternateKey('mp_IndicatorDefinition', 'AK_IndicatorDefinition_Project_Code');
assertAlternateKey('mp_DataSourceMapping', 'AK_DataSourceMapping_Key');
assertAlternateKey('mp_Observation', 'AK_Observation_Key');
assertAlternateKey('mp_Evidence', 'AK_Evidence_Key');
assertAlternateKey('mp_IndicatorResult', 'AK_IndicatorResult_Key');

for (const fragment of [
  'Measured',
  'Estimated',
  'Modelled',
  'verification status',
  'canonical form submissions',
  'Power Automate',
  'service-principal',
]) {
  assertIncludes(schemaSource, fragment, `Schema must document ${fragment}.`);
}

for (const fragment of [
  'Status: review-only schema artifact',
  'Do not compute official indicators directly in dashboard components',
  'Do not store secrets',
  'Initial implementation order after approval',
  'Climate outcomes',
  'Repayment and loan performance',
]) {
  assertIncludes(docSource, fragment, `Schema documentation missing required fragment: ${fragment}`);
}

assertIncludes(modelDocSource, 'schemas/dataverse/indicator-evidence-schema.json', 'Model design must reference the indicator/evidence schema JSON.');
assertIncludes(modelDocSource, 'schemas/dataverse/indicator-evidence-schema.md', 'Model design must reference the indicator/evidence schema documentation.');
assertIncludes(importOrderSource, 'indicator-evidence-schema.json', 'Import order must list the indicator/evidence schema artifact.');

console.log('Indicator/evidence schema validation passed.');
