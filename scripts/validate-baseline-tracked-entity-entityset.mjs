#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const clientPath = resolve(root, 'powerpages/webforms-spa/src/powerpages-api/client.ts');
const source = readFileSync(clientPath, 'utf8');
const uploadSiteSettingsPath = resolve(root, 'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/sitesetting.yml');
const uploadSiteSettings = readFileSync(uploadSiteSettingsPath, 'utf8');
const assignedFormsPath = resolve(root, 'powerpages/webforms-spa/src/views/AssignedFormsView.vue');
const assignedFormsSource = readFileSync(assignedFormsPath, 'utf8');
const uploadReportRowPermissionPath = resolve(root, 'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/table-permissions/mp_submissionreportrow-admin-import.tablepermission.yml');
const uploadReportRowPermission = readFileSync(uploadReportRowPermissionPath, 'utf8');

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
  'Tracked entity create without project bind',
  'Diagnostic tracked entity unbound import path',
  'mp_SubmissionReportRow upsert',
  'async rebuildBaselineReportRowsFromCanonical',
  'private async upsertBaselineReportRow',
  '/_api/mp_submissionreportrows',
];

for (const fragment of requiredFragments) {
  if (!source.includes(fragment)) {
    fail(`Missing required tracked-entity EntitySetName fragment: ${fragment}`);
  }
}

const blockedProjectBindFunctions = [
  'upsertTrackedEntityForBaseline',
  'upsertBeneficiaryProfileForBaseline',
];

for (const functionName of blockedProjectBindFunctions) {
  const pattern = new RegExp(`private async ${functionName}\\([\\s\\S]*?\\n  private async `);
  const match = source.match(pattern);
  if (!match) {
    fail(`Could not inspect baseline import function: ${functionName}`);
  }
  if (match[0].includes('mp_Project@odata.bind')) {
    fail(`${functionName} must not bind mp_Project from the browser baseline import path; repeated Power Pages 90040106 blocks this MVP path.`);
  }
}

const requiredWebApiFieldFragments = [
  'Webapi/mp_entityidentifier/fields',
  'adx_value: mp_entityidentifierid,mp_trackedentity,_mp_trackedentity_value,mp_TrackedEntity,mp_identifiertype,mp_identifiervalue,mp_status',
  'Webapi/mp_beneficiaryprofile/fields',
  'adx_value: mp_beneficiaryprofileid,mp_name,mp_trackedentity,_mp_trackedentity_value,mp_TrackedEntity',
  'Webapi/mp_beneficiarysubmissionlink/fields',
  'adx_value: mp_beneficiarysubmissionlinkid,mp_linkkey,mp_trackedentity,_mp_trackedentity_value,mp_submission,_mp_submission_value,mp_TrackedEntity,mp_Submission',
  'Webapi/mp_submissionreportrow/fields',
  "adx_value: '*'",
];

for (const fragment of requiredWebApiFieldFragments) {
  if (!uploadSiteSettings.includes(fragment)) {
    fail(`Missing required baseline bridge Power Pages Web API field setting fragment: ${fragment}`);
  }
}


const requiredAssignedFormsFragments = [
  'Build report rows',
  'Build 5-row projection smoke',
  'Build all report rows',
  'runBaselineProjectionRepair',
  'rebuildBaselineReportRowsFromCanonical',
];

for (const fragment of requiredAssignedFormsFragments) {
  if (!assignedFormsSource.includes(fragment)) {
    fail(`Missing baseline projection repair UI fragment: ${fragment}`);
  }
}

const requiredReportRowPermissionFragments = [
  'adx_entitylogicalname: mp_submissionreportrow',
  'adx_entityname: mp_submissionreportrow Admin Import',
  'adx_create: true',
  'adx_read: true',
  'adx_write: true',
  'adx_append: true',
  'adx_appendto: true',
  'eee16194-79d2-4e30-9fb9-ea55b3b25e3e',
];

for (const fragment of requiredReportRowPermissionFragments) {
  if (!uploadReportRowPermission.includes(fragment)) {
    fail(`Missing admin baseline report-row table permission fragment: ${fragment}`);
  }
}

console.log('Baseline tracked entity EntitySetName and projection validation passed.');
