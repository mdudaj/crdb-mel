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

for (const sharedClass of [
  '.material-detail-section',
  '.material-detail-header',
  '.material-detail-list',
  '.material-detail-row',
  '.material-row:hover',
  '.material-drawer-actions',
]) {
  assertIncludes(stylesSource, sharedClass, `Shared Material secondary-surface CSS missing: ${sharedClass}`);
}

for (const fragment of [
  'class="material-detail-section record-detail-panel"',
  'class="material-detail-header record-detail-header"',
  'class="material-detail-list answer-list"',
  'class="material-detail-row answer-row"',
  'class="material-detail-section export-create-panel"',
  'class="material-detail-section named-export-list"',
  'class="material-row named-export-row" tabindex="0"',
  'class="material-detail-section connection-panel"',
  'class="material-detail-section powerbi-steps"',
  'class="material-detail-section powerbi-table-list"',
  'class="material-row powerbi-table-row" tabindex="0"',
  'class="material-detail-list access-authorization-list"',
  'class="material-row access-readiness-row" tabindex="0"',
  'class="material-detail-list access-preview-list"',
  'class="material-detail-list manual-invitation-grid"',
  'class="material-drawer-actions access-workflow-actions"',
]) {
  assertIncludes(viewSource, fragment, `Secondary project/access surface missing Material abstraction: ${fragment}`);
}

if (!packageJson.scripts?.['test:material']?.includes('validate-secondary-material-surfaces.mjs')) {
  throw new Error('test:material must run the secondary Material surfaces validator.');
}

console.log('Secondary Material surfaces validation passed.');
