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

assertIncludes(viewSource, 'activeView === \'records\'', 'Project detail route must remain backed by the records view.');
assertIncludes(viewSource, 'class="project-form-workspace"', 'Project detail route must keep the project workspace container.');
assertIncludes(viewSource, 'class="project-command-card"', 'Project detail route must keep the selected project command card.');
assertIncludes(viewSource, 'class="material-tabs"', 'Project detail route must keep Material-style section tabs.');

assertIncludes(viewSource, 'class="material-surface project-detail-surface data-table-panel"', 'Project Data tab must use the shared Material surface and project-detail alias.');
assertIncludes(viewSource, 'aria-labelledby="project-data-title"', 'Project Data surface must be labelled by its visible title.');
assertIncludes(viewSource, 'id="project-data-title"', 'Project Data title must expose a stable heading id.');
assertIncludes(viewSource, 'class="record-toolbar material-surface-header project-detail-surface__header"', 'Project Data toolbar must use the shared Material surface header anatomy.');
assertIncludes(viewSource, 'Submitted and projected records for the selected project form.', 'Project Data surface must explain its data scope.');
assertIncludes(viewSource, 'class="material-count-chip project-detail-count"', 'Project Data surface must show a visible record count chip.');
assertIncludes(viewSource, '{{ reportTotal }} record{{ reportTotal === 1 ? \'\' : \'s\' }}', 'Project Data count chip must reflect the filtered reporting total.');
assertIncludes(viewSource, 'aria-label="Search submitted data"', 'Project Data search must remain accessible.');

assertIncludes(viewSource, 'class="responsive-table material-table project-detail-table"', 'Project Data desktop view must remain a semantic table surface.');
assertIncludes(viewSource, '<caption class="sr-only">Reporting records with record name, version, updated date, review state, projection status, and row actions.</caption>', 'Project Data table must include an accessible caption.');
for (const column of ['Record', 'Version', 'Updated', 'Review', 'Projection', 'Actions']) {
  assertPattern(viewSource, new RegExp(`<th scope="col">${column}</th>`), `Project Data table must keep ${column} column header.`);
}
assertIncludes(viewSource, '<tr v-for="reportRow in reportRows" :key="reportRow.mp_submissionreportrowid" tabindex="0">', 'Project Data rows must be keyboard reachable.');
assertIncludes(viewSource, 'class="project-detail-table__number"', 'Project Data numeric columns must use the numeric alignment class.');
assertIncludes(viewSource, 'projectionStatusTone(reportRow.mp_projectionstatus)', 'Project Data projection state must use a text-labelled status-chip tone.');
assertIncludes(viewSource, 'function projectionStatusTone(value?: number): string', 'Projection status tone mapping must exist in source.');

assertIncludes(viewSource, 'class="material-surface project-detail-surface export-workspace"', 'Exports tab must use the shared Material surface.');
assertIncludes(viewSource, 'class="material-surface project-detail-surface powerbi-workspace"', 'Power BI tab must use the shared Material surface.');
assertIncludes(viewSource, 'class="material-detail-section record-detail-panel"', 'Project record detail panel must use the shared Material detail section abstraction.');
assertIncludes(viewSource, 'class="material-detail-list answer-list"', 'Project record answers must use the shared Material detail list abstraction.');
assertIncludes(viewSource, 'class="material-detail-row answer-row"', 'Project record answer rows must use the shared Material detail row abstraction.');
assertIncludes(viewSource, 'class="material-detail-section export-create-panel"', 'Project exports create panel must use the shared Material detail section abstraction.');
assertIncludes(viewSource, 'class="material-row named-export-row" tabindex="0"', 'Saved export rows must use the shared Material row abstraction.');
assertIncludes(viewSource, 'class="material-row powerbi-table-row" tabindex="0"', 'Power BI table rows must use the shared Material row abstraction.');

assertIncludes(stylesSource, '.material-surface', 'Shared Material surface styles must exist.');
assertIncludes(stylesSource, '.material-surface-header', 'Shared Material surface header styles must exist.');
assertIncludes(stylesSource, '.material-detail-section', 'Shared Material detail section styles must exist.');
assertIncludes(stylesSource, '.material-detail-list', 'Shared Material detail list styles must exist.');
assertIncludes(stylesSource, '.material-detail-row', 'Shared Material detail row styles must exist.');
assertIncludes(stylesSource, '.material-count-chip', 'Shared Material count chip styles must exist.');
assertIncludes(stylesSource, '.data-table-panel .project-detail-surface__header', 'Project detail Data header must support title, count, and search layout.');
assertIncludes(stylesSource, '.material-table tbody tr:hover', 'Project detail table rows must use shared hover/focus feedback.');
assertIncludes(stylesSource, '.project-detail-table__number', 'Project detail numeric alignment styles must exist.');

if (!packageJson.scripts?.['test:material']?.includes('validate-project-detail-material-surface.mjs')) {
  throw new Error('test:material must run the Project detail Material surface validator.');
}

console.log('Project detail Material surface validation passed.');
