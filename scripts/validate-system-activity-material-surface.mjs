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

assertIncludes(viewSource, 'activeView === \'system-activity\'', 'System Activity route must remain backed by the system-activity view.');
assertIncludes(viewSource, 'v-if="!canManageAccess"', 'System Activity route must retain the administrator authorization gate.');
assertIncludes(viewSource, 'class="system-activity-workspace"', 'System Activity route must keep a bounded workspace container.');
assertIncludes(viewSource, 'class="access-metric-strip"', 'System Activity route must keep metric summary cards.');
assertIncludes(viewSource, 'aria-label="System Activity sections"', 'System Activity route must keep section tabs.');
assertIncludes(viewSource, 'class="access-readiness-panel material-surface system-activity-surface"', 'System health panel must use the shared Material surface class.');
assertIncludes(viewSource, 'class="access-activity-panel material-surface system-activity-surface"', 'Activity panels must use the shared Material surface class.');
assertIncludes(viewSource, 'class="material-row system-activity-row system-activity-row--material"', 'System Activity event rows must use the shared Material row class.');
assertPattern(viewSource, /material-row system-activity-row system-activity-row--material" tabindex="0"/, 'System Activity event rows must be keyboard reachable.');
assertIncludes(viewSource, 'systemActivityTone(event.severity)', 'System Activity events must use text-labelled status chip tones.');
assertIncludes(viewSource, '<strong>Next action</strong>', 'System Activity rows must keep explicit next-action content.');

assertIncludes(viewSource, 'class="responsive-table material-table access-table activation-diagnostics-table system-activity-table"', 'Activation diagnostics must use the shared Material table class.');
assertIncludes(viewSource, '<caption class="sr-only">Activation diagnostics with user identity, contact, email, invitation, redemption, external identity, web role, assignment, and next action.</caption>', 'Activation diagnostics table must include an accessible caption.');
for (const column of ['User', 'Contact', 'Email', 'Invitation', 'Redemption', 'Identity', 'Web role', 'Assignment', 'Next action']) {
  assertPattern(viewSource, new RegExp(`<th scope="col">${column}</th>`), `Activation diagnostics table must keep ${column} column header.`);
}
assertIncludes(viewSource, '<tr v-for="row in activationDiagnostics" :key="row.id" tabindex="0">', 'Activation diagnostics rows must be keyboard reachable.');
assertIncludes(viewSource, 'class="system-activity-table__number"', 'Activation diagnostics numeric assignment column must use numeric alignment.');
assertIncludes(viewSource, 'activationStateTone(row.externalIdentityStatus)', 'Activation diagnostics must keep external identity status tone.');
assertIncludes(viewSource, 'nextActionTone(row.nextAction)', 'Activation diagnostics must keep next-action status tone.');

assertIncludes(stylesSource, '.material-surface', 'Shared Material surface styles must exist.');
assertIncludes(stylesSource, '.material-row:hover', 'System Activity rows must use shared hover/focus feedback.');
assertIncludes(stylesSource, '.material-table tbody tr:hover', 'System Activity table rows must use shared hover/focus feedback.');
assertIncludes(stylesSource, '.system-activity-table__number', 'System Activity numeric table alignment styles must exist.');

if (!packageJson.scripts?.['test:material']?.includes('validate-system-activity-material-surface.mjs')) {
  throw new Error('test:material must run the System Activity Material surface validator.');
}

console.log('System Activity Material surface validation passed.');
