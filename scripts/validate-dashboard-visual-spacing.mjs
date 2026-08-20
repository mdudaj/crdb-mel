#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const chartOptionsPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/chartOptions.ts');
const dashboardCardPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/DashboardCard.vue');
const kpiCardPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/KpiCard.vue');
const dashboardPagePath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/TacatdpDashboardPage.vue');
const projectionPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/tacatdpBaselineProjection.ts');
const apiClientPath = resolve(repoRoot, 'powerpages/webforms-spa/src/powerpages-api/client.ts');
const source = readFileSync(chartOptionsPath, 'utf8');
const dashboardCardSource = readFileSync(dashboardCardPath, 'utf8');
const kpiCardSource = readFileSync(kpiCardPath, 'utf8');
const dashboardPageSource = readFileSync(dashboardPagePath, 'utf8');
const projectionSource = readFileSync(projectionPath, 'utf8');
const apiClientSource = readFileSync(apiClientPath, 'utf8');

function assertIncludes(fragment, message) {
  if (!source.includes(fragment)) {
    throw new Error(message);
  }
}

function readNumberConstant(name) {
  const match = source.match(new RegExp(`export const ${name} = (\\d+);`));
  if (!match) {
    throw new Error(`Missing numeric constant ${name}.`);
  }
  return Number(match[1]);
}

const gridLeft = readNumberConstant('DISBURSEMENT_TREND_GRID_LEFT');
const pointLabelDistance = readNumberConstant('DISBURSEMENT_TREND_POINT_LABEL_DISTANCE');

if (gridLeft < 64) {
  throw new Error(`Disbursement Trend grid left gutter is ${gridLeft}px; expected at least 64px to keep point labels clear of y-axis labels.`);
}

if (pointLabelDistance < 12) {
  throw new Error(`Disbursement Trend point label distance is ${pointLabelDistance}px; expected at least 12px.`);
}

assertIncludes('containLabel: true', 'Disbursement Trend grid must keep containLabel enabled so axis labels are reserved inside layout.');
assertIncludes('boundaryGap: true', 'Disbursement Trend x-axis must keep boundaryGap enabled so the first point label does not sit on the y-axis gutter.');
assertIncludes("name: 'TZS, billions'", 'Disbursement Trend must show the unit once as the y-axis name.');
assertIncludes("formatter: '{value}'", 'Disbursement Trend y-axis tick labels must remain plain numbers; do not repeat the unit on every tick.');
assertIncludes('margin: 12', 'Disbursement Trend y-axis labels must keep a margin from the plotting area.');
assertIncludes("position: 'top'", 'Disbursement Trend point labels must be positioned above points, not left/default.');
assertIncludes('hideOverlap: true', 'Disbursement Trend must keep labelLayout.hideOverlap enabled.');
assertIncludes('right: 24', 'Disbursement Trend right gutter must reserve room for the final point label.');

if (dashboardCardSource.includes('.dashboard-card::before') || dashboardCardSource.includes('--dashboard-card-accent')) {
  throw new Error('DashboardCard must not render the metric accent rail; dashboard rails belong only on KPI summary cards.');
}

if (!kpiCardSource.includes('.kpi-card::before') || !kpiCardSource.includes('--kpi-card-accent')) {
  throw new Error('KpiCard must keep the reusable left accent rail and accent token for dashboard metric cards.');
}

