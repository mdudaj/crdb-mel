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
import type { ComposeOption } from 'echarts/core';
import type { BarSeriesOption, LineSeriesOption, MapSeriesOption, PieSeriesOption } from 'echarts/charts';
import type { GridComponentOption, LegendComponentOption, TooltipComponentOption, VisualMapComponentOption } from 'echarts/components';
import tanzaniaAdm1 from '../../assets/maps/tanzania-adm1.json';
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

type DashboardChartOption = ComposeOption<
  | BarSeriesOption
  | LineSeriesOption
  | MapSeriesOption
  | PieSeriesOption
  | GridComponentOption
  | LegendComponentOption
  | TooltipComponentOption
  | VisualMapComponentOption
>;

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
  tooltip: {
    trigger: 'item',
    formatter: (params: unknown) => {
      const itemParams = chartParam(params);
      const row = loanPortfolio.find((item) => item.name === itemParams.name);
      return `${itemParams.name}<br>${itemParams.value.toLocaleString()} loans (${itemParams.percent}%)<br>${row?.amount ?? 'Prototype amount'} disbursed`;
    },
  },
  legend: { orient: 'vertical', right: 0, top: 'middle', itemWidth: 9, itemHeight: 9 },
  series: [{
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['34%', '50%'],
    data: loanPortfolio.map((item) => ({ name: item.name, value: item.value, itemStyle: { color: item.color } })),
    label: { show: false },
  }],
}));

const disbursementTrendOption = computed<DashboardChartOption>(() => ({
  tooltip: { trigger: 'axis', valueFormatter: (value) => `TZS ${value}B` },
  grid: { left: 40, right: 18, top: 20, bottom: 28 },
  xAxis: { type: 'category', data: disbursementTrend.map((point) => point.month), boundaryGap: false },
  yAxis: { type: 'value', axisLabel: { formatter: '{value}B' }, splitLine: { lineStyle: { color: '#E3E8E5' } } },
  series: [{
    type: 'line',
    smooth: true,
    symbolSize: 8,
    data: disbursementTrend.map((point) => point.value),
    label: { show: true, formatter: ({ dataIndex }) => disbursementTrend[dataIndex].label, color: '#064E3B' },
    lineStyle: { color: '#15803D', width: 3 },
    itemStyle: { color: '#15803D' },
    areaStyle: { color: 'rgba(21, 128, 61, 0.14)' },
  }],
}));

