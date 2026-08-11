<script setup lang="ts">
import {
  Building2,
  CalendarDays,
  ChevronDown,
  Download,
  Filter,
  HandCoins,
  Leaf,
  MapPinned,
  Sprout,
  TrendingUp,
  Users,
} from '@lucide/vue';
import { computed, defineAsyncComponent, type Component } from 'vue';
import programImpactFarmer from '../../assets/dashboard/program-impact-farmer.png';
import tanzaniaAdm1 from '../../assets/maps/tanzania-adm1.json';
import { buildDisbursementTrendOption, type DashboardChartOption } from './chartOptions';
import DashboardCard from './DashboardCard.vue';
import DashboardPage from './DashboardPage.vue';
import KpiCard from './KpiCard.vue';
import {
  climateOutcomes,
  dashboardKpis,
  disbursementTrend,
  loanPerformance,
  loanPortfolio,
  recentSubmissions,
  regionalMetrics,
  technologyFinancing,
  type KpiMetric,
} from '../../prototype/tacatdpDashboardData';

type TanzaniaAdm1Feature = {
  properties?: {
    shapeName?: string;
  };
};

type TanzaniaAdm1FeatureCollection = {
  type: string;
  features: TanzaniaAdm1Feature[];
  [key: string]: unknown;
};

const zanzibarRegionNames = new Set([
  'Zanzibar South & Central',
  'North Pemba',
  'Zanzibar North',
  'Zanzibar Urban/West',
  'South Pemba',
]);

const mainlandTanzaniaAdm1 = {
  ...(tanzaniaAdm1 as TanzaniaAdm1FeatureCollection),
  features: (tanzaniaAdm1 as TanzaniaAdm1FeatureCollection).features.filter(
    (feature) => !zanzibarRegionNames.has(feature.properties?.shapeName ?? ''),
  ),
};

const DashboardChart = defineAsyncComponent(async () => {
  const [
    core,
    charts,
    components,
    features,
    renderers,
    vueECharts,
  ] = await Promise.all([
    import('echarts/core'),
    import('echarts/charts'),
    import('echarts/components'),
    import('echarts/features'),
    import('echarts/renderers'),
    import('vue-echarts'),
  ]);

  core.use([
    charts.BarChart,
    charts.LineChart,
    charts.MapChart,
    charts.PieChart,
    components.GridComponent,
    components.LegendComponent,
    components.TitleComponent,
    components.TooltipComponent,
    components.VisualMapComponent,
    features.LabelLayout,
    renderers.CanvasRenderer,
  ]);
  core.registerMap('tanzania-mainland-adm1', mainlandTanzaniaAdm1 as never);
  return vueECharts.default as Component;
});

const selectedRegion = regionalMetrics.find((region) => region.name === 'Morogoro') ?? regionalMetrics[0];
const regionData = regionalMetrics.map((region) => ({ name: region.name, value: region.disbursed }));

function openBeneficiaries(filters: Record<string, string>) {
  const params = new URLSearchParams({ source: 'dashboard', ...filters });
  window.location.hash = `#/beneficiaries?${params.toString()}`;
}

function chartParam(params: unknown): { name: string; value: number; percent: number } {
  const candidate = Array.isArray(params) ? params[0] : params;
  if (candidate && typeof candidate === 'object') {
    const record = candidate as Record<string, unknown>;
    return {
      name: typeof record.name === 'string' ? record.name : '',
      value: typeof record.value === 'number' ? record.value : 0,
      percent: typeof record.percent === 'number' ? record.percent : 0,
    };
  }
  return { name: '', value: 0, percent: 0 };
}

