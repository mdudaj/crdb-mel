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
import {
  climateOutcomes,
  dashboardKpis,
  disbursementTrend,
  loanPerformance,
  loanPortfolio,
  programmeGoal,
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
  core.registerMap('tanzania-adm1', tanzaniaAdm1 as never);
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
    map: 'tanzania-adm1',
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
  <section class="tacatdp-dashboard" aria-labelledby="tacatdp-dashboard-title">
    <header class="tacatdp-dashboard__header">
      <div>
        <h1 id="tacatdp-dashboard-title">Dashboard</h1>
        <p>Monitoring sustainability outcomes and loan performance across Tanzania.</p>
      </div>
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
      <article v-for="metric in dashboardKpis" :key="metric.id" class="kpi-card">
        <span class="kpi-card__icon" :class="`kpi-card__icon--${metric.tone}`">
          <component :is="iconFor(metric)" aria-hidden="true" />
        </span>
        <div>
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <small>↑ {{ metric.change }}</small>
        </div>
      </article>
    </section>

    <section class="analytics-grid" aria-label="TACATDP analytics">
      <article class="dashboard-card dashboard-card--span-4" aria-labelledby="loan-portfolio-title">
        <h2 id="loan-portfolio-title">Loan Portfolio by Type</h2>
        <div class="chart-with-center">
          <DashboardChart class="chart chart--donut" :option="loanPortfolioOption" autoresize />
          <div class="donut-center">
            <span>Total</span>
            <strong>12,458</strong>
          </div>
        </div>
        <a href="#reporting">View full report →</a>
      </article>

      <article class="dashboard-card dashboard-card--span-4" aria-labelledby="disbursement-trend-title">
        <div class="card-heading-row">
          <h2 id="disbursement-trend-title">Disbursement Trend (TZS)</h2>
          <span>Monthly</span>
        </div>
        <DashboardChart class="chart chart--line" :option="disbursementTrendOption" autoresize />
      </article>

      <article class="dashboard-card dashboard-card--span-4 dashboard-card--map" aria-labelledby="regional-map-title">
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
      </article>

      <article class="dashboard-card dashboard-card--span-4" aria-labelledby="technologies-title">
        <h2 id="technologies-title">Technologies Financed</h2>
        <DashboardChart class="chart chart--bars" :option="technologyOption" autoresize />
        <a href="#reporting">View full breakdown →</a>
      </article>

      <article class="dashboard-card dashboard-card--span-4" aria-labelledby="loan-performance-title">
        <h2 id="loan-performance-title">Loan Performance</h2>
        <div class="chart-with-center">
          <DashboardChart class="chart chart--donut" :option="loanPerformanceOption" autoresize />
          <div class="donut-center">
            <span>Total Loans</span>
            <strong>12,458</strong>
          </div>
        </div>
        <a href="#reporting">View portfolio quality →</a>
      </article>

      <article class="dashboard-card dashboard-card--span-4 dashboard-card--outcomes" aria-labelledby="climate-outcomes-title">
        <h2 id="climate-outcomes-title">Climate Resilience Outcomes</h2>
        <div class="outcome-grid">
          <section v-for="outcome in climateOutcomes" :key="outcome.label" class="outcome-metric" :title="outcome.definition">
            <span :class="`outcome-metric__icon outcome-metric__icon--${outcome.tone}`">{{ outcome.icon === 'co2' ? 'CO₂' : '●' }}</span>
            <small>{{ outcome.label }}</small>
            <strong>{{ outcome.value }}</strong>
            <em>↑ {{ outcome.change }}</em>
          </section>
        </div>
      </article>

      <article class="dashboard-card dashboard-card--span-3" aria-labelledby="training-title">
        <h2 id="training-title">Training &amp; Capacity Building</h2>
        <div class="training-grid">
          <div>
            <span>Farmers Trained</span>
            <strong>8,452</strong>
            <small>↑ 21% vs Apr</small>
          </div>
          <div>
            <span>Training Sessions</span>
            <strong>192</strong>
            <small>↑ 15% vs Apr</small>
          </div>
        </div>
        <a href="#reporting">View training report →</a>
      </article>

      <article class="dashboard-card dashboard-card--span-3" aria-labelledby="submissions-title">
        <h2 id="submissions-title">Recent Data Submissions</h2>
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
      </article>

      <article class="dashboard-card dashboard-card--span-2 programme-goal" aria-labelledby="goal-title">
        <h2 id="goal-title">Programme Impact Goal</h2>
        <p>{{ programmeGoal }}</p>
        <div class="goal-illustration" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </article>
    </section>

    <footer class="dashboard-status-footer">
      <div>
        <span>Last updated: May 31, 2025 10:45 AM</span>
        <span class="sync-dot" aria-hidden="true"></span>
        <span>Data synced</span>
      </div>
      <span>© 2025 CRDB Bank — Sustainable Finance Unit. All rights reserved.</span>
    </footer>
  </section>
</template>

<style scoped>
.tacatdp-dashboard {
  --dash-dark: #064E3B;
  --dash-primary: #15803D;
  --dash-positive: #16A34A;
  --dash-bg: #F5F7F6;
  --dash-text: #17211C;
  --dash-muted: #64706A;
  --dash-border: #E3E8E5;
  display: grid;
  gap: 18px;
  min-height: calc(100vh - 126px);
  padding: 24px;
  background: var(--dash-bg);
  color: var(--dash-text);
}

.tacatdp-dashboard__header,
.tacatdp-dashboard__header-actions,
.card-heading-row,
.dashboard-status-footer,
.selected-region-card,
.training-grid,
.submission-list section {
  display: flex;
  align-items: center;
}

.tacatdp-dashboard__header {
  justify-content: space-between;
  gap: 20px;
}

.tacatdp-dashboard__header h1 {
  margin: 0;
  font-size: 1.55rem;
}

.tacatdp-dashboard__header p,
.dashboard-demo-note,
.dashboard-card span,
.dashboard-card small {
  color: var(--dash-muted);
}

.tacatdp-dashboard__header p,
.dashboard-demo-note {
  margin: 4px 0 0;
  font-size: 0.84rem;
}

.tacatdp-dashboard__header-actions {
  gap: 12px;
}

.dashboard-control {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 0 16px;
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
  padding: 10px 14px;
  border: 1px solid rgba(245, 158, 11, 0.28);
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.08);
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.kpi-card,
.dashboard-card {
  border: 1px solid var(--dash-border);
  border-radius: 12px;
  background: #FFFFFF;
  box-shadow: 0 8px 18px rgba(6, 78, 59, 0.06);
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 112px;
  padding: 18px;
}

.kpi-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 54px;
  height: 54px;
  border-radius: 50%;
}

