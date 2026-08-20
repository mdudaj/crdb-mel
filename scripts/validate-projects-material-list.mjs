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

assertIncludes(viewSource, 'activeView === \'projects\'', 'Projects route must remain backed by the projects view.');
assertIncludes(viewSource, 'class="material-list-surface project-list-surface"', 'Projects route must group header, loading, list, and empty state inside one shared Material-style list surface.');
assertIncludes(viewSource, 'aria-labelledby="projects-list-title"', 'Projects list surface must be labelled by its visible heading.');
assertIncludes(viewSource, 'id="projects-list-title"', 'Projects list must expose a stable visible heading.');
assertIncludes(viewSource, 'class="material-surface-header project-list-header"', 'Projects list must use the shared list header anatomy.');
assertIncludes(viewSource, 'class="material-count-chip project-list-count"', 'Projects list must show a visible assigned-project count chip.');
assertIncludes(viewSource, '{{ projectWorkspaces.length }} assigned', 'Projects count chip must reflect assigned projects.');
assertIncludes(viewSource, 'class="project-card project-card--entry project-card--material"', 'Projects list cards must use the Material project-card variant.');
assertIncludes(viewSource, 'tabindex="0"', 'Projects cards must be keyboard reachable.');
assertIncludes(viewSource, 'class="project-card__header"', 'Projects cards must have a stable header slot.');
assertIncludes(viewSource, 'class="project-card__content"', 'Projects cards must have a stable content slot.');
assertIncludes(viewSource, 'class="material-card-footer project-card__footer"', 'Projects cards must have a stable footer/action slot.');
assertIncludes(viewSource, '<span class="state-chip state-chip--success">Assigned</span>', 'Projects cards must show text-labelled assignment status, not color-only state.');
assertIncludes(viewSource, '<dt>Forms</dt>', 'Projects cards must expose assigned form count.');
assertIncludes(viewSource, '<dt>Local drafts</dt>', 'Projects cards must expose local draft count.');
assertIncludes(viewSource, 'Open project', 'Projects card action must use explicit action text.');
assertIncludes(viewSource, 'project-empty-state', 'Projects list must keep a scoped empty state.');

assertIncludes(stylesSource, '.material-list-surface', 'Shared Material list surface styles must exist.');
assertIncludes(stylesSource, '.material-surface-header', 'Shared Material list header styles must exist.');
assertIncludes(stylesSource, '.material-count-chip', 'Shared Material count chip styles must exist.');
assertIncludes(stylesSource, '.project-card--material', 'Projects Material card styles must exist.');
assertIncludes(stylesSource, '.project-card--material:hover', 'Projects Material cards must have hover/focus feedback.');
assertIncludes(stylesSource, '.project-card__header', 'Projects card header styles must exist.');
assertIncludes(stylesSource, '.project-card__content', 'Projects card content styles must exist.');
assertIncludes(stylesSource, '.material-card-footer', 'Shared Material card footer styles must exist.');
assertIncludes(stylesSource, '.project-empty-state', 'Projects scoped empty-state styles must exist.');

if (!packageJson.scripts?.['test:material']?.includes('validate-projects-material-list.mjs')) {
  throw new Error('test:material must run the Projects Material list validator.');
}

console.log('Projects Material list validation passed.');