const loanPortfolioOption = computed<DashboardChartOption>(() => ({
  title: {
    text: 'Total',
    subtext: '12,458',
    left: '28%',
    top: '34%',
    textAlign: 'center',
    itemGap: 2,
    textStyle: { color: '#64706A', fontSize: 11, fontWeight: 600 },
    subtextStyle: { color: '#17211C', fontSize: 18, fontWeight: 800 },
  },
  tooltip: {
    trigger: 'item',
    formatter: (params: unknown) => {
      const itemParams = chartParam(params);
      const row = loanPortfolio.find((item) => item.name === itemParams.name);
      return `${itemParams.name}<br>${itemParams.value.toLocaleString()} loans (${itemParams.percent}%)<br>${row?.amount ?? 'Prototype amount'} disbursed`;
    },
  },
  legend: {
    orient: 'vertical',
    right: -8,
    bottom: -8,
    itemWidth: 9,
    itemHeight: 9,
    itemGap: 12,
    textStyle: { color: '#64706A', fontSize: 11 },
    formatter: (name: string) => {
      const item = loanPortfolio.find((entry) => entry.name === name);
      return item ? `${item.name}\n${item.value.toLocaleString()} (${item.percent}%)` : name;
    },
  },
  series: [{
    type: 'pie',
    radius: ['39%', '62%'],
    center: ['28%', '44%'],
    avoidLabelOverlap: false,
    data: loanPortfolio.map((item) => ({ name: item.name, value: item.value, itemStyle: { color: item.color } })),
    label: { show: false, position: 'center' },
    labelLine: { show: false },
  }],
}));

const disbursementTrendOption = computed<DashboardChartOption>(() => buildDisbursementTrendOption(disbursementTrend));

const loanPerformanceOption = computed<DashboardChartOption>(() => ({
  title: {
    text: 'Total Loans',
    subtext: '12,458',
    left: '30%',
    top: '39%',
    textAlign: 'center',
    itemGap: 2,
    textStyle: { color: '#64706A', fontSize: 11, fontWeight: 600 },
    subtextStyle: { color: '#17211C', fontSize: 18, fontWeight: 800 },
  },
  tooltip: {
    trigger: 'item',
    formatter: (params: unknown) => {
      const itemParams = chartParam(params);
      const row = loanPerformance.find((item) => item.name === itemParams.name);
      return `${itemParams.name}<br>${itemParams.value.toLocaleString()} loans (${itemParams.percent}%)<br>${row?.amount ?? 'Prototype outstanding principal'}`;
    },
  },
  legend: {
    orient: 'vertical',
    right: -6,
    top: 'middle',
    itemWidth: 9,
    itemHeight: 9,
    itemGap: 12,
    textStyle: { color: '#64706A', fontSize: 11 },
    formatter: (name: string) => {
      const item = loanPerformance.find((entry) => entry.name === name);
      return item ? `${item.name}\n${item.value.toLocaleString()} (${item.percent}%)` : name;
    },
  },
  series: [{
    type: 'pie',
    radius: ['39%', '62%'],
    center: ['30%', '50%'],
    avoidLabelOverlap: false,
    data: loanPerformance.map((item) => ({ name: item.name, value: item.value, itemStyle: { color: item.color } })),
    label: { show: false, position: 'center' },
    labelLine: { show: false },
  }],
}));

const technologyOption = computed<DashboardChartOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 6, right: 56, top: 8, bottom: 0, containLabel: true },
  xAxis: { show: false, type: 'value', max: 3000 },
  yAxis: {
    type: 'category',
    data: technologyFinancing.map((item) => item.name).reverse(),
    axisTick: { show: false },
    axisLine: { show: false },
    axisLabel: { color: '#17211C', width: 158, overflow: 'truncate' },
  },
  series: [{
    type: 'bar',
    data: technologyFinancing.map((item) => item.value).reverse(),
    barWidth: 8,
    itemStyle: { color: '#15803D', borderRadius: [0, 8, 8, 0] },
    label: {
      show: true,
      position: 'right',
      formatter: ({ dataIndex }) => {
        const item = [...technologyFinancing].reverse()[dataIndex];
        return `${item.value.toLocaleString()} (${item.percent}%)`;
      },
      color: '#64706A',
      fontSize: 11,
    },
  }],
}));

