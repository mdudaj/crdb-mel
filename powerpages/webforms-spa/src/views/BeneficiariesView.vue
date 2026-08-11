<script setup lang="ts">
import { computed, ref } from 'vue';
import { Filter, Search, SlidersHorizontal, Users } from '@lucide/vue';
import SurfaceCard from '../components/ui/SurfaceCard.vue';
import { beneficiaryRecords, type BeneficiaryRecord } from '../prototype/beneficiaries';

const searchTerm = ref('');
const activeRegion = ref('All regions');
const activeVerification = ref('All statuses');

const regions = computed(() => ['All regions', ...Array.from(new Set(beneficiaryRecords.map((record) => record.region))).sort()]);
const verificationStatuses = ['All statuses', 'Verified', 'Under review', 'Incomplete'];

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
    ].some((value) => value.toLowerCase().includes(search));
    const matchesRegion = activeRegion.value === 'All regions' || record.region === activeRegion.value;
    const matchesVerification = activeVerification.value === 'All statuses' || record.verificationStatus === activeVerification.value;
    return matchesSearch && matchesRegion && matchesVerification;
  });
});

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
  activeVerification.value !== 'All statuses' ? { key: 'status', label: `Status: ${activeVerification.value}` } : null,
  searchTerm.value.trim() ? { key: 'search', label: `Search: ${searchTerm.value.trim()}` } : null,
].filter((filter): filter is { key: string; label: string } => Boolean(filter)));

function clearFilter(key: string) {
  if (key === 'region') activeRegion.value = 'All regions';
  if (key === 'status') activeVerification.value = 'All statuses';
  if (key === 'search') searchTerm.value = '';
}

function clearAllFilters() {
  searchTerm.value = '';
  activeRegion.value = 'All regions';
  activeVerification.value = 'All statuses';
}

function statusTone(status: BeneficiaryRecord['verificationStatus']) {
  if (status === 'Verified') return 'success';
  if (status === 'Under review') return 'warning';
  return 'error';
}
</script>

<template>
  <section class="beneficiaries-page" aria-labelledby="beneficiaries-title">
    <SurfaceCard as="section" accent="green" class="beneficiaries-hero">
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
      <SurfaceCard v-for="metric in summaryMetrics" :key="metric.label" as="article" accent="green" class="beneficiary-metric">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <small>{{ metric.detail }}</small>
      </SurfaceCard>
    </section>

    <SurfaceCard as="section" accent="green" class="beneficiary-list" aria-labelledby="beneficiary-list-title">
      <header class="beneficiary-list__header">
        <div>
          <p class="beneficiaries-eyebrow">Material list surface</p>
          <h2 id="beneficiary-list-title">Beneficiary records</h2>
          <p>Prototype data only. These figures are not official CRDB Bank or Green Climate Fund statistics.</p>
        </div>
        <span class="beneficiary-list__count">{{ filteredBeneficiaries.length }} shown</span>
      </header>

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
        <span>Clear filters or adjust the search term to review prototype beneficiary records.</span>
      </div>

      <div v-else class="beneficiary-table-wrap">
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
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredBeneficiaries" :key="record.id" tabindex="0">
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
            </tr>
          </tbody>
        </table>
      </div>

      <div class="beneficiary-card-list" aria-label="Beneficiary records mobile list">
        <article v-for="record in filteredBeneficiaries" :key="`card:${record.id}`" class="beneficiary-record-card">
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
          <footer>
            <span>{{ record.trained ? 'Trained' : 'Not yet trained' }}</span>
            <span class="beneficiary-status-chip" :class="`beneficiary-status-chip--${statusTone(record.verificationStatus)}`">
              {{ record.verificationStatus }}
            </span>
          </footer>
        </article>
      </div>
    </SurfaceCard>
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

.beneficiary-list__count {
  flex: 0 0 auto;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--m3-surface-container-high);
  color: var(--m3-primary-dark);
  font-size: 0.78rem;
  font-weight: 800;
}

.beneficiary-toolbar {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(160px, 0.28fr) minmax(170px, 0.28fr) auto;
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
.beneficiary-table tbody tr:focus-visible {
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
  min-width: 1120px;
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

.beneficiary-table td strong,
.beneficiary-table td span {
  display: block;
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
  border: 1px dashed var(--m3-outline-strong);
  border-radius: 14px;
  background: var(--m3-surface-container);
  color: var(--m3-on-surface-variant);
  text-align: center;
}

.beneficiary-empty-state strong {
  color: var(--m3-on-surface);
}

.beneficiary-card-list {
  display: none;
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

  .beneficiary-record-card footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
  }
}
</style>
