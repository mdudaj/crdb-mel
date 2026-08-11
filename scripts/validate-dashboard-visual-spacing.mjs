#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const chartOptionsPath = resolve(repoRoot, 'powerpages/webforms-spa/src/components/dashboard/chartOptions.ts');
const source = readFileSync(chartOptionsPath, 'utf8');

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

if (/axisLabel:\s*{[\s\S]*formatter:\s*['"`]{value}B['"`]/.test(source)) {
  throw new Error('Disbursement Trend y-axis must not repeat B on every tick; use the unit label instead.');
}

console.log('Dashboard visual spacing validation passed.');
