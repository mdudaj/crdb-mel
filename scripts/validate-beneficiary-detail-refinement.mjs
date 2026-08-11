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

function assertBefore(source, first, second, message) {
  const firstIndex = source.indexOf(first);
  const secondIndex = source.indexOf(second);
  if (firstIndex === -1 || secondIndex === -1 || firstIndex > secondIndex) {
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
assertIncludes(viewSource, 'class="material-detail-surface beneficiary-detail-drawer"', 'Beneficiary detail drawer must use the shared Material detail surface abstraction.');
assertIncludes(viewSource, 'class="material-detail-header beneficiary-detail-header beneficiary-detail-header--structured"', 'Beneficiary detail header must use the shared Material detail header abstraction.');
assertIncludes(viewSource, 'class="material-detail-section beneficiary-detail-section"', 'Beneficiary detail sections must use the shared Material detail section abstraction.');
assertIncludes(viewSource, 'class="material-detail-list beneficiary-detail-grid"', 'Beneficiary detail grids must use the shared Material detail list abstraction.');
assertIncludes(viewSource, 'class="material-detail-row"', 'Beneficiary detail fields must use the shared Material detail row abstraction.');
assertIncludes(viewSource, 'aria-label="Beneficiary identity summary"', 'Beneficiary detail identity tags must be labelled for assistive technology.');
for (const heading of ['Profile', 'Record matching', 'Group/member links', 'Finance', 'Technology', 'Training', 'Outcomes', 'Data lineage', 'Location history']) {
  assertPattern(viewSource, new RegExp(`<h3>${heading}</h3>`), `Beneficiary detail drawer must include the ${heading} section.`);
}
for (const [first, second] of [
  ['<h3>Profile</h3>', '<h3>Finance</h3>'],
  ['<h3>Finance</h3>', '<h3>Technology</h3>'],
  ['<h3>Technology</h3>', '<h3>Training</h3>'],
  ['<h3>Training</h3>', '<h3>Outcomes</h3>'],
  ['<h3>Outcomes</h3>', '<h3>Data lineage</h3>'],
  ['<h3>Data lineage</h3>', '<h3>Record matching</h3>'],
  ['<h3>Record matching</h3>', '<h3>Group/member links</h3>'],
  ['<h3>Group/member links</h3>', '<h3>Location history</h3>'],
  ['<h3>Location history</h3>', '<summary>Technical mapping</summary>'],
]) {
  assertBefore(viewSource, first, second, `Beneficiary detail drawer must keep ${first} before ${second}.`);
}

assertIncludes(viewSource, '<summary>Technical mapping</summary>', 'Technical mapping must be hidden behind a compact disclosure summary.');
assertIncludes(viewSource, 'beneficiary-detail-section--technical[open] summary::after', 'Technical mapping disclosure must expose open/closed state text.');
if (viewSource.includes('beneficiary-detail-section--accented') || viewSource.includes('beneficiary-detail-segment')) {
  throw new Error('Beneficiary detail drawer must use one visible Material section container per detail block, with no extra segment wrappers or left shade accent rails.');
}
if (viewSource.includes('<h3>Technical Dataverse mapping</h3>')) {
  throw new Error('Technical Dataverse mapping must not remain as an always-visible drawer section heading.');
}
if (viewSource.includes('<h3>Identity governance</h3>') || viewSource.includes('<h3>Group membership</h3>')) {
  throw new Error('Beneficiary model sections must use business-friendly labels.');
}

assertIncludes(viewSource, 'beneficiary-detail-list--nested', 'Programme participation must be grouped under Profile instead of isolated as a competing drawer section.');
assertIncludes(viewSource, 'Demonstration detail, not official statistics', 'Beneficiary detail drawer must preserve prototype data disclosure.');
const businessDetailStart = viewSource.indexOf('Demonstration detail, not official statistics');
const technicalMappingStart = viewSource.indexOf('<summary>Technical mapping</summary>');
const beforeTechnicalMapping = viewSource.slice(businessDetailStart, technicalMappingStart);
if (businessDetailStart === -1 || technicalMappingStart === -1 || beforeTechnicalMapping.includes('mp_') || beforeTechnicalMapping.includes('<dt>Model target</dt>')) {
  throw new Error('Business-facing beneficiary detail sections must not expose Dataverse table names or model-target rows.');
}
assertIncludes(viewSource, 'mp_BeneficiarySubmissionLink', 'Technical mapping must keep the future Dataverse submission relationship visible.');
assertIncludes(viewSource, 'mp_BeneficiaryIdentityMatch', 'Technical mapping must keep the future Dataverse identity-match relationship visible.');
assertIncludes(viewSource, 'mp_BeneficiaryGroupMembership', 'Technical mapping must keep the future Dataverse group-membership relationship visible.');
assertIncludes(viewSource, 'mp_BeneficiaryLocationHistory', 'Technical mapping must keep the future Dataverse location-history relationship visible.');
assertIncludes(viewSource, 'No reviewer decision recorded', 'Record matching must have a clear fallback state for records not yet reviewed.');
assertIncludes(viewSource, 'No member linkage in prototype data', 'Group/member links must have a clear fallback state for records not yet modelled.');
assertIncludes(viewSource, 'Production location changes keep the current dashboard location usable without losing historical evidence.', 'Location history must explain current-location versus historical evidence without Dataverse table names.');

if (!packageJson.scripts?.['test:material']?.includes('validate-beneficiary-detail-refinement.mjs')) {
  throw new Error('test:material must run the beneficiary detail refinement validator.');
}

console.log('Beneficiary detail refinement validation passed.');
