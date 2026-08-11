<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { Eye, Filter, Search, SlidersHorizontal, Users, X } from '@lucide/vue';
import SurfaceCard from '../components/ui/SurfaceCard.vue';
import { beneficiaryRecords, type BeneficiaryRecord } from '../prototype/beneficiaries';

const searchTerm = ref('');
const activeRegion = ref('All regions');
const activeVerification = ref('All statuses');
const activeBorrowerStatus = ref('All borrower statuses');
const activeTraining = ref('All training states');
const activeTechnology = ref('All technologies');
const activeSubmissionStatus = ref('All submission states');
const drillthroughSource = ref('');
const selectedBeneficiaryId = ref('');
const suppressHashSync = ref(false);

const regions = computed(() => ['All regions', ...Array.from(new Set(beneficiaryRecords.map((record) => record.region))).sort()]);
const verificationStatuses = ['All statuses', 'Verified', 'Under review', 'Incomplete'];
const borrowerStatuses = ['All borrower statuses', 'Active borrower', 'Training only', 'Pending verification'];
const trainingStates = ['All training states', 'Trained', 'Not yet trained'];
const submissionStatuses = ['All submission states', 'Submitted', 'Under review', 'Returned', 'Awaiting submission'];
const technologies = computed(() => [
  'All technologies',
  ...Array.from(new Set(beneficiaryRecords.flatMap((record) => [
    record.technology,
    ...record.technologiesFinanced.map((technology) => technology.name),
  ]))).sort(),
]);
const beneficiaryDataverseTargets = [
  'mp_TrackedEntity',
  'mp_BeneficiaryProfile',
  'mp_BeneficiaryProgrammeParticipation',
  'mp_BeneficiaryFinanceLink',
  'mp_BeneficiaryTechnologyAdoption',
  'mp_BeneficiaryTrainingParticipation',
  'mp_BeneficiaryOutcomeSnapshot',
  'mp_BeneficiarySubmissionLink',
  'mp_BeneficiaryIdentityMatch',
  'mp_BeneficiaryGroupMembership',
  'mp_BeneficiaryLocationHistory',
];

