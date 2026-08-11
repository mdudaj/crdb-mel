#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const viewPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/BeneficiariesView.vue');
const shellPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');
const dataPath = resolve(repoRoot, 'powerpages/webforms-spa/src/prototype/beneficiaries.ts');

const viewSource = readFileSync(viewPath, 'utf8');
const shellSource = readFileSync(shellPath, 'utf8');
const dataSource = readFileSync(dataPath, 'utf8');

function assertIncludes(source, fragment, message) {
  if (!source.includes(fragment)) {
    throw new Error(message);
  }
}

function assertPattern(source, pattern, message) {
  if (!pattern.test(source)) {
    throw new Error(message);
  }
}

assertIncludes(shellSource, "type AppView = 'dashboard' | 'workspace' | 'projects' | 'beneficiaries'", 'Shell AppView must include a dedicated beneficiaries route.');
assertIncludes(shellSource, "activeView === 'beneficiaries'", 'Side navigation or content switch must mark/open the beneficiaries route.');
assertIncludes(shellSource, '<BeneficiariesView />', 'Shell must render BeneficiariesView for the beneficiaries route.');
assertIncludes(shellSource, "return 'beneficiaries';", 'Hash route parsing must support #/beneficiaries.');

assertIncludes(viewSource, 'role="search"', 'Beneficiaries filters must expose a search landmark.');
assertIncludes(viewSource, 'Search beneficiaries', 'Search control must have a visible label.');
assertIncludes(viewSource, '<table class="beneficiary-table" aria-label="Beneficiary records">', 'Desktop record surface must use a semantic table with an accessible label.');
assertIncludes(viewSource, '<thead>', 'Beneficiary table must include a table header.');
assertIncludes(viewSource, '<tbody>', 'Beneficiary table must include a table body.');
assertPattern(viewSource, /<th scope="col">Beneficiary<\/th>[\s\S]*<th scope="col">Location<\/th>[\s\S]*<th scope="col">Borrower status<\/th>/, 'Beneficiary table must use scoped column headers for scanability.');
assertIncludes(viewSource, 'beneficiary-status-chip', 'Verification status must be rendered as a text status chip.');
assertIncludes(viewSource, 'Prototype data only', 'Prototype figures must be explicitly labelled as non-official demonstration data.');
assertIncludes(viewSource, 'No data for the selected filters', 'List must provide an explicit empty state.');
assertIncludes(viewSource, 'beneficiary-card-list', 'Mobile layout must provide a stacked record-card fallback.');
assertPattern(viewSource, /@media \(max-width: 760px\)[\s\S]*\.beneficiary-table-wrap\s*{\s*display: none;/, 'Responsive rule must hide the desktop table on narrow screens.');
assertPattern(viewSource, /@media \(max-width: 760px\)[\s\S]*\.beneficiary-card-list\s*{\s*display: grid;/, 'Responsive rule must show record cards on narrow screens.');
assertPattern(dataSource, /export const beneficiaryRecords: BeneficiaryRecord\[] = \[[\s\S]*BEN-/, 'Prototype beneficiary data must live in a separate structured data file.');

if (/official CRDB Bank or Green Climate Fund statistics/.test(dataSource)) {
  throw new Error('Official-statistics disclaimer belongs in UI/documentation, not inside prototype data values.');
}

console.log('Beneficiaries Material list validation passed.');
