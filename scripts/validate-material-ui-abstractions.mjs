#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const viewPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');
const beneficiariesPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/BeneficiariesView.vue');
const stylesPath = resolve(repoRoot, 'powerpages/webforms-spa/src/styles.css');
const packagePath = resolve(repoRoot, 'powerpages/webforms-spa/package.json');

const viewSource = readFileSync(viewPath, 'utf8');
const beneficiariesSource = readFileSync(beneficiariesPath, 'utf8');
const stylesSource = readFileSync(stylesPath, 'utf8');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));

function assertIncludes(source, fragment, message) {
  if (!source.includes(fragment)) {
    throw new Error(message);
  }
}

for (const sharedClass of [
  '.material-surface',
  '.material-list-surface',
  '.material-surface-header',
  '.material-count-chip',
  '.material-table tbody tr:hover',
  '.material-row:hover',
  '.material-card-footer',
]) {
  assertIncludes(stylesSource, sharedClass, `Shared Material abstraction missing CSS rule: ${sharedClass}`);
}

for (const routeFragment of [
  'class="material-list-surface project-list-surface"',
  'class="material-list-surface reporting-list-surface"',
  'class="material-list-surface access-list-surface"',
  'class="material-surface project-detail-surface data-table-panel"',
  'class="access-readiness-panel material-surface system-activity-surface"',
]) {
  assertIncludes(viewSource, routeFragment, `Route must use shared Material surface abstraction: ${routeFragment}`);
}

for (const headerFragment of [
  'class="material-surface-header project-list-header"',
  'class="material-surface-header reporting-list-header"',
  'class="material-surface-header access-list-header"',
  'class="record-toolbar material-surface-header project-detail-surface__header"',
]) {
  assertIncludes(viewSource, headerFragment, `Route must use shared Material header abstraction: ${headerFragment}`);
}

for (const countFragment of [
  'class="material-count-chip project-list-count"',
  'class="material-count-chip reporting-list-count"',
  'class="material-count-chip project-detail-count"',
  'class="material-count-chip access-list-count"',
]) {
  assertIncludes(viewSource, countFragment, `Route must use shared Material count chip abstraction: ${countFragment}`);
}

for (const tableFragment of [
  'class="responsive-table material-table reporting-table"',
  'class="responsive-table material-table project-detail-table"',
  'class="responsive-table material-table access-table"',
  'class="responsive-table material-table access-table activation-diagnostics-table system-activity-table"',
]) {
  assertIncludes(viewSource, tableFragment, `Route must use shared Material table abstraction: ${tableFragment}`);
}

assertIncludes(viewSource, 'class="material-row system-activity-row system-activity-row--material"', 'System Activity rows must use the shared Material row abstraction.');
assertIncludes(viewSource, 'class="material-card-footer project-card__footer"', 'Project cards must use the shared Material card footer abstraction.');

for (const beneficiaryFragment of [
  'class="material-list-surface beneficiary-list"',
  'class="material-surface-header beneficiary-list__header"',
  'class="material-count-chip beneficiary-list__count"',
  'class="beneficiary-table-wrap material-table"',
  'class="material-row" tabindex="0"',
  'class="material-row beneficiary-record-card"',
  'class="material-card-footer"',
]) {
  assertIncludes(beneficiariesSource, beneficiaryFragment, `Beneficiaries route must use shared Material abstraction: ${beneficiaryFragment}`);
}

if (!packageJson.scripts?.['test:material']?.includes('validate-material-ui-abstractions.mjs')) {
  throw new Error('test:material must run the shared Material UI abstraction validator.');
}

console.log('Shared Material UI abstraction validation passed.');