const regionalMapOption = computed<DashboardChartOption>(() => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: unknown) => {
      const itemParams = chartParam(params);
      const region = regionalMetrics.find((item) => item.name === itemParams.name);
      if (!region) return `${itemParams.name}<br>No prototype data`;
      return `${region.name}<br>${region.disbursedLabel} disbursed<br>${region.loans.toLocaleString()} loans<br>${region.repaymentRate} repayment`;
    },
  },
  visualMap: {
    type: 'piecewise',
    min: 0,
    max: 22,
    right: 0,
    top: 54,
    itemWidth: 12,
    itemHeight: 10,
    itemGap: 7,
    calculable: false,
    pieces: [
      { min: 20, label: '> TZS 20B', color: '#064E3B' },
      { min: 15, max: 20, label: 'TZS 15B – 20B', color: '#15803D' },
      { min: 10, max: 15, label: 'TZS 10B – 15B', color: '#2F9E44' },
      { min: 5, max: 10, label: 'TZS 5B – 10B', color: '#74C69D' },
      { min: 1, max: 5, label: 'TZS 1B – 5B', color: '#B7E4C7' },
      { min: 0, max: 1, label: '< TZS 1B', color: '#EAF7EE' },
    ],
    inRange: { color: ['#EAF7EE', '#B7E4C7', '#74C69D', '#2F9E44', '#064E3B'] },
    textStyle: { color: '#64706A', fontSize: 10.5 },
  },
  series: [{
    type: 'map',
    map: 'tanzania-mainland-adm1',
    aspectScale: 1.08,
    roam: false,
    nameProperty: 'shapeName',
    selectedMode: 'single',
    data: regionData,
    layoutCenter: ['38%', '52%'],
    layoutSize: '82%',
    label: { show: true, color: '#214036', fontSize: 9 },
    emphasis: { label: { color: '#064E3B', fontWeight: 700 }, itemStyle: { areaColor: '#8FD19E' } },
    select: { itemStyle: { areaColor: '#15803D' }, label: { color: '#FFFFFF' } },
    itemStyle: { borderColor: '#FFFFFF', borderWidth: 0.7, areaColor: '#EAF7EE' },
  }],
}));

function iconFor(metric: KpiMetric) {
  if (metric.icon === 'group') return Users;
  if (metric.icon === 'finance') return HandCoins;
  if (metric.icon === 'repayment') return TrendingUp;
  if (metric.icon === 'sprout') return Sprout;
  if (metric.icon === 'co2') return Building2;
  return Leaf;
}

function openKpiDetail(metric: KpiMetric) {
  if (metric.id === 'active-borrowers') {
    openBeneficiaries({ borrowerStatus: 'Active borrower' });
  }
  if (metric.id === 'farmers-trained') {
    openBeneficiaries({ trained: 'true' });
  }
}

function openTechnologyBeneficiaries(params: unknown) {
  const itemParams = chartParam(params);
  if (itemParams.name) openBeneficiaries({ technology: itemParams.name });
}

function regionNameFromSubmission(regionLabel: string) {
  return regionLabel.replace(/\s+Region$/, '');
}
</script>

