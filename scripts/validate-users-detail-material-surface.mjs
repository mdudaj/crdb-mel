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
  '.material-detail-surface',
  '.material-detail-header',
  '.material-detail-section',
  '.material-detail-list',
  '.material-detail-row',
  '.material-drawer-actions',
]) {
  assertIncludes(stylesSource, sharedClass, `Shared Material detail CSS missing: ${sharedClass}`);
}

for (const fragment of [
  'class="material-detail-surface access-detail-drawer"',
  'role="dialog"',
  'aria-modal="true"',
  'aria-labelledby="access-detail-title"',
  'class="material-detail-header access-drawer-header"',
  'class="material-detail-list access-detail-list"',
  'class="material-detail-row"',
  'class="material-detail-section access-assignment-list"',
  'class="material-row access-assignment-row" tabindex="0"',
  'class="material-detail-section access-drawer-activity"',
  'class="material-row access-activity-row access-activity-row--compact" tabindex="0"',
  'class="material-drawer-actions access-workflow-actions"',
]) {
  assertIncludes(viewSource, fragment, `Users detail drawer missing Material detail fragment: ${fragment}`);
}

if (!packageJson.scripts?.['test:material']?.includes('validate-users-detail-material-surface.mjs')) {
  throw new Error('test:material must run the users detail Material surface validator.');
}

console.log('Users detail Material surface validation passed.');
