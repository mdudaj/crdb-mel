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
const source = readFileSync(chartOptionsPath, 'utf8');
const dashboardCardSource = readFileSync(dashboardCardPath, 'utf8');
const kpiCardSource = readFileSync(kpiCardPath, 'utf8');
const dashboardPageSource = readFileSync(dashboardPagePath, 'utf8');

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
  'Live KPI projection:',
  'Baseline Records',
  'Live report projection',
  'Regions Covered',
  'From beneficiary profiles',
  'Training Data',
  'Not in minimal import',
  'Climate KPI',
  'Requires verification',
]) {
  if (!dashboardPageSource.includes(fragment)) {
    throw new Error(`Dashboard live KPI projection must include conservative ${fragment} state.`);
  }
}

if (!dashboardPageSource.includes('api.listSubmissionReportRows({ page: 1, pageSize: 10 })')) {
  throw new Error('Dashboard live KPI projection must read recent report rows, not only the total count.');
}

console.log('Dashboard visual spacing validation passed.');