<template>
  <DashboardPage>
    <header class="tacatdp-dashboard__header">
      <div class="tacatdp-dashboard__header-actions" aria-label="Dashboard controls">
        <button class="dashboard-control" type="button">
          <CalendarDays aria-hidden="true" />
          May 1 – May 31, 2025
          <ChevronDown aria-hidden="true" />
        </button>
        <button class="dashboard-control" type="button">
          <Filter aria-hidden="true" />
          Filters
        </button>
        <button class="dashboard-control dashboard-control--compact" type="button" aria-label="Export dashboard">
          <Download aria-hidden="true" />
        </button>
      </div>
    </header>

    <p class="dashboard-demo-note">Prototype dashboard using demonstration data for TACATDP visualisation design. Figures are not official CRDB Bank or Green Climate Fund statistics.</p>

    <section class="kpi-row" aria-label="TACATDP KPI summary">
      <KpiCard
        v-for="metric in dashboardKpis"
        :key="metric.id"
        :label="metric.label"
        :value="metric.value"
        :change="metric.change"
        :tone="metric.tone"
        :icon="iconFor(metric)"
        :class="{ 'kpi-card--clickable': metric.id === 'active-borrowers' || metric.id === 'farmers-trained' }"
        :tabindex="metric.id === 'active-borrowers' || metric.id === 'farmers-trained' ? 0 : undefined"
        :role="metric.id === 'active-borrowers' || metric.id === 'farmers-trained' ? 'button' : undefined"
        @click="openKpiDetail(metric)"
        @keydown.enter.prevent="openKpiDetail(metric)"
        @keydown.space.prevent="openKpiDetail(metric)"
      />
    </section>

    <section class="analytics-grid" aria-label="TACATDP analytics">
      <DashboardCard :span="3" title="Loan Portfolio by Type">
        <DashboardChart class="chart chart--donut" :option="loanPortfolioOption" autoresize />
        <template #footer>
          <a href="#reporting">View full report →</a>
        </template>
      </DashboardCard>

      <DashboardCard :span="5">
        <template #header>
          <div class="card-heading-row">
            <h2 id="disbursement-trend-title">Disbursement Trend (TZS)</h2>
            <span>Monthly</span>
          </div>
        </template>
        <DashboardChart class="chart chart--line" :option="disbursementTrendOption" autoresize />
      </DashboardCard>

      <DashboardCard :span="4" :row-span="2">
        <template #header>
          <div class="card-heading-row">
            <h2 id="regional-map-title">Loans by Region</h2>
            <button class="text-action" type="button">Reset map</button>
          </div>
        </template>
        <DashboardChart class="chart chart--map" :option="regionalMapOption" autoresize aria-label="Tanzania regional choropleth map showing prototype disbursement by region" />
        <button class="selected-region-card selected-region-card--action" type="button" @click="openBeneficiaries({ region: selectedRegion.name })">
          <div>
            <span>Top Region</span>
            <strong>{{ selectedRegion.name }}</strong>
          </div>
          <div>
            <span>Disbursed</span>
            <strong>{{ selectedRegion.disbursedLabel }}</strong>
          </div>
          <div>
            <span>Loans</span>
            <strong>{{ selectedRegion.loans.toLocaleString() }}</strong>
          </div>
          <MapPinned aria-hidden="true" />
        </button>
      </DashboardCard>

      <DashboardCard :span="4" title="Technologies Financed">
        <DashboardChart class="chart chart--bars" :option="technologyOption" autoresize @click="openTechnologyBeneficiaries" />
        <template #footer>
          <a href="#/beneficiaries?source=dashboard">View full breakdown →</a>
        </template>
      </DashboardCard>

      <DashboardCard :span="4" title="Loan Performance">
        <DashboardChart class="chart chart--donut" :option="loanPerformanceOption" autoresize />
        <template #footer>
          <a href="#reporting">View portfolio quality →</a>
        </template>
      </DashboardCard>
    </section>

    <section class="insights-grid" aria-label="TACATDP monitoring insights">
      <DashboardCard :span="8" title="Climate Resilience Outcomes">
        <div class="outcome-grid">
          <section class="outcome-metric" :title="climateOutcomes[0].definition">
            <span class="outcome-metric__icon outcome-metric__icon--blue" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M12 2C8.7 6.1 6 9.7 6 13a6 6 0 0 0 12 0c0-3.3-2.7-6.9-6-11Z" /></svg>
            </span>
            <small>Area Under Improved<br>Practices (ha)</small>
            <strong>26,842</strong>
            <em>↑ 18% vs Apr</em>
          </section>
          <section class="outcome-metric" :title="climateOutcomes[1].definition">
            <span class="outcome-metric__icon outcome-metric__icon--green" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M12 21V10" /><path d="M12 13c-4.2 0-6.8-2.3-7.8-6.8C8.7 6.2 11 8.6 12 13Z" /><path d="M12 11c1-4.4 3.3-6.7 7.8-6.8C18.8 8.8 16.2 11 12 11Z" /></svg>
            </span>
            <small>Yield Increase<br>(Avg %)</small>
            <strong>28%</strong>
            <em>↑ 6pp vs Apr</em>
          </section>
          <section class="outcome-metric" :title="climateOutcomes[2].definition">
            <span class="outcome-metric__icon outcome-metric__icon--amber" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M7.5 7.5h9l2.2 11.5H5.3L7.5 7.5Z" /><path d="M9 7.5 10.2 4h3.6L15 7.5" /><path d="M12 17v-4" /><path d="M12 14.4c-1.8 0-2.9-1-3.4-2.9 2 .1 3.1 1 3.4 2.9Z" /><path d="M12 14.2c.5-1.8 1.6-2.7 3.4-2.7-.5 1.9-1.6 2.8-3.4 2.7Z" /></svg>
            </span>
            <small>Soil Fertility Improved<br>(Reports)</small>
            <strong>5,642</strong>
            <em>↑ 15% vs Apr</em>
          </section>
          <section class="outcome-metric" :title="climateOutcomes[3].definition">
            <span class="outcome-metric__icon outcome-metric__icon--teal" aria-hidden="true">
              <svg viewBox="0 0 30 24"><path d="M9 19h13.2a5.3 5.3 0 0 0 .8-10.5A7.1 7.1 0 0 0 9.8 6 5.8 5.8 0 0 0 9 19Z" /><text x="14.8" y="15.3" text-anchor="middle">CO₂</text></svg>
            </span>
            <small>tCO₂e Avoided<br>(Cumulative)</small>
            <strong>32,184</strong>
            <em>↑ 19% vs Apr</em>
          </section>
        </div>
      </DashboardCard>

      <DashboardCard :span="4" title="Training &amp; Capacity Building">
        <div class="training-grid">
          <div>
            <span>Farmers Trained</span>
            <strong class="training-value-with-icon">8,452 <Users aria-hidden="true" /></strong>
            <small>↑ 21% vs Apr</small>
          </div>
          <div>
            <span>Training Sessions</span>
            <strong>192</strong>
            <small>↑ 15% vs Apr</small>
          </div>
        </div>
        <template #footer>
          <a href="#reporting">View training report →</a>
        </template>
      </DashboardCard>

      <DashboardCard :span="6" title="Recent Data Submissions">
        <div class="submission-list">
          <button
            v-for="submission in recentSubmissions"
            :key="submission.region"
            class="submission-row"
            type="button"
            @click="openBeneficiaries({ region: regionNameFromSubmission(submission.region), submissionStatus: submission.status })"
          >
            <div>
              <strong>{{ submission.region }}</strong>
              <span>{{ submission.period }}</span>
            </div>
            <div>
              <span class="status-chip">{{ submission.status }}</span>
              <small>{{ submission.time }}</small>
            </div>
          </button>
        </div>
        <template #footer>
          <a href="#/beneficiaries?source=dashboard">View all submissions →</a>
        </template>
      </DashboardCard>

      <DashboardCard :span="6" variant="goal" title="Program Impact Goal">
        <template #background>
          <img class="goal-illustration" :src="programImpactFarmer" alt="">
        </template>
        <p class="programme-goal-copy">Increase the resilience of food crop farmers<br>to climate change through finance,<br>technology and capacity building.</p>
      </DashboardCard>
    </section>
  </DashboardPage>
