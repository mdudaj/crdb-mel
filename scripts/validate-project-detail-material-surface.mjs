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

assertIncludes(viewSource, 'class="project-detail-surface data-table-panel"', 'Project Data tab must use the shared project-detail surface.');
assertIncludes(viewSource, 'aria-labelledby="project-data-title"', 'Project Data surface must be labelled by its visible title.');
assertIncludes(viewSource, 'id="project-data-title"', 'Project Data title must expose a stable heading id.');
assertIncludes(viewSource, 'class="record-toolbar project-detail-surface__header"', 'Project Data toolbar must use the project-detail surface header anatomy.');
assertIncludes(viewSource, 'Submitted and projected records for the selected project form.', 'Project Data surface must explain its data scope.');
assertIncludes(viewSource, 'class="project-detail-count"', 'Project Data surface must show a visible record count chip.');
assertIncludes(viewSource, '{{ reportTotal }} record{{ reportTotal === 1 ? \'\' : \'s\' }}', 'Project Data count chip must reflect the filtered reporting total.');
assertIncludes(viewSource, 'aria-label="Search submitted data"', 'Project Data search must remain accessible.');

assertIncludes(viewSource, 'class="responsive-table project-detail-table"', 'Project Data desktop view must remain a semantic table surface.');
assertIncludes(viewSource, '<caption class="sr-only">Reporting records with record name, version, updated date, review state, projection status, and row actions.</caption>', 'Project Data table must include an accessible caption.');
for (const column of ['Record', 'Version', 'Updated', 'Review', 'Projection', 'Actions']) {
  assertPattern(viewSource, new RegExp(`<th scope="col">${column}</th>`), `Project Data table must keep ${column} column header.`);
}
assertIncludes(viewSource, '<tr v-for="reportRow in reportRows" :key="reportRow.mp_submissionreportrowid" tabindex="0">', 'Project Data rows must be keyboard reachable.');
assertIncludes(viewSource, 'class="project-detail-table__number"', 'Project Data numeric columns must use the numeric alignment class.');
assertIncludes(viewSource, 'projectionStatusTone(reportRow.mp_projectionstatus)', 'Project Data projection state must use a text-labelled status-chip tone.');
assertIncludes(viewSource, 'function projectionStatusTone(value?: number): string', 'Projection status tone mapping must exist in source.');

assertIncludes(viewSource, 'class="project-detail-surface export-workspace"', 'Exports tab must use the project-detail surface.');
assertIncludes(viewSource, 'class="project-detail-surface powerbi-workspace"', 'Power BI tab must use the project-detail surface.');

assertIncludes(stylesSource, '.project-detail-surface', 'Project detail surface styles must exist.');
assertIncludes(stylesSource, '.project-detail-surface__header', 'Project detail surface header styles must exist.');
assertIncludes(stylesSource, '.project-detail-count', 'Project detail count chip styles must exist.');
assertIncludes(stylesSource, '.data-table-panel .project-detail-surface__header', 'Project detail Data header must support title, count, and search layout.');
assertIncludes(stylesSource, '.project-detail-table tbody tr:hover', 'Project detail table rows must have hover/focus feedback.');
assertIncludes(stylesSource, '.project-detail-table__number', 'Project detail numeric alignment styles must exist.');

if (!packageJson.scripts?.['test:material']?.includes('validate-project-detail-material-surface.mjs')) {
  throw new Error('test:material must run the Project detail Material surface validator.');
}

console.log('Project detail Material surface validation passed.');