function normaliseFilterValue(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function setIfAllowed(target: typeof activeRegion, value: string | null, allowedValues: string[], fallback: string) {
  target.value = value && allowedValues.includes(value) ? value : fallback;
}

function technologyMatches(record: BeneficiaryRecord, technologyFilter: string) {
  if (technologyFilter === 'All technologies') return true;
  const requested = normaliseFilterValue(technologyFilter);
  const candidates = [
    record.technology,
    ...record.technologiesFinanced.map((technology) => technology.name),
  ].map(normaliseFilterValue);
  return candidates.some((candidate) => candidate.includes(requested) || requested.includes(candidate));
}

const filteredBeneficiaries = computed(() => {
  const search = searchTerm.value.trim().toLowerCase();
  return beneficiaryRecords.filter((record) => {
    const matchesSearch = !search || [
      record.id,
      record.name,
      record.category,
      record.region,
      record.district,
      record.borrowerStatus,
      record.loanType,
      record.technology,
      record.verificationStatus,
      record.projectParticipation.programme,
      record.projectParticipation.project,
      record.projectParticipation.implementationPartner,
      record.latestSubmission.form,
      record.latestSubmission.status,
    ].some((value) => value.toLowerCase().includes(search));
    const matchesRegion = activeRegion.value === 'All regions' || record.region === activeRegion.value;
    const matchesVerification = activeVerification.value === 'All statuses' || record.verificationStatus === activeVerification.value;
    const matchesBorrowerStatus = activeBorrowerStatus.value === 'All borrower statuses' || record.borrowerStatus === activeBorrowerStatus.value;
    const matchesTraining = activeTraining.value === 'All training states'
      || (activeTraining.value === 'Trained' ? record.trained : !record.trained);
    const matchesTechnology = technologyMatches(record, activeTechnology.value);
    const matchesSubmission = activeSubmissionStatus.value === 'All submission states' || record.latestSubmission.status === activeSubmissionStatus.value;
    return matchesSearch && matchesRegion && matchesVerification && matchesBorrowerStatus && matchesTraining && matchesTechnology && matchesSubmission;
  });
});

const selectedBeneficiary = computed(() => (
  beneficiaryRecords.find((record) => record.id === selectedBeneficiaryId.value) ?? null
));

const summaryMetrics = computed(() => {
  const activeBorrowers = beneficiaryRecords.filter((record) => record.borrowerStatus === 'Active borrower').length;
  const trained = beneficiaryRecords.filter((record) => record.trained).length;
  const verified = beneficiaryRecords.filter((record) => record.verificationStatus === 'Verified').length;
  return [
    { label: 'Beneficiary records', value: beneficiaryRecords.length.toLocaleString(), detail: 'Prototype list limit' },
    { label: 'Active borrowers', value: activeBorrowers.toLocaleString(), detail: 'Linked to finance' },
    { label: 'Training reached', value: trained.toLocaleString(), detail: 'Capacity-building flag' },
    { label: 'Verified records', value: verified.toLocaleString(), detail: 'Ready for reporting' },
  ];
});

const activeFilters = computed(() => [
  activeRegion.value !== 'All regions' ? { key: 'region', label: `Region: ${activeRegion.value}` } : null,
  activeVerification.value !== 'All statuses' ? { key: 'verification', label: `Verification: ${activeVerification.value}` } : null,
  activeBorrowerStatus.value !== 'All borrower statuses' ? { key: 'borrowerStatus', label: `Borrower: ${activeBorrowerStatus.value}` } : null,
  activeTraining.value !== 'All training states' ? { key: 'trained', label: `Training: ${activeTraining.value}` } : null,
  activeTechnology.value !== 'All technologies' ? { key: 'technology', label: `Technology: ${activeTechnology.value}` } : null,
  activeSubmissionStatus.value !== 'All submission states' ? { key: 'submissionStatus', label: `Submission: ${activeSubmissionStatus.value}` } : null,
  searchTerm.value.trim() ? { key: 'search', label: `Search: ${searchTerm.value.trim()}` } : null,
].filter((filter): filter is { key: string; label: string } => Boolean(filter)));

const hasDashboardContext = computed(() => drillthroughSource.value === 'dashboard');
const filterSummary = computed(() => activeFilters.value.map((filter) => filter.label).join(' · '));

function syncBeneficiaryHashFilters() {
  if (suppressHashSync.value || window.location.hash.split('?')[0].replace(/^#\/?/, '') !== 'beneficiaries') return;

  const params = new URLSearchParams();
  if (activeRegion.value !== 'All regions') params.set('region', activeRegion.value);
  if (activeVerification.value !== 'All statuses') params.set('verification', activeVerification.value);
  if (activeBorrowerStatus.value !== 'All borrower statuses') params.set('borrowerStatus', activeBorrowerStatus.value);
  if (activeTraining.value !== 'All training states') params.set('trained', activeTraining.value === 'Trained' ? 'true' : 'false');
  if (activeTechnology.value !== 'All technologies') params.set('technology', activeTechnology.value);
  if (activeSubmissionStatus.value !== 'All submission states') params.set('submissionStatus', activeSubmissionStatus.value);
  if (drillthroughSource.value) params.set('source', drillthroughSource.value);

  const query = params.toString();
  const nextHash = `#/beneficiaries${query ? `?${query}` : ''}`;
  if (window.location.hash !== nextHash) {
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}${nextHash}`);
  }
}

function readBeneficiaryHashFilters() {
  if (window.location.hash.split('?')[0].replace(/^#\/?/, '') !== 'beneficiaries') return;

  suppressHashSync.value = true;
  const query = window.location.hash.split('?')[1] ?? '';
  const params = new URLSearchParams(query);
  setIfAllowed(activeRegion, params.get('region'), regions.value, 'All regions');
  setIfAllowed(activeVerification, params.get('verification'), verificationStatuses, 'All statuses');
  setIfAllowed(activeBorrowerStatus, params.get('borrowerStatus'), borrowerStatuses, 'All borrower statuses');
  setIfAllowed(activeTechnology, params.get('technology'), technologies.value, 'All technologies');
  setIfAllowed(activeSubmissionStatus, params.get('submissionStatus'), submissionStatuses, 'All submission states');
  activeTraining.value = params.get('trained') === 'true'
    ? 'Trained'
    : params.get('trained') === 'false'
      ? 'Not yet trained'
      : 'All training states';
  drillthroughSource.value = params.get('source') === 'dashboard' ? 'dashboard' : '';
  suppressHashSync.value = false;
}

function clearFilter(key: string) {
  if (key === 'region') activeRegion.value = 'All regions';
  if (key === 'verification') activeVerification.value = 'All statuses';
  if (key === 'borrowerStatus') activeBorrowerStatus.value = 'All borrower statuses';
  if (key === 'trained') activeTraining.value = 'All training states';
  if (key === 'technology') activeTechnology.value = 'All technologies';
  if (key === 'submissionStatus') activeSubmissionStatus.value = 'All submission states';
  if (key === 'search') searchTerm.value = '';
  if (key !== 'search') syncBeneficiaryHashFilters();
}

function clearAllFilters() {
  searchTerm.value = '';
  activeRegion.value = 'All regions';
  activeVerification.value = 'All statuses';
  activeBorrowerStatus.value = 'All borrower statuses';
  activeTraining.value = 'All training states';
  activeTechnology.value = 'All technologies';
  activeSubmissionStatus.value = 'All submission states';
  drillthroughSource.value = '';
  syncBeneficiaryHashFilters();
}

function openAllBeneficiaries() {
  clearAllFilters();
}

function backToDashboard() {
  window.location.hash = '#/dashboard';
}

function openBeneficiary(record: BeneficiaryRecord) {
  selectedBeneficiaryId.value = record.id;
}

function closeBeneficiary() {
  selectedBeneficiaryId.value = '';
}

function statusTone(status: BeneficiaryRecord['verificationStatus']) {
  if (status === 'Verified') return 'success';
  if (status === 'Under review') return 'warning';
  return 'error';
}

watch([activeRegion, activeVerification, activeBorrowerStatus, activeTraining, activeTechnology, activeSubmissionStatus], syncBeneficiaryHashFilters);

onMounted(() => {
  readBeneficiaryHashFilters();
  window.addEventListener('hashchange', readBeneficiaryHashFilters);
});

onUnmounted(() => {
  window.removeEventListener('hashchange', readBeneficiaryHashFilters);
});
</script>

<template>
  <section class="beneficiaries-page" aria-labelledby="beneficiaries-title">
    <SurfaceCard as="section" class="beneficiaries-hero">
      <div>
        <p class="beneficiaries-eyebrow">Beneficiary registry</p>
        <h1 id="beneficiaries-title">Beneficiaries</h1>
        <p>
          Demonstration records for modelling TACATDP farmers, groups, and institutions as reusable monitored entities.
        </p>
      </div>
      <span class="beneficiaries-hero__icon" aria-hidden="true">
        <Users />
      </span>
    </SurfaceCard>

    <section class="beneficiaries-summary" aria-label="Beneficiary summary">
      <SurfaceCard v-for="metric in summaryMetrics" :key="metric.label" as="article" accent="green" accented class="beneficiary-metric">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <small>{{ metric.detail }}</small>
      </SurfaceCard>
    </section>

    <SurfaceCard as="section" class="material-list-surface beneficiary-list" aria-labelledby="beneficiary-list-title">
      <header class="material-surface-header beneficiary-list__header">
        <div>
          <h2 id="beneficiary-list-title">Beneficiary records</h2>
          <p>Prototype data only. These figures are not official CRDB Bank or Green Climate Fund statistics.</p>
        </div>
        <span class="material-count-chip beneficiary-list__count">{{ filteredBeneficiaries.length }} shown</span>
      </header>

      <section v-if="hasDashboardContext" class="beneficiary-drillthrough-context" aria-label="Dashboard drill-through context">
        <div>
          <strong>Opened from dashboard</strong>
          <span>{{ filterSummary || 'Dashboard context is active. Filters are preserved in the URL for review and sharing.' }}</span>
        </div>
        <button class="beneficiary-row-action" type="button" @click="backToDashboard">Back to Dashboard</button>
      </section>

      <form class="beneficiary-toolbar" role="search" aria-label="Search and filter beneficiary records" @submit.prevent>
        <label class="beneficiary-search">
          <span>Search beneficiaries</span>
          <span class="beneficiary-search__field">
            <Search aria-hidden="true" />
            <input v-model="searchTerm" type="search" placeholder="Name, ID, region, technology" autocomplete="off">
          </span>
        </label>

        <label class="beneficiary-filter">
          <span>Region</span>
          <select v-model="activeRegion">
            <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
          </select>
        </label>

        <label class="beneficiary-filter">
          <span>Verification</span>
          <select v-model="activeVerification">
            <option v-for="status in verificationStatuses" :key="status" :value="status">{{ status }}</option>
          </select>
        </label>

        <label class="beneficiary-filter">
          <span>Borrower status</span>
          <select v-model="activeBorrowerStatus">
            <option v-for="status in borrowerStatuses" :key="status" :value="status">{{ status }}</option>
          </select>
        </label>

        <label class="beneficiary-filter">
          <span>Training</span>
          <select v-model="activeTraining">
            <option v-for="state in trainingStates" :key="state" :value="state">{{ state }}</option>
          </select>
        </label>

        <label class="beneficiary-filter">
          <span>Technology</span>
          <select v-model="activeTechnology">
            <option v-for="technology in technologies" :key="technology" :value="technology">{{ technology }}</option>
          </select>
        </label>

        <button class="beneficiary-filter-button" type="button" @click="clearAllFilters">
          <Filter aria-hidden="true" />
          Clear filters
        </button>
      </form>

      <div v-if="activeFilters.length > 0" class="beneficiary-active-filters" aria-label="Active filters">
        <button v-for="filter in activeFilters" :key="filter.key" type="button" @click="clearFilter(filter.key)">
          {{ filter.label }}
          <span aria-hidden="true">×</span>
        </button>
      </div>

      <div v-if="filteredBeneficiaries.length === 0" class="beneficiary-empty-state" role="status">
        <SlidersHorizontal aria-hidden="true" />
        <strong>No data for the selected filters</strong>
        <span v-if="hasDashboardContext">Dashboard drill-through filters: {{ filterSummary || 'no active filters' }}.</span>
        <span v-else>Clear filters or adjust the search term to review prototype beneficiary records.</span>
        <div class="beneficiary-empty-state__actions">
          <button class="beneficiary-row-action" type="button" @click="clearAllFilters">Clear filters</button>
          <button v-if="hasDashboardContext" class="beneficiary-row-action" type="button" @click="openAllBeneficiaries">Open all beneficiaries</button>
          <button v-if="hasDashboardContext" class="beneficiary-row-action" type="button" @click="backToDashboard">Back to Dashboard</button>
        </div>
      </div>

      <div v-else class="beneficiary-table-wrap material-table">
        <table class="beneficiary-table" aria-label="Beneficiary records">
          <thead>
            <tr>
              <th scope="col">Beneficiary</th>
              <th scope="col">Location</th>
              <th scope="col">Borrower status</th>
              <th scope="col">Loan type</th>
              <th scope="col">Technology financed</th>
              <th scope="col">Training</th>
              <th scope="col">Verification</th>
              <th scope="col">Updated</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredBeneficiaries" :key="record.id" class="material-row" tabindex="0" @dblclick="openBeneficiary(record)">
              <td>
                <strong>{{ record.name }}</strong>
                <span>{{ record.id }} · {{ record.category }}</span>
              </td>
              <td>
                <strong>{{ record.region }}</strong>
                <span>{{ record.district }}</span>
              </td>
              <td>{{ record.borrowerStatus }}</td>
              <td>{{ record.loanType }}</td>
              <td>{{ record.technology }}</td>
              <td>{{ record.trained ? 'Trained' : 'Not yet trained' }}</td>
              <td>
                <span class="beneficiary-status-chip" :class="`beneficiary-status-chip--${statusTone(record.verificationStatus)}`">
                  {{ record.verificationStatus }}
                </span>
              </td>
              <td>{{ record.lastUpdated }}</td>
              <td>
                <button class="beneficiary-row-action" type="button" @click="openBeneficiary(record)">
                  <Eye aria-hidden="true" />
                  View details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="beneficiary-card-list" aria-label="Beneficiary records mobile list">
        <article v-for="record in filteredBeneficiaries" :key="`card:${record.id}`" class="material-row beneficiary-record-card" tabindex="0">
          <div>
            <strong>{{ record.name }}</strong>
            <span>{{ record.id }} · {{ record.category }}</span>
          </div>
          <dl>
            <div>
              <dt>Location</dt>
              <dd>{{ record.region }} · {{ record.district }}</dd>
            </div>
            <div>
              <dt>Finance</dt>
              <dd>{{ record.borrowerStatus }} · {{ record.loanType }}</dd>
            </div>
            <div>
              <dt>Technology</dt>
              <dd>{{ record.technology }}</dd>
            </div>
          </dl>
          <footer class="material-card-footer">
            <span>{{ record.trained ? 'Trained' : 'Not yet trained' }}</span>
            <span class="beneficiary-status-chip" :class="`beneficiary-status-chip--${statusTone(record.verificationStatus)}`">
              {{ record.verificationStatus }}
            </span>
          </footer>
          <button class="beneficiary-row-action" type="button" @click="openBeneficiary(record)">
            <Eye aria-hidden="true" />
            View details
          </button>
        </article>
      </div>
    </SurfaceCard>

    <button
      v-if="selectedBeneficiary"
      class="beneficiary-detail-scrim"
      type="button"
      aria-label="Close beneficiary detail"
      @click="closeBeneficiary"
    ></button>

    <aside
      v-if="selectedBeneficiary"
      class="material-detail-surface beneficiary-detail-drawer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="beneficiary-detail-title"
    >
      <header class="material-detail-header beneficiary-detail-header beneficiary-detail-header--structured">
        <div class="beneficiary-detail-identity">
          <p class="beneficiaries-eyebrow">Beneficiary detail</p>
          <h2 id="beneficiary-detail-title">{{ selectedBeneficiary.name }}</h2>
          <div class="beneficiary-detail-tags" aria-label="Beneficiary identity summary">
            <span>{{ selectedBeneficiary.id }}</span>
            <span>{{ selectedBeneficiary.category }}</span>
            <span>{{ selectedBeneficiary.region }} · {{ selectedBeneficiary.district }}</span>
            <span class="beneficiary-status-chip" :class="`beneficiary-status-chip--${statusTone(selectedBeneficiary.verificationStatus)}`">
              {{ selectedBeneficiary.verificationStatus }}
            </span>
          </div>
        </div>
        <button class="beneficiary-detail-close" type="button" aria-label="Close beneficiary detail" @click="closeBeneficiary">
          <X aria-hidden="true" />
        </button>
      </header>

      <section v-if="hasDashboardContext" class="beneficiary-detail-context" aria-label="Dashboard drill-through context">
        <div>
          <strong>Opened from dashboard</strong>
          <span>{{ filterSummary || 'Dashboard context is active.' }}</span>
        </div>
        <button class="beneficiary-row-action" type="button" @click="backToDashboard">Back to Dashboard</button>
      </section>

      <p class="beneficiary-detail-note">Demonstration detail, not official statistics. Values show the reviewed Dataverse-ready entity shape for prototype review.</p>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Profile">
        <h3>Profile</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Location</dt>
            <dd>{{ selectedBeneficiary.region }} · {{ selectedBeneficiary.district }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Borrower status</dt>
            <dd>{{ selectedBeneficiary.borrowerStatus }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Verification</dt>
            <dd>
              <span class="beneficiary-status-chip" :class="`beneficiary-status-chip--${statusTone(selectedBeneficiary.verificationStatus)}`">
                {{ selectedBeneficiary.verificationStatus }}
              </span>
            </dd>
          </div>
          <div class="material-detail-row">
            <dt>Last updated</dt>
            <dd>{{ selectedBeneficiary.lastUpdated }}</dd>
          </div>
        </dl>
        <dl class="material-detail-list beneficiary-detail-list beneficiary-detail-list--nested">
          <div class="material-detail-row">
            <dt>Programme</dt>
            <dd>{{ selectedBeneficiary.projectParticipation.programme }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Project</dt>
            <dd>{{ selectedBeneficiary.projectParticipation.project }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Implementation partner</dt>
            <dd>{{ selectedBeneficiary.projectParticipation.implementationPartner }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Enrolment</dt>
            <dd>{{ selectedBeneficiary.projectParticipation.enrolmentDate }} · {{ selectedBeneficiary.projectParticipation.participationRole }}</dd>
          </div>
        </dl>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Identity governance">
        <h3>Identity governance</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Match state</dt>
            <dd>{{ selectedBeneficiary.identityGovernance?.matchState ?? 'Not yet reviewed' }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Match signals</dt>
            <dd>{{ selectedBeneficiary.identityGovernance?.matchSignals ?? 'Awaiting identity review' }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Reviewer decision</dt>
            <dd>{{ selectedBeneficiary.identityGovernance?.reviewerDecision ?? 'No reviewer decision recorded' }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Model target</dt>
            <dd>mp_BeneficiaryIdentityMatch</dd>
          </div>
        </dl>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Group membership">
        <h3>Group membership</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Membership type</dt>
            <dd>{{ selectedBeneficiary.groupMembership?.membershipType ?? 'Not yet modelled' }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Members linked</dt>
            <dd>{{ selectedBeneficiary.groupMembership?.membersLinked ?? 'No member linkage in prototype data' }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Status</dt>
            <dd>{{ selectedBeneficiary.groupMembership?.membershipStatus ?? 'Not modelled' }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Model target</dt>
            <dd>mp_BeneficiaryGroupMembership</dd>
          </div>
        </dl>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Finance">
        <h3>Finance</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Loan reference</dt>
            <dd>{{ selectedBeneficiary.finance.loanAccountRef }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Disbursed</dt>
            <dd>{{ selectedBeneficiary.finance.disbursedAmount }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Outstanding</dt>
            <dd>{{ selectedBeneficiary.finance.outstandingBalance }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Repayment rate</dt>
            <dd>{{ selectedBeneficiary.finance.repaymentRate }}</dd>
          </div>
        </dl>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Technology">
        <h3>Technology</h3>
        <ul class="beneficiary-technology-list">
          <li v-for="technology in selectedBeneficiary.technologiesFinanced" :key="`${selectedBeneficiary.id}:${technology.name}`">
            <strong>{{ technology.name }}</strong>
            <span>{{ technology.category }} · {{ technology.adoptionStage }}</span>
          </li>
        </ul>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Training">
        <h3>Training</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Sessions attended</dt>
            <dd>{{ selectedBeneficiary.trainingSummary.sessionsAttended }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Completion</dt>
            <dd>{{ selectedBeneficiary.trainingSummary.completionRate }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Latest topic</dt>
            <dd>{{ selectedBeneficiary.trainingSummary.lastTopic }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Last training</dt>
            <dd>{{ selectedBeneficiary.trainingSummary.lastTrainingDate }}</dd>
          </div>
        </dl>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Outcomes">
        <h3>Outcomes</h3>
        <dl class="material-detail-list beneficiary-detail-list">
          <div class="material-detail-row">
            <dt>Area under improved practices</dt>
            <dd>{{ selectedBeneficiary.outcomeSnapshot.areaUnderImprovedPractices }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Yield increase</dt>
            <dd>{{ selectedBeneficiary.outcomeSnapshot.yieldIncrease }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Climate estimate</dt>
            <dd>{{ selectedBeneficiary.outcomeSnapshot.climateEstimate }}</dd>
          </div>
        </dl>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Data lineage">
        <h3>Data lineage</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Latest submission</dt>
            <dd>{{ selectedBeneficiary.latestSubmission.form }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Reporting period</dt>
            <dd>{{ selectedBeneficiary.latestSubmission.reportingPeriod }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Completeness</dt>
            <dd>{{ selectedBeneficiary.latestSubmission.completeness }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Verification state</dt>
            <dd>{{ selectedBeneficiary.latestSubmission.status }}</dd>
          </div>
        </dl>
        <p class="beneficiary-detail-secondary">
          Source: {{ selectedBeneficiary.latestSubmission.dataSource }}. In production this links through
          mp_BeneficiarySubmissionLink to the source mp_Submission record.
        </p>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Location history">
        <h3>Location history</h3>
        <dl class="material-detail-list beneficiary-detail-grid">
          <div class="material-detail-row">
            <dt>Current location</dt>
            <dd>{{ selectedBeneficiary.locationHistory?.currentLocation ?? `${selectedBeneficiary.region} · ${selectedBeneficiary.district}` }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Source</dt>
            <dd>{{ selectedBeneficiary.locationHistory?.source ?? selectedBeneficiary.latestSubmission.dataSource }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Effective from</dt>
            <dd>{{ selectedBeneficiary.locationHistory?.effectiveFrom ?? selectedBeneficiary.projectParticipation.enrolmentDate }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>History state</dt>
            <dd>{{ selectedBeneficiary.locationHistory?.historyState ?? 'Current profile location' }}</dd>
          </div>
        </dl>
        <p class="beneficiary-detail-secondary">
          Production location changes are stored in mp_BeneficiaryLocationHistory so dashboard filters can use the current location without losing historical evidence.
        </p>
      </section>

      <section class="material-detail-section beneficiary-detail-section" aria-label="Technical Dataverse mapping">
        <h3>Technical Dataverse mapping</h3>
        <ul class="beneficiary-mapping-targets" aria-label="Mapped Dataverse tables">
          <li v-for="target in beneficiaryDataverseTargets" :key="target">{{ target }}</li>
        </ul>
        <dl class="material-detail-list beneficiary-detail-list">
          <div class="material-detail-row">
            <dt>Primary target</dt>
            <dd>{{ selectedBeneficiary.futureDataverseMapping.table }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Record ID</dt>
            <dd>{{ selectedBeneficiary.futureDataverseMapping.recordId }}</dd>
          </div>
          <div class="material-detail-row">
            <dt>Relationship notes</dt>
            <dd>{{ selectedBeneficiary.futureDataverseMapping.relationshipNotes }}</dd>
          </div>
        </dl>
      </section>
    </aside>
  </section>
</template>

<style scoped>
.beneficiaries-page {
  --m3-primary: #15803D;
  --m3-primary-dark: #064E3B;
  --m3-surface: #FFFFFF;
  --m3-surface-container: #F7FAF8;
  --m3-surface-container-high: #EEF6F0;
  --m3-outline: #DCE7E0;
  --m3-outline-strong: #C6D6CD;
  --m3-on-surface: #17211C;
  --m3-on-surface-variant: #64706A;
  --m3-error: #DC2626;
  --m3-warning: #9A6500;
  display: grid;
  gap: 24px;
}

.beneficiaries-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: center;
  padding: 24px;
}

.beneficiaries-hero h1,
.beneficiary-list h2 {
  margin: 0;
  color: var(--m3-on-surface);
  line-height: 1.15;
}

.beneficiaries-hero h1 {
  font-size: clamp(1.45rem, 2vw, 1.9rem);
}

.beneficiaries-hero p,
.beneficiary-list__header p {
  max-width: 780px;
  margin: 8px 0 0;
  color: var(--m3-on-surface-variant);
  font-size: 0.92rem;
  line-height: 1.45;
}

.beneficiaries-eyebrow {
  margin: 0 0 6px;
  color: var(--m3-primary-dark);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.beneficiaries-hero__icon {
  display: inline-grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: var(--m3-surface-container-high);
  color: var(--m3-primary);
}

.beneficiaries-hero__icon svg,
.beneficiary-row-action svg,
.beneficiary-detail-close svg,
.beneficiary-filter-button svg,
.beneficiary-search__field svg,
.beneficiary-empty-state svg {
  width: 20px;
  height: 20px;
}

.beneficiaries-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.beneficiary-metric {
  display: grid;
  gap: 6px;
  padding: 18px;
}

.beneficiary-metric span,
.beneficiary-metric small {
  color: var(--m3-on-surface-variant);
  font-weight: 700;
}

.beneficiary-metric span {
  font-size: 0.76rem;
  text-transform: uppercase;
}

.beneficiary-metric strong {
  color: var(--m3-on-surface);
  font-size: 1.55rem;
  line-height: 1;
}

.beneficiary-list {
  display: grid;
  gap: 16px;
  padding: 20px;
  overflow: hidden;
}

.beneficiary-list__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
}

.material-surface-header h2,
.material-surface-header p {
  margin: 0;
}

.beneficiary-list__count {
  flex: 0 0 auto;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--m3-surface-container-high);
  color: var(--m3-primary-dark);
  font-size: 0.78rem;
  font-weight: 800;
}

.beneficiary-drillthrough-context {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #B7D6BF;
  border-radius: 12px;
  background: #EAF7EE;
  color: var(--m3-primary-dark);
  font-size: 0.82rem;
  font-weight: 800;
}

.beneficiary-drillthrough-context div {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.beneficiary-drillthrough-context span {
  color: #315D44;
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.35;
}

.beneficiary-toolbar {
  display: grid;
  grid-template-columns: minmax(260px, 1.4fr) repeat(4, minmax(145px, 0.5fr)) auto;
  gap: 12px;
  align-items: end;
}

.beneficiary-search,
.beneficiary-filter {
  display: grid;
  gap: 6px;
  color: var(--m3-on-surface-variant);
  font-size: 0.76rem;
  font-weight: 800;
}

.beneficiary-search__field {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 14px;
  border: 1px solid var(--m3-outline-strong);
  border-radius: 12px;
  background: var(--m3-surface-container);
  color: var(--m3-on-surface-variant);
}

.beneficiary-search input,
.beneficiary-filter select {
  width: 100%;
  border: 0;
  background: transparent;
  color: var(--m3-on-surface);
  font: inherit;
  font-size: 0.9rem;
  outline: none;
}

.beneficiary-filter select {
  min-height: 44px;
  padding: 0 12px;
  border: 1px solid var(--m3-outline-strong);
  border-radius: 12px;
  background: var(--m3-surface-container);
}

.beneficiary-search__field:focus-within,
.beneficiary-filter select:focus-visible,
.beneficiary-filter-button:focus-visible,
.beneficiary-active-filters button:focus-visible,
.beneficiary-empty-state__actions button:focus-visible,
.beneficiary-table tbody tr:focus-visible,
.beneficiary-row-action:focus-visible,
.beneficiary-detail-close:focus-visible {
  outline: 3px solid rgba(21, 128, 61, 0.24);
  outline-offset: 2px;
}

.beneficiary-filter-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 16px;
  border: 1px solid var(--m3-outline-strong);
  border-radius: 999px;
  background: var(--m3-surface);
  color: var(--m3-primary-dark);
  font: inherit;
  font-size: 0.86rem;
  font-weight: 800;
  cursor: pointer;
}

.beneficiary-active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.beneficiary-active-filters button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
  padding: 0 12px;
  border: 1px solid #B7D6BF;
  border-radius: 999px;
  background: #EAF7EE;
  color: var(--m3-primary-dark);
  font: inherit;
  font-size: 0.78rem;
  font-weight: 800;
  cursor: pointer;
}

.beneficiary-table-wrap {
  overflow: auto;
  border: 1px solid var(--m3-outline);
  border-radius: 14px;
}

.beneficiary-table {
  width: 100%;
  min-width: 1240px;
  border-collapse: collapse;
  color: var(--m3-on-surface);
  font-size: 0.84rem;
}

.beneficiary-table thead {
  background: var(--m3-surface-container);
}

.beneficiary-table th {
  padding: 13px 16px;
  color: var(--m3-on-surface-variant);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.02em;
  text-align: left;
  text-transform: uppercase;
  white-space: nowrap;
}

.beneficiary-table td {
  padding: 14px 16px;
  border-top: 1px solid var(--m3-outline);
  vertical-align: middle;
}

.beneficiary-table tbody tr:hover,
.beneficiary-table tbody tr:focus-visible {
  background: #F4FAF6;
}

.material-table tbody tr:hover,
.material-table tbody tr:focus-visible,
.material-row:hover,
.material-row:focus-visible {
  outline: 3px solid rgba(21, 128, 61, 0.16);
  outline-offset: -3px;
}

.beneficiary-table td strong,
.beneficiary-table td span {
  display: block;
}

.beneficiary-row-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid #B7D6BF;
  border-radius: 999px;
  background: #FFFFFF;
  color: var(--m3-primary-dark);
  font: inherit;
  font-size: 0.76rem;
  font-weight: 900;
  white-space: nowrap;
  cursor: pointer;
}

.beneficiary-row-action:hover {
  background: #EAF7EE;
}

.beneficiary-table td span {
  margin-top: 3px;
  color: var(--m3-on-surface-variant);
  font-size: 0.76rem;
  font-weight: 650;
}

.beneficiary-status-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 900;
  white-space: nowrap;
}

.beneficiary-status-chip--success {
  background: #EAF7EE;
  color: #0F6B2D;
}

.beneficiary-status-chip--warning {
  background: #FFF5DD;
  color: var(--m3-warning);
}

.beneficiary-status-chip--error {
  background: #FFF1F1;
  color: var(--m3-error);
}

.beneficiary-empty-state {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 220px;
  padding: 24px;
  border: 1px dashed var(--m3-outline-strong);
  border-radius: 14px;
  background: var(--m3-surface-container);
  color: var(--m3-on-surface-variant);
  text-align: center;
}

.beneficiary-empty-state strong {
  color: var(--m3-on-surface);
}

.beneficiary-empty-state > span {
  max-width: 620px;
  line-height: 1.45;
}

.beneficiary-empty-state__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 6px;
}

.beneficiary-card-list {
  display: none;
}

.beneficiary-detail-scrim {
  position: fixed;
  inset: 0;
  z-index: 45;
  border: 0;
  background: rgba(6, 78, 59, 0.22);
  cursor: pointer;
}

.beneficiary-detail-drawer {
  position: fixed;
  inset: 16px 16px 16px auto;
  z-index: 46;
  display: grid;
  align-content: start;
  gap: 14px;
  width: min(520px, calc(100vw - 32px));
  padding: 20px;
  overflow: auto;
  border: 1px solid var(--m3-outline);
  border-radius: 22px;
  background: var(--m3-surface);
  box-shadow: 0 24px 72px rgba(23, 33, 28, 0.22);
}

.beneficiary-detail-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
}

.beneficiary-detail-identity {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.beneficiary-detail-header h2 {
  margin: 0;
  color: var(--m3-on-surface);
  font-size: 1.35rem;
  line-height: 1.16;
}

.beneficiary-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-items: center;
}

.beneficiary-detail-tags > span:not(.beneficiary-status-chip) {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border: 1px solid var(--m3-outline);
  border-radius: 999px;
  background: var(--m3-surface-container);
  color: var(--m3-on-surface-variant);
  font-size: 0.74rem;
  font-weight: 850;
  white-space: nowrap;
}

.beneficiary-detail-header p:not(.beneficiaries-eyebrow),
.beneficiary-detail-note,
.beneficiary-detail-secondary {
  margin: 6px 0 0;
  color: var(--m3-on-surface-variant);
  font-size: 0.84rem;
  line-height: 1.45;
}

.beneficiary-detail-context {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border: 1px solid #B7D6BF;
  border-radius: 14px;
  background: #EAF7EE;
}

.beneficiary-detail-context div {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.beneficiary-detail-context strong {
  color: var(--m3-primary-dark);
  font-size: 0.84rem;
}

.beneficiary-detail-context span {
  color: #315D44;
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.35;
}

.beneficiary-detail-close {
  display: inline-grid;
  flex: 0 0 auto;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--m3-outline);
  border-radius: 999px;
  background: var(--m3-surface-container);
  color: var(--m3-on-surface);
  cursor: pointer;
}

.beneficiary-detail-section {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid var(--m3-outline);
  border-radius: 16px;
  background: var(--m3-surface-container);
}

.beneficiary-detail-section h3 {
  margin: 0;
  color: var(--m3-on-surface);
  font-size: 0.9rem;
  line-height: 1.25;
}

.beneficiary-detail-grid,
.beneficiary-detail-list {
  display: grid;
  gap: 10px;
  margin: 0;
}

.beneficiary-detail-list--nested {
  margin-top: 2px;
  padding-top: 12px;
  border-top: 1px solid var(--m3-outline);
}

.beneficiary-detail-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.beneficiary-detail-grid div,
.beneficiary-detail-list div {
  min-width: 0;
}

.beneficiary-detail-grid dt,
.beneficiary-detail-list dt {
  margin: 0 0 3px;
  color: var(--m3-on-surface-variant);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
}

.beneficiary-detail-grid dd,
.beneficiary-detail-list dd {
  margin: 0;
  color: var(--m3-on-surface);
  font-size: 0.84rem;
  font-weight: 750;
  line-height: 1.35;
}

.beneficiary-technology-list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.beneficiary-technology-list li {
  display: grid;
  gap: 3px;
  padding: 10px 12px;
  border: 1px solid var(--m3-outline);
  border-radius: 12px;
  background: #FFFFFF;
}

.beneficiary-technology-list strong {
  color: var(--m3-on-surface);
  font-size: 0.84rem;
}

.beneficiary-technology-list span {
  color: var(--m3-on-surface-variant);
  font-size: 0.76rem;
  font-weight: 750;
}

.beneficiary-mapping-targets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.beneficiary-mapping-targets li {
  padding: 6px 10px;
  border: 1px solid #B7D6BF;
  border-radius: 999px;
  background: #EAF7EE;
  color: var(--m3-primary-dark);
  font-size: 0.72rem;
  font-weight: 850;
  white-space: nowrap;
}

@media (max-width: 1180px) {
  .beneficiaries-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .beneficiary-toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .beneficiaries-page {
    gap: 16px;
  }

  .beneficiaries-hero,
  .beneficiary-list {
    padding: 16px;
  }

  .beneficiaries-summary,
  .beneficiary-toolbar {
    grid-template-columns: 1fr;
  }

  .beneficiary-list__header {
    display: grid;
  }

  .beneficiary-drillthrough-context,
  .beneficiary-detail-context {
    display: grid;
    justify-items: start;
  }

  .beneficiary-table-wrap {
    display: none;
  }

  .beneficiary-card-list {
    display: grid;
    gap: 12px;
  }

  .beneficiary-record-card {
    display: grid;
    gap: 12px;
    padding: 14px;
    border: 1px solid var(--m3-outline);
    border-radius: 14px;
    background: var(--m3-surface-container);
  }

  .beneficiary-record-card strong,
  .beneficiary-record-card span {
    display: block;
  }

  .beneficiary-record-card span,
  .beneficiary-record-card dt {
    color: var(--m3-on-surface-variant);
    font-size: 0.78rem;
    font-weight: 750;
  }

  .beneficiary-record-card dl {
    display: grid;
    gap: 8px;
    margin: 0;
  }

  .beneficiary-record-card div,
  .beneficiary-record-card dd {
    min-width: 0;
  }

  .beneficiary-record-card dt,
  .beneficiary-record-card dd {
    margin: 0;
  }

  .beneficiary-record-card footer,
  .material-card-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
  }

  .beneficiary-record-card > .beneficiary-row-action {
    justify-self: start;
  }

  .beneficiary-detail-drawer {
    inset: auto 0 0;
    width: 100%;
    max-height: calc(100vh - 32px);
    border-radius: 22px 22px 0 0;
  }

  .beneficiary-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
