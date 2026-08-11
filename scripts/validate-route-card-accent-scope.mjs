#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const stylesPath = resolve(repoRoot, 'powerpages/webforms-spa/src/styles.css');
const assignedFormsPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');

const stylesSource = readFileSync(stylesPath, 'utf8');
const assignedFormsSource = readFileSync(assignedFormsPath, 'utf8');

function blockFor(selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = stylesSource.match(new RegExp(`${escaped}\\s*\\{([\\s\\S]*?)\\n\\}`));
  if (!match) {
    throw new Error(`Missing expected selector ${selector}.`);
  }
  return match[1];
}

function assertNoDecorativeRail(selector) {
  const block = blockFor(selector);
  if (/border-left\s*:/.test(block) || /box-shadow\s*:\s*inset\s+4px\s+0\s+0/.test(block)) {
    throw new Error(`${selector} must not use a decorative left accent rail; rails are limited to metric cards and semantic states.`);
  }
}

const plainRouteCards = [
  '.submit-progress-panel',
  '.route-header',
  '.project-command-card',
  '.form-section-header',
  '.access-detail-drawer',
  '.access-workflow-panel',
  '.access-user-card',
  '.record-detail-panel',
  '.connection-panel',
  '.pagination-bar',
];

for (const selector of plainRouteCards) {
  assertNoDecorativeRail(selector);
}

if (!stylesSource.includes('.project-card::before')) {
  throw new Error('Project list cards should keep their left shade for now.');
}

for (const forbiddenSelector of ['.form-card::before', '.data-card::before']) {
  if (stylesSource.includes(forbiddenSelector)) {
    throw new Error(`${forbiddenSelector} must not reintroduce decorative content-card rails.`);
  }
}

if (!stylesSource.includes('.metric-card--accent') || !/\.metric-card--accent\s*\{[\s\S]*?border-left\s*:\s*6px\s+solid\s+var\(--mt-color-brand\)/.test(stylesSource)) {
  throw new Error('Metric cards must keep the shared metric-card accent rail.');
}

const metricAccentCount = (assignedFormsSource.match(/class="metric-card metric-card--accent"/g) || []).length;
if (metricAccentCount < 4) {
  throw new Error(`Expected metric-card accent rails on route metric strips; found ${metricAccentCount}.`);
}

console.log('Route card accent scope validation passed.');