if (/axisLabel:\s*{[\s\S]*formatter:\s*['"`]{value}B['"`]/.test(source)) {
  throw new Error('Disbursement Trend y-axis must not repeat B on every tick; use the unit label instead.');
}

if (!dashboardPageSource.includes('object-fit: fill;')) {
  throw new Error('Program Impact Goal illustration must fill the full card background plane so it does not render as a small contained image.');
}

if (dashboardPageSource.includes('object-fit: cover;')) {
  throw new Error('Program Impact Goal illustration must not use object-fit: cover; it crops the supplied farmer image.');
}

if (!dashboardPageSource.includes('object-position: center center;')) {
  throw new Error('Program Impact Goal illustration must stay centered when filling the card background plane.');
}

if (!/\.programme-goal-copy\s*{[\s\S]*background:\s*linear-gradient/.test(dashboardPageSource)) {
  throw new Error('Program Impact Goal copy must keep a subtle scrim for readability over the illustration.');
}

for (const fragment of [
  'Live projection:',
  'Baseline Records',
  'Rows',
  'Loan Amount',
  'Baseline loans',
  'Farmers Trained',
  'Baseline',
  'tCO₂e Avoided',
  'Projection',
  'Verify',
  "changeDirection: 'neutral'",
  'Demo data: dashboard visual design only',
  'flex-wrap: wrap;',
  'border-radius: 999px;',
]) {
  if (!dashboardPageSource.includes(fragment)) {
    throw new Error(`Dashboard live KPI projection must include conservative ${fragment} state.`);
  }
}

for (const fragment of [
  'dashboardRegionMetrics',
  'dashboardTechnologyFinancing',
  'dashboardDisbursementTrend',
  'dashboardRecentSubmissions',
  'dashboardLoanPortfolio',
  'loanPortfolioTitle',
  'Loan Financing by Stage',
  'stage selections',
  'regionData.value',
  'Reported</span>',
]) {
  if (!dashboardPageSource.includes(fragment)) {
    throw new Error(`Dashboard live projection must drive regional/map/chart/list data through ${fragment}.`);
  }
}

if (!dashboardPageSource.includes('calculateTacatdpBaselineProjection') || !dashboardPageSource.includes('liveBaselineProjection')) {
  throw new Error('Dashboard must calculate KPI projections from imported baseline report rows.');
}

if (!dashboardPageSource.includes('api.listDashboardSubmissionReportRows({ maxRows: 1000 })')) {
  throw new Error('Dashboard live KPI projection must page through report rows up to the prototype dashboard limit, not only read the first page.');
}

for (const fragment of [
  'export function calculateTacatdpBaselineProjection',
  'DIESEL_KG_CO2E_PER_LITRE = 2.68',
  'ACRE_TO_HECTARE = 0.404686',
  'annualTco2eAvoided',
  'improvedHectares',
  'farmersTrained',
  'femaleTrained',
  'maleTrained',
  'femaleParticipationPct',
  'youthParticipationPct',
  'genderResponsiveRecords',
  'improvedReports',
  'reportedLoanAmountTzs',
  'loanPortfolio: NamedValue[]',
  'regions: RegionMetric[]',
  'technologies: NamedValue[]',
  'disbursementTrend: TrendPoint[]',
  'recentSubmissions: RecentSubmission[]',
  'TECHNOLOGY_PATTERNS',
  'LOAN_STAGE_ROOT_PREFIX',
  'buildRegions',
  'buildLoanPortfolioValues',
  'buildTechnologyValues',
  'buildTrend',
  'buildRecentSubmissions',
  'readSelectedLoanStages',
  'readTruthy',
]) {
  if (!projectionSource.includes(fragment)) {
    throw new Error(`Baseline KPI projection helper is missing required calculation fragment: ${fragment}`);
  }
}

if (!apiClientSource.includes('async listDashboardSubmissionReportRows') || !apiClientSource.includes('maxRows ?? 1000')) {
  throw new Error('Power Pages API client must expose a bounded dashboard report-row reader for automatic KPI projection.');
}

if (!apiClientSource.includes('parsed.root') || !apiClientSource.includes('buildBaselineRootAnswersJson')) {
  throw new Error('Baseline report-row projection must preserve bridge asset root answers in mp_rootanswersjson.');
}

for (const fragment of [
  'Number of MALE farmers trained',
  'Number of FEMALE farmers trained',
  'Number of MALE Youth farmers trained',
  'Number of FEMALE Youth farmers trained',
]) {
  if (!projectionSource.includes(fragment)) {
    throw new Error(`Training projection must match imported XLSX label payloads, not only XLSForm technical names: missing ${fragment}.`);
  }
}

if (projectionSource.includes('/farmers?.*trained/i') || projectionSource.includes('/youth.*trained/i')) {
  throw new Error('Training projection must not use broad trained regexes; they can read male/female fields as total fields.');
}

if (dashboardPageSource.includes('May 1 – May 31, 2025')) {
  throw new Error('Dashboard must not show the old prototype May 2025 date range once live baseline projection is enabled.');
}

if (!dashboardPageSource.includes('Reporting period awaiting live data')) {
  throw new Error('Dashboard must show a neutral reporting-period awaiting state until real reporting-period metadata exists.');
}

for (const fragment of [
  '__dashboardAggregates',
  'buildBaselineDashboardAggregates',
  'loan_repeat',
  'normalizeBaselineLoanYear',
  'excelSerialDateYear',
]) {
  if (!apiClientSource.includes(fragment)) {
    throw new Error(`Baseline import projection must enrich report rows for dashboard aggregates: missing ${fragment}.`);
  }
}

if (!kpiCardSource.includes("changeDirection?: 'up' | 'neutral'") || !kpiCardSource.includes("changeDirection === 'up'")) {
  throw new Error('KpiCard must support neutral helper text so status metadata is not shown as a positive trend.');
}

if (!kpiCardSource.includes('text-overflow: ellipsis;') || !kpiCardSource.includes(':title="change"') || !kpiCardSource.includes(':title="label"') || !kpiCardSource.includes(':title="value"')) {
  throw new Error('KpiCard text must fail safely with ellipsis and full hover/title context instead of visibly clipping partial words.');
}

if (!kpiCardSource.includes('line-height: 1.25;') || !kpiCardSource.includes('line-height: 1.18;')) {
  throw new Error('KpiCard label/value/helper text must keep explicit line-height to avoid cropped characters.');
}

if (!kpiCardSource.includes('flex: 1 1 auto;') || !kpiCardSource.includes('flex: 0 0 44px;')) {
  throw new Error('KpiCard content must reserve more horizontal space by using flexible text content and compact icon sizing.');
}

if (dashboardPageSource.includes('Training Sessions') || dashboardPageSource.includes('<strong>192</strong>') || dashboardPageSource.includes('Prototype pending')) {
  throw new Error('Training & Capacity Building card must not show unsupported prototype training sessions after baseline import projection exists.');
}

for (const fragment of [
  'Female Participation',
  'Youth Participation',
  'Gender Content',
  'dashboardTrainingMetrics',
]) {
  if (!dashboardPageSource.includes(fragment)) {
    throw new Error(`Training & Capacity Building card must expose baseline-supported training breakdown: missing ${fragment}.`);
  }
}

console.log('Dashboard visual spacing validation passed.');
