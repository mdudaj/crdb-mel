#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const repoRoot = resolve(import.meta.dirname, '..');
const runbookPath = resolve(repoRoot, 'docs/powerpages-odk-webforms/indicator-evidence-dataverse-implementation-runbook-20260820.md');
const modelDocPath = resolve(repoRoot, 'docs/powerpages-odk-webforms/prototype-model-design-20260820.md');

const runbook = readFileSync(runbookPath, 'utf8');
const modelDoc = readFileSync(modelDocPath, 'utf8');

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertIncludes(source, fragment, message) {
  assert(source.includes(fragment), message);
}

for (const fragment of [
  'Status: approved planning artifact',
  'does not execute Dataverse writes by itself',
  'Do not create tables until the target environment and user/service identity are confirmed immediately before execution',
  'node scripts/validate-indicator-evidence-schema.mjs',
  'python3 scripts/dataverse-schema-plan.py',
  'writes_performed: false',
  'pac auth who',
  'pac env who',
  'pac solution import',
  '--publish-changes',
  'Do not use `--skip-dependency-check`',
  'Do not use `--force-overwrite`',
  'AK_IndicatorDefinition_Project_Code',
  'null key values do not enforce uniqueness',
  'Site settings use table logical names',
  'Browser `/_api` URLs use EntitySetName',
  'explicit fields',
  'Mutating browser calls require CSRF handling',
  'Do not expose `mp_Evidence` to broad browser reads',
  'Avoid portal writes to these tables for the first implementation',
  'approved Power Automate ownership',
  'approved application user/service principal',
  'Do not retry with `--force-overwrite` immediately',
]) {
  assertIncludes(runbook, fragment, `Runbook missing required fragment: ${fragment}`);
}

for (const tableName of [
  'mp_IndicatorDefinition',
  'mp_DataSourceMapping',
  'mp_Observation',
  'mp_IndicatorResult',
  'mp_Evidence',
]) {
  assertIncludes(runbook, tableName, `Runbook missing table: ${tableName}`);
}

for (const forbidden of [
  'Webapi/mp_evidence/fields=*',
  'Webapi/mp_indicatorresult/fields=*',
  'mp_TACATDPIndicator',
  'mp_TACATDPEvidence',
]) {
  assert(!runbook.includes(forbidden), `Runbook contains forbidden fragment: ${forbidden}`);
}

assertIncludes(modelDoc, 'indicator-evidence-dataverse-implementation-runbook-20260820.md', 'Model design must link to the implementation runbook.');

console.log('Indicator/evidence implementation runbook validation passed.');
