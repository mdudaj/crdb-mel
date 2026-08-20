#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const repoRoot = resolve(import.meta.dirname, '..');
const docPath = resolve(repoRoot, 'docs/powerpages-odk-webforms/prototype-model-design-20260820.md');
const source = readFileSync(docPath, 'utf8');

function assertIncludes(fragment, message) {
  if (!source.includes(fragment)) {
    throw new Error(message);
  }
}

for (const fragment of [
  'Canonical form submissions remain the evidence source',
  'Beneficiary and dashboard records are projections',
  'mp_SubmissionVersion',
  'mp_SubmissionReportRow',
  'mp_TrackedEntity',
  'mp_EntityIdentifier',
  'mp_BeneficiaryProfile',
  'mp_BeneficiarySubmissionLink',
  'mp_IndicatorDefinition',
  'mp_IndicatorResult',
  'Baseline-supported projection',
  'Demonstration data',
  'Not available',
  'Repayment rate',
  'No repayment performance or NPL status fields',
  'True training sessions',
  'Baseline has trained people and training types',
  'do not auto-merge',
  'method and verification status',
  'Power BI should read reporting/indicator projection tables',
]) {
  assertIncludes(fragment, `Prototype model design is missing required fragment: ${fragment}`);
}

if (/TACATDP-only beneficiary table/i.test(source) && !source.includes('not a TACATDP-only beneficiary table')) {
  throw new Error('Model design must reject TACATDP-only beneficiary identity tables.');
}

console.log('Prototype model design validation passed.');
