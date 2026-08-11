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
assertIncludes(viewSource, 'class="material-detail-surface beneficiary-detail-drawer"', 'Beneficiary detail drawer must use the shared Material detail surface abstraction.');
assertIncludes(viewSource, 'class="material-detail-header beneficiary-detail-header beneficiary-detail-header--structured"', 'Beneficiary detail header must use the shared Material detail header abstraction.');
assertIncludes(viewSource, 'class="material-detail-section beneficiary-detail-section"', 'Beneficiary detail sections must use the shared Material detail section abstraction.');
assertIncludes(viewSource, 'class="beneficiary-detail-segment"', 'Beneficiary detail drawer must group related cards into internal segment containers.');
assertIncludes(viewSource, 'class="material-detail-list beneficiary-detail-grid"', 'Beneficiary detail grids must use the shared Material detail list abstraction.');
assertIncludes(viewSource, 'class="material-detail-row"', 'Beneficiary detail fields must use the shared Material detail row abstraction.');
assertIncludes(viewSource, 'aria-label="Beneficiary identity summary"', 'Beneficiary detail identity tags must be labelled for assistive technology.');
for (const segment of ['Profile and participation', 'Beneficiary model', 'Programme delivery', 'Evidence and location']) {
  assertIncludes(viewSource, `aria-label="${segment}"`, `Beneficiary detail drawer must group detail cards under the ${segment} segment.`);
}
for (const heading of ['Profile', 'Record matching', 'Group/member links', 'Finance', 'Technology', 'Training', 'Outcomes', 'Data lineage', 'Location history']) {
  assertPattern(viewSource, new RegExp(`<h3>${heading}</h3>`), `Beneficiary detail drawer must include the ${heading} section.`);
}

assertIncludes(viewSource, '<summary>Technical mapping</summary>', 'Technical mapping must be hidden behind a compact disclosure summary.');
assertIncludes(viewSource, 'beneficiary-detail-section--technical[open] summary::after', 'Technical mapping disclosure must expose open/closed state text.');
if (viewSource.includes('beneficiary-detail-section--accented') || viewSource.includes('beneficiary-detail-segment--accented')) {
  throw new Error('Beneficiary detail drawer must not use left shade accent rails on sections or segment containers.');
}
if (/beneficiary-detail-segment[^{]*::before/.test(viewSource)) {
  throw new Error('Beneficiary detail segment containers must not render a left shade pseudo-element.');
}
if (viewSource.includes('<h3>Technical Dataverse mapping</h3>')) {
  throw new Error('Technical Dataverse mapping must not remain as an always-visible drawer section heading.');
}
if (viewSource.includes('<h3>Identity governance</h3>') || viewSource.includes('<h3>Group membership</h3>')) {
  throw new Error('Beneficiary model sections must use business-friendly labels.');
}

assertIncludes(viewSource, 'beneficiary-detail-list--nested', 'Programme participation must be grouped under Profile instead of isolated as a competing drawer section.');
assertIncludes(viewSource, 'Demonstration detail, not official statistics', 'Beneficiary detail drawer must preserve prototype data disclosure.');
assertIncludes(viewSource, 'mp_BeneficiarySubmissionLink', 'Data lineage must keep the future Dataverse submission relationship visible.');
assertIncludes(viewSource, 'mp_BeneficiaryIdentityMatch', 'Record matching must expose the future Dataverse identity-match relationship.');
assertIncludes(viewSource, 'mp_BeneficiaryGroupMembership', 'Group/member links must expose the future Dataverse group-membership relationship.');
assertIncludes(viewSource, 'mp_BeneficiaryLocationHistory', 'Location history must expose the future Dataverse location-history relationship.');
assertIncludes(viewSource, 'No reviewer decision recorded', 'Record matching must have a clear fallback state for records not yet reviewed.');
assertIncludes(viewSource, 'No member linkage in prototype data', 'Group/member links must have a clear fallback state for records not yet modelled.');
assertIncludes(viewSource, 'Production location changes are stored in mp_BeneficiaryLocationHistory', 'Location history must explain current-location versus historical evidence.');

if (!packageJson.scripts?.['test:material']?.includes('validate-beneficiary-detail-refinement.mjs')) {
  throw new Error('test:material must run the beneficiary detail refinement validator.');
}

console.log('Beneficiary detail refinement validation passed.');
