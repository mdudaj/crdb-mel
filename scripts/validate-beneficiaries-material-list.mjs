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
assertIncludes(viewSource, "import SurfaceCard from '../components/ui/SurfaceCard.vue';", 'Beneficiaries page must use the shared SurfaceCard abstraction.');
assertIncludes(viewSource, '<SurfaceCard as="section" class="beneficiaries-hero">', 'Beneficiaries hero must use a plain SurfaceCard without the metric accent rail.');
assertIncludes(viewSource, 'as="article" accent="green" accented class="beneficiary-metric"', 'Beneficiary summary metrics must opt into the metric accent rail.');
assertIncludes(viewSource, '<SurfaceCard as="section" class="beneficiary-list"', 'Beneficiary list surface must use a plain SurfaceCard without the metric accent rail.');
assertIncludes(viewSource, 'class="beneficiary-metric"', 'Beneficiary summary metrics must use shared card styling.');
assertIncludes(viewSource, 'class="beneficiary-list"', 'Beneficiary list surface must use shared card styling.');
assertIncludes(viewSource, 'Search beneficiaries', 'Search control must have a visible label.');
assertIncludes(viewSource, '<table class="beneficiary-table" aria-label="Beneficiary records">', 'Desktop record surface must use a semantic table with an accessible label.');
assertIncludes(viewSource, '<thead>', 'Beneficiary table must include a table header.');
assertIncludes(viewSource, '<tbody>', 'Beneficiary table must include a table body.');
assertPattern(viewSource, /<th scope="col">Beneficiary<\/th>[\s\S]*<th scope="col">Location<\/th>[\s\S]*<th scope="col">Borrower status<\/th>/, 'Beneficiary table must use scoped column headers for scanability.');
assertIncludes(viewSource, '<th scope="col">Actions</th>', 'Beneficiary table must expose a clear details action column.');
assertIncludes(viewSource, 'View details', 'Beneficiary records must provide a details action.');
assertIncludes(viewSource, 'beneficiary-detail-drawer', 'Beneficiary details must open in a dedicated drawer.');
assertIncludes(viewSource, 'role="dialog"', 'Beneficiary details drawer must use dialog semantics.');
assertIncludes(viewSource, 'aria-modal="true"', 'Beneficiary details drawer must be marked modal for assistive technology.');
assertIncludes(viewSource, 'Demonstration detail, not official statistics', 'Beneficiary detail drawer must label values as demonstration data.');
assertIncludes(viewSource, 'reviewed Dataverse-ready entity shape', 'Beneficiary detail drawer must align with the reviewed schema plan.');
assertIncludes(viewSource, 'Data lineage', 'Beneficiary detail drawer must expose source submission lineage.');
assertIncludes(viewSource, 'Dataverse mapping', 'Beneficiary detail drawer must document the reviewed Dataverse mapping.');
assertIncludes(viewSource, 'beneficiaryDataverseTargets', 'Beneficiary detail drawer must use an explicit Dataverse target list.');
assertIncludes(viewSource, 'mp_TrackedEntity', 'Beneficiary detail drawer must show the central tracked entity target.');
assertIncludes(viewSource, 'mp_BeneficiaryProfile', 'Beneficiary detail drawer must show the profile extension target.');
assertIncludes(viewSource, 'mp_BeneficiaryProgrammeParticipation', 'Beneficiary detail drawer must show the participation extension target.');
assertIncludes(viewSource, 'mp_BeneficiaryFinanceLink', 'Beneficiary detail drawer must show the finance extension target.');
assertIncludes(viewSource, 'mp_BeneficiaryTechnologyAdoption', 'Beneficiary detail drawer must show the technology extension target.');
assertIncludes(viewSource, 'mp_BeneficiaryTrainingParticipation', 'Beneficiary detail drawer must show the training extension target.');
assertIncludes(viewSource, 'mp_BeneficiaryOutcomeSnapshot', 'Beneficiary detail drawer must show the outcome extension target.');
assertIncludes(viewSource, 'mp_BeneficiarySubmissionLink', 'Beneficiary detail drawer must show the submission-lineage extension target.');
if (viewSource.includes('Future Dataverse mapping')) {
  throw new Error('Beneficiary detail drawer must not use stale Future Dataverse mapping wording after schema review.');
}
assertIncludes(viewSource, 'beneficiary-detail-scrim', 'Beneficiary detail drawer must provide a scrim close target.');
assertIncludes(viewSource, 'beneficiary-status-chip', 'Verification status must be rendered as a text status chip.');
assertIncludes(viewSource, 'Prototype data only', 'Prototype figures must be explicitly labelled as non-official demonstration data.');
assertIncludes(viewSource, 'No data for the selected filters', 'List must provide an explicit empty state.');
assertIncludes(viewSource, 'beneficiary-card-list', 'Mobile layout must provide a stacked record-card fallback.');
assertPattern(viewSource, /@media \(max-width: 760px\)[\s\S]*\.beneficiary-table-wrap\s*{\s*display: none;/, 'Responsive rule must hide the desktop table on narrow screens.');
assertPattern(viewSource, /@media \(max-width: 760px\)[\s\S]*\.beneficiary-card-list\s*{\s*display: grid;/, 'Responsive rule must show record cards on narrow screens.');
assertPattern(dataSource, /export const beneficiaryRecords: BeneficiaryRecord\[] = \[[\s\S]*BEN-/, 'Prototype beneficiary data must live in a separate structured data file.');
assertIncludes(dataSource, 'projectParticipation', 'Prototype beneficiary entity must include programme participation data.');
assertIncludes(dataSource, 'finance:', 'Prototype beneficiary entity must include finance snapshot data.');
assertIncludes(dataSource, 'technologiesFinanced', 'Prototype beneficiary entity must include financed technology relationships.');
assertIncludes(dataSource, 'trainingSummary', 'Prototype beneficiary entity must include training summary data.');
assertIncludes(dataSource, 'latestSubmission', 'Prototype beneficiary entity must include latest submission state.');
assertIncludes(dataSource, 'outcomeSnapshot', 'Prototype beneficiary entity must include monitored outcome data.');
assertIncludes(dataSource, 'futureDataverseMapping', 'Prototype beneficiary entity must include future Dataverse mapping notes.');

const surfaceCardPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/ui/SurfaceCard.vue');
const surfaceCardSource = readFileSync(surfaceCardPath, 'utf8');
assertIncludes(surfaceCardSource, 'accented?: boolean;', 'Shared SurfaceCard must make the accent rail opt-in.');
assertIncludes(surfaceCardSource, '.surface-card--accented::before', 'Shared SurfaceCard must render the rail only when accented is true.');
assertIncludes(surfaceCardSource, '--surface-card-accent', 'Shared SurfaceCard must expose an accent token.');
if (surfaceCardSource.includes('.surface-card::before')) {
  throw new Error('Shared SurfaceCard must not shade every card; use .surface-card--accented::before only.');
}

if (/official CRDB Bank or Green Climate Fund statistics/.test(dataSource)) {
  throw new Error('Official-statistics disclaimer belongs in UI/documentation, not inside prototype data values.');
}

console.log('Beneficiaries Material list validation passed.');
