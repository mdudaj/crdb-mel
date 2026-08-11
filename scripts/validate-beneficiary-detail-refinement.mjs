#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const viewPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/BeneficiariesView.vue');
const packagePath = resolve(repoRoot, 'powerpages/webforms-spa/package.json');

const viewSource = readFileSync(viewPath, 'utf8');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));

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

assertIncludes(viewSource, "const hasDashboardContext = computed(() => drillthroughSource.value === 'dashboard')", 'Beneficiaries view must centralize dashboard-origin state.');
assertIncludes(viewSource, 'const filterSummary = computed(() => activeFilters.value.map((filter) => filter.label).join', 'Beneficiaries view must summarize active filters for drill-through review.');
assertIncludes(viewSource, 'function backToDashboard()', 'Beneficiaries view must expose a dashboard return action.');
assertIncludes(viewSource, "window.location.hash = '#/dashboard'", 'Dashboard return action must route back to the dashboard.');
assertIncludes(viewSource, 'function openAllBeneficiaries()', 'Empty dashboard drill-through state must offer an all-records recovery path.');

assertIncludes(viewSource, 'aria-label="Dashboard drill-through context"', 'Dashboard drill-through context must be semantically labelled.');
assertIncludes(viewSource, 'Opened from dashboard', 'Dashboard drill-through context must be visible in plain language.');
assertIncludes(viewSource, 'Back to Dashboard', 'Dashboard drill-through context must include a return action.');
assertIncludes(viewSource, 'Dashboard drill-through filters:', 'No-data state must show the exact dashboard drill-through filters.');
assertIncludes(viewSource, 'Open all beneficiaries', 'No-data state must offer a non-misleading recovery action.');

assertIncludes(viewSource, 'class="beneficiary-detail-tags"', 'Beneficiary detail header must show structured identity tags.');
assertIncludes(viewSource, 'aria-label="Beneficiary identity summary"', 'Beneficiary detail identity tags must be labelled for assistive technology.');
for (const heading of ['Profile', 'Finance', 'Technology', 'Training', 'Outcomes', 'Data lineage', 'Technical Dataverse mapping']) {
  assertPattern(viewSource, new RegExp(`<h3>${heading}</h3>`), `Beneficiary detail drawer must include the ${heading} section.`);
}

assertIncludes(viewSource, 'beneficiary-detail-list--nested', 'Programme participation must be grouped under Profile instead of isolated as a competing drawer section.');
assertIncludes(viewSource, 'Demonstration detail, not official statistics', 'Beneficiary detail drawer must preserve prototype data disclosure.');
assertIncludes(viewSource, 'mp_BeneficiarySubmissionLink', 'Data lineage must keep the future Dataverse submission relationship visible.');

if (!packageJson.scripts?.['test:material']?.includes('validate-beneficiary-detail-refinement.mjs')) {
  throw new Error('test:material must run the beneficiary detail refinement validator.');
}

console.log('Beneficiary detail refinement validation passed.');
