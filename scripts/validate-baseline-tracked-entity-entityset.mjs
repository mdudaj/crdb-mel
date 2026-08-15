#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const clientPath = resolve(root, 'powerpages/webforms-spa/src/powerpages-api/client.ts');
const source = readFileSync(clientPath, 'utf8');

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

if (source.includes('mp_trackedentities')) {
  fail('Baseline tracked entity Power Pages Web API path must use live EntitySetName mp_trackedentitys, not guessed plural mp_trackedentities.');
}

const requiredFragments = [
  '/_api/mp_trackedentitys',
  '/mp_trackedentitys(${trackedEntityId})',
];

for (const fragment of requiredFragments) {
  if (!source.includes(fragment)) {
    fail(`Missing required tracked-entity EntitySetName fragment: ${fragment}`);
  }
}

console.log('Baseline tracked entity EntitySetName validation passed.');
