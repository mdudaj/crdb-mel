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

assertIncludes(viewSource, 'class="access-list-surface"', 'Users route must group toolbar, table/cards, and empty/loading states inside one Material-style list surface.');
assertIncludes(viewSource, 'aria-labelledby="access-users-title"', 'Users list surface must be labelled by its visible heading.');
assertIncludes(viewSource, 'id="access-users-title"', 'Users list must expose a stable visible heading.');
assertIncludes(viewSource, 'class="access-list-count"', 'Users list must show a visible filtered count chip.');
assertIncludes(viewSource, '{{ filteredAccessUsers.length }} shown', 'Users list count must reflect filtered rows, not only total users.');
assertIncludes(viewSource, 'class="access-toolbar"', 'Users list must keep visible filter/search controls.');
assertIncludes(viewSource, '<span>Role</span>', 'Users role filter must keep a visible label.');
assertIncludes(viewSource, 'aria-label="Search users"', 'Users search field must remain accessible.');

assertIncludes(viewSource, 'class="responsive-table access-table"', 'Users desktop view must remain a semantic table surface.');
assertIncludes(viewSource, '<caption class="sr-only">Portal users with contact state, role, project count, form count, access state, and row actions.</caption>', 'Users table must include an accessible caption.');
for (const column of ['User', 'Contact', 'Role', 'Projects', 'Forms', 'Access', 'Actions']) {
  assertPattern(viewSource, new RegExp(`<th scope="col">${column}</th>`), `Users table must keep ${column} column header.`);
}
assertIncludes(viewSource, 'tabindex="0"', 'Users table region and rows must remain keyboard reachable.');
assertIncludes(viewSource, 'class="access-table__number"', 'Users numeric columns must use the numeric alignment class.');
assertIncludes(viewSource, 'accessStatusTone(user.accessStatus)', 'Users access status must use text-labelled status chip tone.');
assertIncludes(viewSource, 'contactStateTone(user.contactState)', 'Users contact state must use text-labelled status chip tone.');

assertIncludes(viewSource, 'class="access-card-list"', 'Users mobile view must use stacked cards.');
assertIncludes(viewSource, 'class="access-user-card__header"', 'Users mobile cards must use stable leading identity and trailing status anatomy.');
assertIncludes(viewSource, '<dt>Projects</dt>', 'Users mobile cards must include project count.');
assertIncludes(viewSource, '<dt>Forms</dt>', 'Users mobile cards must include form count.');
assertIncludes(viewSource, 'access-empty-state', 'Users list must keep a scoped no-results state.');
assertIncludes(viewSource, 'class="loading-panel loading-panel--inline access-loading-state"', 'Users list must keep a scoped loading state.');

assertIncludes(stylesSource, '.access-list-surface', 'Users list surface styles must exist.');
assertIncludes(stylesSource, '.access-list-header', 'Users list header styles must exist.');
assertIncludes(stylesSource, '.access-list-count', 'Users list count chip styles must exist.');
assertIncludes(stylesSource, '.access-list-surface .access-toolbar', 'Users list toolbar must be styled as part of the list surface.');
assertIncludes(stylesSource, '.access-table tbody tr:hover', 'Users table rows must have hover/focus feedback.');
assertIncludes(stylesSource, '.access-table__number', 'Users numeric column alignment styles must exist.');
assertIncludes(stylesSource, '.access-user-card__header', 'Users mobile card header styles must exist.');

if (!packageJson.scripts?.['test:material']?.includes('validate-users-material-list.mjs')) {
  throw new Error('test:material must run the Users Material list validator.');
}

console.log('Users Material list validation passed.');