const loanPerformanceOption = computed<DashboardChartOption>(() => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: unknown) => {
      const itemParams = chartParam(params);
      const row = loanPerformance.find((item) => item.name === itemParams.name);
      return `${itemParams.name}<br>${itemParams.value.toLocaleString()} loans (${itemParams.percent}%)<br>${row?.amount ?? 'Prototype outstanding principal'}`;
    },
  },
  legend: { orient: 'vertical', right: 0, top: 'middle', itemWidth: 9, itemHeight: 9 },
  series: [{
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['34%', '50%'],
    data: loanPerformance.map((item) => ({ name: item.name, value: item.value, itemStyle: { color: item.color } })),
    label: { show: false },
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
    min: 0,
    max: 22,
    right: 8,
    top: 78,
    text: ['>15B', '<1B'],
    itemWidth: 12,
    itemHeight: 86,
    calculable: false,
    inRange: { color: ['#EAF7EE', '#B7E4C7', '#74C69D', '#2F9E44', '#064E3B'] },
    textStyle: { color: '#64706A', fontSize: 11 },
  },
  series: [{
    type: 'map',
    map: 'tanzania-mainland-adm1',
    roam: false,
    nameProperty: 'shapeName',
    selectedMode: 'single',
    data: regionData,
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
      />
    </section>

    <section class="analytics-grid" aria-label="TACATDP analytics">
      <DashboardCard :span="3" title="Loan Portfolio by Type">
        <div class="chart-with-center">
          <DashboardChart class="chart chart--donut" :option="loanPortfolioOption" autoresize />
          <div class="donut-center">
            <span>Total</span>
            <strong>12,458</strong>
          </div>
        </div>
        <a href="#reporting">View full report →</a>
      </DashboardCard>

      <DashboardCard :span="5">
        <div class="card-heading-row">
          <h2 id="disbursement-trend-title">Disbursement Trend (TZS)</h2>
          <span>Monthly</span>
        </div>
        <DashboardChart class="chart chart--line" :option="disbursementTrendOption" autoresize />
      </DashboardCard>

      <DashboardCard :span="4" :row-span="2">
        <div class="card-heading-row">
          <h2 id="regional-map-title">Loans by Region</h2>
          <button class="text-action" type="button">Reset map</button>
        </div>
        <DashboardChart class="chart chart--map" :option="regionalMapOption" autoresize aria-label="Tanzania regional choropleth map showing prototype disbursement by region" />
        <div class="selected-region-card">
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
        </div>
      </DashboardCard>

      <DashboardCard :span="4" title="Technologies Financed">
        <DashboardChart class="chart chart--bars" :option="technologyOption" autoresize />
        <a href="#reporting">View full breakdown →</a>
      </DashboardCard>

      <DashboardCard :span="4" title="Loan Performance">
        <div class="chart-with-center">
          <DashboardChart class="chart chart--donut" :option="loanPerformanceOption" autoresize />
          <div class="donut-center">
            <span>Total Loans</span>
            <strong>12,458</strong>
          </div>
        </div>
        <a href="#reporting">View portfolio quality →</a>
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
        <a href="#reporting">View training report →</a>
      </DashboardCard>

      <DashboardCard :span="7" title="Recent Data Submissions">
        <div class="submission-list">
          <section v-for="submission in recentSubmissions" :key="submission.region">
            <div>
              <strong>{{ submission.region }}</strong>
              <span>{{ submission.period }}</span>
            </div>
            <div>
              <span class="status-chip">{{ submission.status }}</span>
              <small>{{ submission.time }}</small>
            </div>
          </section>
        </div>
        <a href="#records">View all submissions →</a>
      </DashboardCard>

      <DashboardCard :span="5" variant="goal" title="Program Impact Goal">
        <p class="programme-goal-copy">Increase the resilience of food crop farmers<br>to climate change through finance,<br>technology and capacity building.</p>
        <svg class="goal-illustration" viewBox="0 0 360 168" preserveAspectRatio="none" aria-hidden="true">
          <path class="goal-hill goal-hill--back" d="M0 78c44-32 81-32 126 0 38 27 80 28 122 0 43-28 75-26 112 0v90H0Z" />
          <path class="goal-hill goal-hill--mid" d="M0 100c52-40 94-38 143 0 42 32 81 34 125 4 35-25 63-25 92-5v69H0Z" />
          <path class="goal-hill goal-hill--front" d="M0 126c48-28 92-29 137-2 48 28 95 29 145 0 31-18 56-19 78-6v50H0Z" />
          <g class="goal-crops">
            <path d="M0 153c12-22 22-22 34 0M23 158c13-29 25-29 37 0M51 160c11-25 22-25 34 0M78 160c15-36 28-36 42 0M115 160c11-28 22-28 33 0M146 160c15-30 28-30 42 0M184 160c12-28 24-28 36 0M219 160c11-28 22-28 34 0M248 160c15-34 29-34 43 0M286 160c13-29 25-29 37 0M321 160c12-24 24-24 36 0" />
            <path d="M8 168v-30M20 168v-38M40 168v-34M65 168v-42M93 168v-46M125 168v-37M157 168v-43M191 168v-36M226 168v-43M258 168v-48M295 168v-39M330 168v-36" />
          </g>
          <g class="goal-farmer">
            <path class="goal-farmer__hat" d="M260 53c12-14 32-14 44 0l18 4c-21 9-53 9-80 0Z" />
            <circle cx="282" cy="65" r="9" />
            <path d="M270 76c16-4 30 1 42 15l-10 18c-12-13-25-19-39-16Z" />
            <path d="M265 91c-10 17-18 28-29 37l-8-8c11-8 19-19 28-34Z" />
            <path d="M302 108c5 18 8 35 8 52h-13c-1-16-4-31-10-45Z" />
            <path d="M282 111c-9 16-18 31-30 49h-14c13-18 24-36 32-54Z" />
            <path class="goal-hoe" d="M227 81 318 148" />
            <path class="goal-hoe" d="m216 75 16 12" />
          </g>
        </svg>
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
.submission-list section {
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
  left: 34%;
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
  gap: var(--dash-space-4);
  padding: var(--dash-space-3);
  border: 1px solid var(--dash-border);
  border-radius: 10px;
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
  align-items: stretch;
  gap: var(--dash-space-4);
}

.training-grid div {
  display: grid;
  gap: var(--dash-space-2);
  min-width: 0;
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

.submission-list section {
  justify-content: space-between;
  gap: var(--dash-space-3);
}

.submission-list div {
  display: grid;
  gap: 4px;
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
  margin: 0;
  color: var(--dash-text);
  font-size: 0.88rem;
  line-height: 1.45;
}

.goal-illustration {
  width: calc(100% + 32px);
  height: 154px;
  margin: -12px -16px -16px;
  align-self: end;
}

.goal-hill--back { fill: #D8F0DD; }
.goal-hill--mid { fill: #BFE5C8; }
.goal-hill--front { fill: #9ED4AE; }

.goal-crops path {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.goal-crops path:first-child {
  stroke: #1F7A31;
  stroke-width: 5;
}

.goal-crops path:last-child {
  stroke: #43A047;
  stroke-width: 3;
}

.goal-farmer {
  fill: #0F5C36;
}

.goal-farmer__hat {
  fill: #1F7A31;
}

.goal-hoe {
  fill: none;
  stroke: #064E3B;
  stroke-linecap: round;
  stroke-width: 4;
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