.kpi-card__icon svg {
  width: 25px;
  height: 25px;
}

.kpi-card__icon--green { background: #EAF7EE; color: #15803D; }
.kpi-card__icon--blue { background: #DBEAFE; color: #2563EB; }
.kpi-card__icon--amber { background: #FEF3C7; color: #B45309; }
.kpi-card__icon--purple { background: #EDE9FE; color: #7C3AED; }

.kpi-card span,
.kpi-card small {
  display: block;
  font-size: 0.78rem;
}

.kpi-card strong {
  display: block;
  margin: 6px 0;
  font-size: 1.42rem;
  letter-spacing: -0.03em;
}

.kpi-card small {
  color: #15803D;
  font-weight: 700;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 14px;
}

.dashboard-card {
  display: grid;
  gap: 12px;
  align-content: start;
  min-height: 196px;
  padding: 16px;
}

.dashboard-card--span-2 { grid-column: span 2; }
.dashboard-card--span-3 { grid-column: span 3; }
.dashboard-card--span-4 { grid-column: span 4; }
.dashboard-card--map {
  grid-row: span 2;
  min-height: 470px;
}

.dashboard-card h2 {
  margin: 0;
  color: var(--dash-text);
  font-size: 0.98rem;
}

.dashboard-card a,
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
.selected-region-card,
.dashboard-status-footer {
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
  gap: 16px;
  padding: 14px;
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
  gap: 12px;
}

.outcome-metric {
  display: grid;
  gap: 7px;
}

.outcome-metric__icon {
  display: inline-grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
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

.outcome-metric em,
.training-grid small {
  color: #15803D;
  font-size: 0.76rem;
  font-style: normal;
  font-weight: 700;
}

.training-grid {
  align-items: stretch;
  gap: 18px;
}

.training-grid div {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.submission-list {
  display: grid;
  gap: 12px;
}

.submission-list section {
  justify-content: space-between;
  gap: 12px;
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

.programme-goal {
  overflow: hidden;
  background: linear-gradient(180deg, #FFFFFF 0%, #EAF7EE 100%);
}

.programme-goal p {
  margin: 0;
  color: var(--dash-text);
  font-size: 0.82rem;
  line-height: 1.55;
}

.goal-illustration {
  position: relative;
  min-height: 82px;
  margin: 4px -16px -16px;
  background: linear-gradient(135deg, rgba(21, 128, 61, 0.18), rgba(6, 78, 59, 0.24));
}

.goal-illustration span {
  position: absolute;
  bottom: 0;
  width: 45%;
  height: 56px;
  border-radius: 50% 50% 0 0;
  background: rgba(21, 128, 61, 0.25);
}

.goal-illustration span:nth-child(1) { left: -8%; }
.goal-illustration span:nth-child(2) { left: 26%; height: 70px; }
.goal-illustration span:nth-child(3) { right: -10%; height: 60px; }

.dashboard-status-footer {
  gap: 16px;
  padding: 10px 6px 0;
  color: var(--dash-muted);
  font-size: 0.78rem;
}

.dashboard-status-footer div {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.sync-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #15803D;
}

@media (max-width: 1280px) {
  .kpi-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dashboard-card--span-2,
  .dashboard-card--span-3,
  .dashboard-card--span-4 {
    grid-column: span 6;
  }

  .dashboard-card--map {
    grid-column: span 12;
  }
}

@media (max-width: 760px) {
  .tacatdp-dashboard {
    padding: 14px;
  }

  .tacatdp-dashboard__header,
  .tacatdp-dashboard__header-actions,
  .dashboard-status-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .kpi-row,
  .analytics-grid,
  .outcome-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-card--span-2,
  .dashboard-card--span-3,
  .dashboard-card--span-4,
  .dashboard-card--map {
    grid-column: span 1;
  }
}
</style>
