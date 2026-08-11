#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const viewPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');
const stylesPath = resolve(repoRoot, 'powerpages/webforms-spa/src/styles.css');
const packagePath = resolve(repoRoot, 'powerpages/webforms-spa/package.json');

const viewSource = readFileSync(viewPath, 'utf8');
const stylesSource = readFileSync(stylesPath, 'utf8');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));

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

assertIncludes(viewSource, 'activeView === \'reporting\'', 'Reporting route must remain backed by the reporting view.');
assertIncludes(viewSource, 'class="route-status-strip"', 'Reporting route must keep its metric summary strip.');
assertIncludes(viewSource, 'class="material-list-surface reporting-list-surface"', 'Reporting route must group table and empty state inside one shared Material-style list surface.');
assertIncludes(viewSource, 'aria-labelledby="reporting-projects-title"', 'Reporting list surface must be labelled by its visible heading.');
assertIncludes(viewSource, 'id="reporting-projects-title"', 'Reporting list must expose a stable visible heading.');
assertIncludes(viewSource, 'class="material-surface-header reporting-list-header"', 'Reporting list must use a stable shared list header anatomy.');
assertIncludes(viewSource, 'Open assigned project reporting areas for data review, governed CSV exports, and Power BI setup guidance.', 'Reporting list must describe its operational scope.');
assertIncludes(viewSource, 'class="material-count-chip reporting-list-count"', 'Reporting list must show a visible workspace count chip.');
assertIncludes(viewSource, '{{ reportingProjectRows.length }} workspace{{ reportingProjectRows.length === 1 ? \'\' : \'s\' }}', 'Reporting count chip must reflect reporting workspaces.');

assertIncludes(viewSource, 'class="responsive-table material-table reporting-table"', 'Reporting desktop view must remain a semantic table surface.');
assertIncludes(viewSource, '<caption class="sr-only">Reporting workspaces with project name, form count, projected record count, last updated date, projection status, and actions.</caption>', 'Reporting table must include an accessible caption.');
for (const column of ['Project', 'Forms', 'Records', 'Last updated', 'Projection', 'Actions']) {
  assertPattern(viewSource, new RegExp(`<th scope="col">${column}</th>`), `Reporting table must keep ${column} column header.`);
}
assertIncludes(viewSource, '<tr v-for="row in reportingProjectRows" :key="`reporting:${row.project.id}`" tabindex="0">', 'Reporting rows must be keyboard reachable.');
assertIncludes(viewSource, 'class="reporting-table__number"', 'Reporting numeric columns must use the numeric alignment class.');
assertIncludes(viewSource, 'state-chip--warning', 'Reporting projection status must retain a warning tone path.');
assertIncludes(viewSource, 'state-chip--success', 'Reporting projection status must retain a success tone path.');
assertIncludes(viewSource, 'aria-label="Open project data"', 'Reporting table must keep the Data action.');
assertIncludes(viewSource, 'aria-label="Open exports"', 'Reporting table must keep the Exports action.');
assertIncludes(viewSource, 'aria-label="Open Power BI"', 'Reporting table must keep the Power BI action.');
assertIncludes(viewSource, 'reporting-empty-state', 'Reporting route must keep a scoped empty state.');

assertIncludes(stylesSource, '.material-list-surface', 'Shared Material list surface styles must exist.');
assertIncludes(stylesSource, '.material-surface-header', 'Shared Material list header styles must exist.');
assertIncludes(stylesSource, '.material-count-chip', 'Shared Material count chip styles must exist.');
assertIncludes(stylesSource, '.material-table tbody tr:hover', 'Reporting table rows must use shared hover/focus feedback.');
assertIncludes(stylesSource, '.reporting-table__number', 'Reporting numeric alignment styles must exist.');
assertIncludes(stylesSource, '.reporting-empty-state', 'Reporting scoped empty-state styles must exist.');

if (!packageJson.scripts?.['test:material']?.includes('validate-reporting-material-list.mjs')) {
  throw new Error('test:material must run the Reporting Material list validator.');
}

console.log('Reporting Material list validation passed.');