</template>

<style scoped>
.tacatdp-dashboard__header,
.tacatdp-dashboard__header-actions,
.card-heading-row,
.selected-region-card,
.training-grid,
.submission-row {
  display: flex;
  align-items: center;
}

.tacatdp-dashboard__header {
  justify-content: flex-end;
  gap: var(--dash-space-4);
}

.dashboard-demo-note,
.card-heading-row span,
.donut-center span,
.selected-region-card span,
.selected-region-card small,
.training-grid span,
.submission-list span,
.submission-list small {
  color: var(--dash-muted);
}

.dashboard-demo-note {
  margin: 4px 0 0;
  font-size: 0.84rem;
}

.tacatdp-dashboard__header-actions {
  gap: var(--dash-space-3);
}

.dashboard-control {
  display: inline-flex;
  align-items: center;
  gap: var(--dash-space-2);
  min-height: 44px;
  padding: 0 var(--dash-space-4);
  border: 1px solid var(--dash-border);
  border-radius: 10px;
  background: #FFFFFF;
  color: var(--dash-text);
  font: inherit;
  font-weight: 700;
}

.dashboard-control svg {
  width: 18px;
  height: 18px;
}

.dashboard-control--compact {
  width: 44px;
  padding: 0;
  justify-content: center;
}

.kpi-card--clickable {
  cursor: pointer;
}

.kpi-card--clickable:focus-visible {
  outline: 3px solid rgba(21, 128, 61, 0.24);
  outline-offset: 3px;
}

.dashboard-demo-note {
  padding: var(--dash-space-2) var(--dash-space-3);
  border: 1px solid rgba(245, 158, 11, 0.28);
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.08);
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: var(--dash-space-4);
}

.analytics-grid,
.insights-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--dash-space-4);
}

.card-heading-row h2 {
  margin: 0;
  color: var(--dash-text);
  font-size: 0.98rem;
  white-space: nowrap;
}

a,
.text-action {
  color: var(--dash-dark);
  font-weight: 800;
  font-size: 0.8rem;
  text-decoration: none;
}

.text-action {
  border: 0;
  background: transparent;
  font: inherit;
  cursor: pointer;
}

.card-heading-row,
.selected-region-card {
  justify-content: space-between;
}

.chart {
  width: 100%;
}

.chart--donut,
.chart--line,
.chart--bars {
  min-height: 190px;
}

.chart--map {
  min-height: 360px;
}

