#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const repoRoot = resolve(import.meta.dirname, '..');
const clientPath = resolve(repoRoot, 'powerpages/webforms-spa/src/powerpages-api/client.ts');
const viewPath = resolve(repoRoot, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');
const siteSettingsDir = resolve(repoRoot, 'powerpages/tacatdp-monitoring-tool/.powerpages-site/site-settings');
const tablePermissionsDir = resolve(repoRoot, 'powerpages/tacatdp-monitoring-tool/.powerpages-site/table-permissions');
const uploadSiteSettingPath = resolve(repoRoot, 'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/sitesetting.yml');
const uploadTablePermissionsDir = resolve(repoRoot, 'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/table-permissions');

const client = readFileSync(clientPath, 'utf8');
const view = readFileSync(viewPath, 'utf8');
const uploadSiteSetting = readFileSync(uploadSiteSettingPath, 'utf8');

function readRelative(path) {
  return readFileSync(resolve(repoRoot, path), 'utf8');
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertIncludes(source, fragment, message) {
  assert(source.includes(fragment), message);
}

for (const fragment of [
  'async seedIndicatorEvidenceDefinitions(',
  'async readIndicatorEvidenceSeedBack()',
  'validateIndicatorEvidenceSeedAsset',
  "writesOnly.size !== allowedWrites.length",
  "'/_api/mp_indicatordefinitions'",
  "'/_api/mp_datasourcemappings'",
  "'mp_Project@odata.bind'",
  "'mp_IndicatorDefinition@odata.bind'",
  'isPowerPagesAssociationPermissionError',
  'Project lookup bind was skipped',
  'Power Pages blocked mp_project association',
  'compactDataSourceMappingSummary',
  'summary.length <= 200',
  'INDICATOR_SEED_DEFINITION_CODES',
  'INDICATOR_SEED_MAPPING_KEYS',
  'missingDefinitionCodes',
  'missingMappingKeys',
  "mp_code eq '${this.escapeODataString(definition.code)}'",
  "mp_mappingkey eq '${this.escapeODataString(mapping.mapping_key)}'",
  'LOCAL_YES_NO_CODES',
]) {
  assertIncludes(client, fragment, `Power Pages client missing indicator browser seed fragment: ${fragment}`);
}

for (const forbidden of [
  "'/_api/mp_observations'",
  "'/_api/mp_evidences'",
  "'/_api/mp_indicatorresults'",
  'new Entity("mp_observation")',
  'pac package deploy',
  'az account',
  'mp_datasourcemappingjson: JSON.stringify(definition.mappings)',
]) {
  assert(!client.includes(forbidden), `Power Pages browser seed client contains forbidden fragment: ${forbidden}`);
}

for (const fragment of [
  'IndicatorEvidenceSeedAsset',
  'IndicatorEvidenceSeedResult',
  'indicatorSeedAsset',
  'handleIndicatorSeedFileChange',
  'runIndicatorEvidenceSeed',
  'verifyIndicatorEvidenceSeedReadBack',
  'Verify seeded metadata',
  'Indicator definitions readable',
  'Data-source mappings readable',
  'buildIndicatorProjectionReadiness',
  'calculateTacatdpBaselineProjection',
  'Build indicator projection',
  'read-only readiness check',
  'No mp_IndicatorResult rows are written',
  'Indicator projection readiness table',
  'Seed indicator definitions',
  'Indicator evidence seed JSON',
  'Run indicator seed',
  'writes only indicator metadata',
]) {
  assertIncludes(view, fragment, `Admin import view missing indicator seed fragment: ${fragment}`);
}

const requiredSettings = {
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/site-settings/Webapi-mp_indicatordefinition-enabled.sitesetting.yml': [
    'name: Webapi/mp_indicatordefinition/enabled',
    'value: true',
  ],
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/site-settings/Webapi-mp_indicatordefinition-fields.sitesetting.yml': [
    'name: Webapi/mp_indicatordefinition/fields',
    'mp_project',
    'mp_code',
    'mp_datasourcemappingjson',
  ],
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/site-settings/Webapi-mp_datasourcemapping-enabled.sitesetting.yml': [
    'name: Webapi/mp_datasourcemapping/enabled',
    'value: true',
  ],
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/site-settings/Webapi-mp_datasourcemapping-fields.sitesetting.yml': [
    'name: Webapi/mp_datasourcemapping/fields',
    'mp_mappingkey',
    'mp_project',
    'mp_indicatordefinition',
  ],
};

for (const [path, fragments] of Object.entries(requiredSettings)) {
  const file = readRelative(path);
  for (const fragment of fragments) {
    assertIncludes(file, fragment, `${path} missing required fragment: ${fragment}`);
  }
}

for (const fragment of [
  'adx_name: Webapi/mp_indicatordefinition/enabled',
  'adx_name: Webapi/mp_indicatordefinition/fields',
  'mp_indicatordefinitionid',
  'mp_datasourcemappingjson',
  'adx_name: Webapi/mp_datasourcemapping/enabled',
  'adx_name: Webapi/mp_datasourcemapping/fields',
  'mp_datasourcemappingid',
  'mp_IndicatorDefinition',
]) {
  assertIncludes(uploadSiteSetting, fragment, `Enhanced upload sitesetting.yml missing required fragment: ${fragment}`);
}

for (const [path, entityLogicalName] of Object.entries({
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/table-permissions/mp_indicatordefinition-admin-import.tablepermission.yml': 'mp_indicatordefinition',
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/table-permissions/mp_datasourcemapping-admin-import.tablepermission.yml': 'mp_datasourcemapping',
  'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/table-permissions/mp_indicatordefinition-admin-import.tablepermission.yml': 'mp_indicatordefinition',
  'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/table-permissions/mp_datasourcemapping-admin-import.tablepermission.yml': 'mp_datasourcemapping',
})) {
  const file = readRelative(path);
  for (const fragment of [
    `adx_entitylogicalname: ${entityLogicalName}`,
    'adx_create: true',
    'adx_read: true',
    'adx_write: true',
    'adx_append: true',
    'adx_appendto: true',
    'adx_delete: false',
    '- eee16194-79d2-4e30-9fb9-ea55b3b25e3e',
  ]) {
    assertIncludes(file, fragment, `${path} missing required fragment: ${fragment}`);
  }
}

assert(siteSettingsDir.endsWith('site-settings'), 'Site settings directory path is wrong.');
assert(tablePermissionsDir.endsWith('table-permissions'), 'Table permissions directory path is wrong.');
assert(uploadTablePermissionsDir.endsWith('table-permissions'), 'Upload table permissions directory path is wrong.');

console.log('Indicator browser seed validation passed.');
