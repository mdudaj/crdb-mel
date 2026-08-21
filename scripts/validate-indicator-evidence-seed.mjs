#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const repoRoot = resolve(import.meta.dirname, '..');
const seedPath = resolve(repoRoot, 'schemas/dataverse/indicator-evidence-seed.json');
const seed = JSON.parse(readFileSync(seedPath, 'utf8'));

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

assert(seed.seed_name === 'tacatdp_indicator_evidence_seed', 'Unexpected seed name.');
assert(seed.target_environment === 'Mshirika development', 'Seed must target Mshirika development.');
assert(seed.target_project_code === 'TACATDP', 'Seed must target TACATDP.');
assert(Array.isArray(seed.writes_only), 'writes_only must be present.');
assert(seed.writes_only.length === 2, 'Seed must write only two tables.');
assert(seed.writes_only.includes('mp_IndicatorDefinition'), 'Seed must write indicator definitions.');
assert(seed.writes_only.includes('mp_DataSourceMapping'), 'Seed must write data source mappings.');

const definitions = seed.indicator_definitions;
assert(Array.isArray(definitions), 'indicator_definitions must be an array.');
assert(definitions.length === 5, 'Expected exactly five first-pass indicators.');

const expectedCodes = ['TAC-BEN-001', 'TAC-FIN-001', 'TAC-REG-001', 'TAC-TEC-001', 'TAC-TRN-001'];
const actualCodes = definitions.map((definition) => definition.code);
for (const code of expectedCodes) {
  assert(actualCodes.includes(code), `Missing indicator ${code}.`);
}
assert(new Set(actualCodes).size === actualCodes.length, 'Indicator codes must be unique.');

const allowedTypes = new Set(['Financial', 'Output', 'Outcome', 'ClimateImpactEstimate', 'OperationalDataQuality']);
const allowedLevels = new Set(['Programme', 'Component', 'Outcome', 'Output', 'Activity', 'Operational']);
const allowedFrequencies = new Set(['OnDemand', 'Weekly', 'Monthly', 'Quarterly', 'Seasonal', 'Annual', 'Baseline', 'Endline']);

const mappingKeys = new Set();
for (const definition of definitions) {
  assert(definition.name && definition.name.length <= 100, `${definition.code} needs a concise name.`);
  assert(definition.description, `${definition.code} needs a description.`);
  assert(allowedTypes.has(definition.indicator_type), `${definition.code} has invalid indicator_type.`);
  assert(allowedLevels.has(definition.result_level), `${definition.code} has invalid result_level.`);
  assert(allowedFrequencies.has(definition.reporting_frequency), `${definition.code} has invalid reporting_frequency.`);
  assert(definition.unit, `${definition.code} needs a unit.`);
  assert(definition.formula, `${definition.code} needs a formula.`);
  assert(definition.verification_method, `${definition.code} needs a verification method.`);
  assert(definition.status === 'Active', `${definition.code} must be Active for seed.`);
  assert(Array.isArray(definition.disaggregation), `${definition.code} disaggregation must be an array.`);
  assert(Array.isArray(definition.mappings), `${definition.code} mappings must be an array.`);
  assert(definition.mappings.length >= 1, `${definition.code} needs at least one mapping.`);
  for (const mapping of definition.mappings) {
    assert(mapping.mapping_key?.startsWith(`${definition.code}:`), `${definition.code} mapping key must be indicator-scoped.`);
    assert(!mappingKeys.has(mapping.mapping_key), `Duplicate mapping key ${mapping.mapping_key}.`);
    mappingKeys.add(mapping.mapping_key);
    assert(mapping.source_type, `${mapping.mapping_key} needs source_type.`);
    assert(mapping.transform_rule, `${mapping.mapping_key} needs transform_rule.`);
    assert(typeof mapping.required === 'boolean', `${mapping.mapping_key} required must be boolean.`);
    assert(mapping.active === true, `${mapping.mapping_key} must be active.`);
  }
}

for (const forbidden of ['mp_Observation', 'mp_Evidence', 'mp_IndicatorResult']) {
  assert(!seed.writes_only.includes(forbidden), `Seed must not write ${forbidden}.`);
}

console.log('Indicator evidence seed validation passed.');