.chart-with-center {
  position: relative;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  display: grid;
  transform: translate(-50%, -50%);
  text-align: center;
}

.donut-center span {
  font-size: 0.72rem;
}

.donut-center strong {
  font-size: 1.2rem;
}

.selected-region-card {
  width: 100%;
  gap: var(--dash-space-4);
  padding: var(--dash-space-3);
  border: 1px solid var(--dash-border);
  border-radius: 10px;
  background: #FFFFFF;
  color: inherit;
  font: inherit;
  text-align: left;
}

.selected-region-card--action {
  cursor: pointer;
}

.selected-region-card--action:focus-visible,
.submission-row:focus-visible {
  outline: 3px solid rgba(21, 128, 61, 0.24);
  outline-offset: 2px;
}

.selected-region-card div {
  display: grid;
  gap: 4px;
}

.selected-region-card svg {
  width: 30px;
  height: 30px;
  padding: 8px;
  border-radius: 50%;
  background: #EAF7EE;
  color: #064E3B;
}

.outcome-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--dash-space-3);
}

.outcome-metric {
  display: grid;
  gap: var(--dash-space-2);
  justify-items: start;
  min-width: 0;
}

.outcome-metric__icon {
  display: inline-grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-weight: 900;
}

.outcome-metric__icon svg {
  width: 28px;
  height: 28px;
  overflow: visible;
}

.outcome-metric__icon path {
  fill: currentColor;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.6;
}

.outcome-metric__icon text {
  fill: #064E3B;
  font-size: 7px;
  font-weight: 900;
}

.outcome-metric__icon--blue { background: #DBEAFE; color: #2563EB; }
.outcome-metric__icon--green { background: #DCFCE7; color: #15803D; }
.outcome-metric__icon--amber { background: #FEF3C7; color: #92400E; }
.outcome-metric__icon--teal { background: #CCFBF1; color: #0F766E; }

.outcome-metric strong,
.training-grid strong {
  font-size: 1.45rem;
}

.outcome-metric small,
.outcome-metric strong,
.outcome-metric em,
.training-grid span,
.training-grid strong,
.training-grid small,
.submission-list strong,
.submission-list span,
.submission-list small,
.dashboard-card h2 {
  white-space: nowrap;
}

.outcome-metric small {
  font-size: 0.62rem;
  line-height: 1.2;
}

.training-grid span {
  font-size: 0.68rem;
}

.outcome-metric em,
.training-grid small {
  color: #15803D;
  font-size: 0.76rem;
  font-style: normal;
  font-weight: 700;
}

.training-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
  gap: var(--dash-space-3);
  height: 100%;
}

.training-grid div {
  display: grid;
  align-content: center;
  gap: var(--dash-space-2);
  min-width: 0;
  padding: var(--dash-space-3);
  border: 1px solid var(--dash-border);
  border-radius: 10px;
  background: #F8FBF9;
}

.training-grid div:last-child {
  justify-items: end;
  text-align: right;
}

.training-value-with-icon {
  display: inline-flex !important;
  align-items: center;
  gap: var(--dash-space-2);
}

.training-value-with-icon svg {
  width: 24px;
  height: 24px;
  color: #15803D;
  stroke-width: 2.6;
}

.submission-list {
  display: grid;
  gap: var(--dash-space-3);
}

.submission-row {
  justify-content: space-between;
  gap: var(--dash-space-4);
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.submission-list div {
  display: grid;
  gap: 4px;
}

.submission-list div:last-child {
  justify-items: end;
  min-width: 86px;
}

.status-chip {
  display: inline-flex;
  justify-content: center;
  padding: 3px 8px;
  border-radius: 999px;
  background: #EAF7EE;
  color: #15803D !important;
  font-size: 0.72rem;
  font-weight: 800;
}

.programme-goal-copy {
  position: relative;
  z-index: 1;
  max-width: 18rem;
  margin: 0;
  color: var(--dash-text);
  font-size: 0.88rem;
  line-height: 1.45;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.65);
}

.goal-illustration {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center bottom;
  opacity: 0.92;
  pointer-events: none;
}

@media (max-width: 1280px) {
  .kpi-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .tacatdp-dashboard__header,
  .tacatdp-dashboard__header-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .kpi-row,
  .analytics-grid,
  .insights-grid,
  .outcome-grid {
    grid-template-columns: 1fr;
  }
}
</style>
