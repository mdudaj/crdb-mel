#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const dashboardPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/TacatdpDashboardPage.vue');
const beneficiariesPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/BeneficiariesView.vue');
const shellPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');

const dashboardSource = readFileSync(dashboardPath, 'utf8');
const beneficiariesSource = readFileSync(beneficiariesPath, 'utf8');
const shellSource = readFileSync(shellPath, 'utf8');

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

assertIncludes(shellSource, ".split('?')[0].split('/')[0]", 'Shell route parser must strip beneficiary query strings before resolving the active route.');

assertIncludes(dashboardSource, 'function openBeneficiaries(filters: Record<string, string>)', 'Dashboard must use a single drill-through helper.');
assertIncludes(dashboardSource, "new URLSearchParams({ source: 'dashboard', ...filters })", 'Dashboard drill-through must preserve source metadata in the URL.');
assertIncludes(dashboardSource, "`#/beneficiaries?${params.toString()}`", 'Dashboard drill-through must navigate to the beneficiaries route with URL filters.');
assertIncludes(dashboardSource, "borrowerStatus: 'Active borrower'", 'Active Borrowers KPI must drill into active borrower records.');
assertIncludes(dashboardSource, "trained: 'true'", 'Farmers Trained KPI must drill into trained beneficiary records.');
assertIncludes(dashboardSource, "@click=\"openBeneficiaries({ region: selectedRegion.name })\"", 'Selected map-region card must drill into region-filtered beneficiaries.');
assertIncludes(dashboardSource, '@click="openTechnologyBeneficiaries"', 'Technology chart clicks must drill into technology-filtered beneficiaries.');
assertIncludes(dashboardSource, "technology: itemParams.name", 'Technology drill-through must pass the selected chart item as a URL filter.');
assertIncludes(dashboardSource, "submissionStatus: submission.status", 'Submission rows must pass the submission status as a URL filter.');
assertIncludes(dashboardSource, "region: regionNameFromSubmission(submission.region)", 'Submission rows must pass the normalized region as a URL filter.');
assertPattern(dashboardSource, /kpi-card--clickable[\s\S]*@keydown\.enter\.prevent="openKpiDetail\(metric\)"/, 'Clickable KPI cards must remain keyboard accessible.');

assertIncludes(beneficiariesSource, 'function readBeneficiaryHashFilters()', 'Beneficiaries route must parse URL filters on entry.');
assertIncludes(beneficiariesSource, 'function syncBeneficiaryHashFilters()', 'Beneficiaries route must keep active filters in the URL.');
assertIncludes(beneficiariesSource, 'new URLSearchParams(query)', 'Beneficiaries route must parse URL query parameters.');
assertIncludes(beneficiariesSource, "params.set('borrowerStatus', activeBorrowerStatus.value)", 'Borrower-status filter must be persisted in the URL.');
assertIncludes(beneficiariesSource, "params.set('trained', activeTraining.value === 'Trained' ? 'true' : 'false')", 'Training filter must be persisted as a URL parameter.');
assertIncludes(beneficiariesSource, "params.set('technology', activeTechnology.value)", 'Technology filter must be persisted in the URL.');
assertIncludes(beneficiariesSource, "params.set('submissionStatus', activeSubmissionStatus.value)", 'Submission-status filter must be persisted in the URL.');
assertIncludes(beneficiariesSource, 'Opened from dashboard', 'Beneficiaries route must show visible dashboard drill-through context.');
assertIncludes(beneficiariesSource, 'Back to Dashboard', 'Beneficiaries route must provide a dashboard return action when opened from dashboard drill-through.');
assertIncludes(beneficiariesSource, "Technology: ${activeTechnology.value}", 'Active filter chips must expose technology drill-through state.');
assertIncludes(beneficiariesSource, "Borrower: ${activeBorrowerStatus.value}", 'Active filter chips must expose borrower drill-through state.');
assertIncludes(beneficiariesSource, "Training: ${activeTraining.value}", 'Active filter chips must expose training drill-through state.');
assertIncludes(beneficiariesSource, "Submission: ${activeSubmissionStatus.value}", 'Active filter chips must expose submission drill-through state.');
assertIncludes(beneficiariesSource, 'technologyMatches(record, activeTechnology.value)', 'Beneficiaries filtering must match URL technology filters against beneficiary technology relationships.');
assertIncludes(beneficiariesSource, "window.addEventListener('hashchange', readBeneficiaryHashFilters)", 'Beneficiaries route must update filters when hash navigation changes.');
assertIncludes(beneficiariesSource, "window.removeEventListener('hashchange', readBeneficiaryHashFilters)", 'Beneficiaries route must clean up the hash listener.');

console.log('Dashboard beneficiary drill-through validation passed.');
