import type {
  AccessAuthorizationDecision,
  AccessAuditPreviewPayload,
  BeneficiaryListItem,
  BeneficiaryProfileRow,
  BeneficiarySubmissionLinkRow,
  BaselineBridgeImportAsset,
  BaselineBridgeImportProgress,
  BaselineImportDiagnosticStep,
  BaselineBridgeImportOptions,
  BaselineBridgeImportResult,
  AccessWriteAction,
  AccessWriteCommand,
  AccessWritePreview,
  AccessWriteReadiness,
  AccessWriteScopeType,
  AccessUserSummary,
  AssignFormAccessInput,
  AssignFormAccessReadiness,
  AssignFormAccessResult,
  ContactRow,
  CreateCsvExportSettingInput,
  DataverseCollection,
  EntityIdentifierRow,
  ExportSettingRow,
  FormAttachmentRow,
  FormAssignmentRow,
  FormAssignmentMetadataRow,
  FormAssignmentSummary,
  ManageAccessUserInput,
  ManageAccessUserResult,
  FormRow,
  FormVersionRow,
  MailboxReadinessStatus,
  NotificationDeliveryMode,
  NotificationDeliverySetting,
  NotificationDeliverySettingInput,
  OdkSubmitResult,
  ReportingFilters,
  ReportingAccessScope,
  SubmissionAnswerRow,
  SubmissionReportPage,
  SubmissionReportRow,
  SubmissionRow,
  SubmissionSummary,
  SubmissionVersionRow,
  UserActivationDiagnostic,
  UserOnboardingAccessInput,
  UserOnboardingAccessResult,
} from './types';
import { devAssignedForms } from '../dev/assignedForms';
import { devExportSettings, devReportingRows, devSubmissionAnswers } from '../dev/reporting';
import { xformCache } from '../offline/xform-cache';
import { measureAsync } from '../performance';

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

interface RequestOptions {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
}

const INSTANCE_FILE_NAME = 'xml_submission_file';
const XFORM_FILE_MARKER_PREFIX = 'dataverse-file:';
const XFORM_CACHE_PREFIX = 'tacatdp.xformXml.v1';
const SUBMISSION_LIFECYCLE_SUBMITTED = 100000001;
const SUBMISSION_REVIEW_RECEIVED = 100000000;
const PROJECTION_READY = 100000000;
const FORM_VERSION_LIFECYCLE_PUBLISHED = 100000001;
const TRACKED_ENTITY_TYPE_BENEFICIARY = 100000000;
const TRACKED_ENTITY_STATUS_ACTIVE = 100000000;
const IDENTIFIER_SOURCE_RECORD = 100000000;
const IDENTIFIER_PHONE = 100000002;
const IDENTIFIER_CUSTOMER_ID = 100000006;
const IDENTIFIER_STATUS_ACTIVE = 100000000;
const BENEFICIARY_CATEGORY_INDIVIDUAL_FARMER = 100000000;
const BENEFICIARY_VERIFICATION_UNDER_REVIEW = 100000000;
const SUBMISSION_LINK_RELATIONSHIP_BASELINE = 100000000;
const SUBMISSION_LINK_REVIEW_UNDER_REVIEW = 100000000;
const EXPORT_FORMAT_CSV = 100000000;
const EXPORT_SCOPE_CURRENT_FILTERS = 100000000;
const ACCESS_ADMIN_POWERPAGES_ROLES = ['Administrators', 'Platform Administrator'];
const ACCESS_WRITE_ACTIONS_ENABLED = import.meta.env.VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true';
const ACCESS_ASSIGN_FORM_WRITE_ENABLED = import.meta.env.VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED === 'true';
const ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED = import.meta.env.VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED === 'true';
const ACCESS_WRITE_DISABLED_MESSAGE = 'User & Access writes are disabled until audit schema, table permissions, Web API settings, and CRDB approval are complete.';
const ACCESS_ASSIGN_FORM_DISABLED_MESSAGE = 'AssignForm writes are disabled until AccessAuditLogs schema, administrator table permissions, and AssignForm smoke tests are approved.';
const ACCESS_ONBOARDING_AUTOMATION_ENABLED = import.meta.env.VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED === 'true';
const ACCESS_ONBOARDING_DISABLED_MESSAGE = 'Create, invite, assign, and notify is disabled until the OnboardingRequests queue table, administrator table permissions, and Dataverse-triggered processor are approved.';
const ACCESS_AUDIT_WEB_API_PATH = '/_api/mp_accessauditlogs';
const ACCESS_ONBOARDING_QUEUE_WEB_API_PATH = '/_api/mp_onboardingrequests';
const NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH = '/_api/mp_notificationdeliverysettings';
const NOTIFICATION_DELIVERY_SETTING_KEY = 'onboarding-delivery';
const ONBOARDING_STATUS_PENDING = 100000000;
const FORM_ASSIGNMENT_LIFECYCLE_ACTIVE = 100000000;
const FORM_ASSIGNMENT_LIFECYCLE_INACTIVE = 100000001;
const NOTIFICATION_DELIVERY_MODE_CODES: Record<NotificationDeliveryMode, number> = {
  'manual-code': 100000000,
  email: 100000001,
};
const NOTIFICATION_DELIVERY_MODE_LABELS: Record<number, NotificationDeliveryMode> = {
  100000000: 'manual-code',
  100000001: 'email',
};
const MAILBOX_STATUS_CODES: Record<MailboxReadinessStatus, number> = {
  'not-configured': 100000000,
  'pending-admin-setup': 100000001,
  approved: 100000002,
  'tested-and-enabled': 100000003,
  failed: 100000004,
};
const MAILBOX_STATUS_LABELS: Record<number, MailboxReadinessStatus> = {
  100000000: 'not-configured',
  100000001: 'pending-admin-setup',
  100000002: 'approved',
  100000003: 'tested-and-enabled',
  100000004: 'failed',
};
const ONBOARDING_REQUEST_TYPE_CODES = {
  NewUser: 100000000,
  ExistingUser: 100000001,
  Unresolved: 100000002,
} as const;
const ONBOARDING_STATUS_LABELS: Record<number, UserOnboardingAccessResult['queueStatus']> = {
  100000000: 'Pending',
  100000001: 'Processing',
  100000002: 'Completed',
  100000003: 'Failed',
  100000004: 'Cancelled',
  100000005: 'NeedsReview',
};
const ONBOARDING_REQUEST_TYPE_LABELS: Record<number, UserOnboardingAccessResult['requestType']> = {
  100000000: 'NewUser',
  100000001: 'ExistingUser',
  100000002: 'Unresolved',
};
const INVITATION_STATUS_LABELS: Record<number, NonNullable<UserOnboardingAccessResult['invitationStatus']>> = {
  100000000: 'Pending',
  100000001: 'ManualDeliveryRequired',
  100000002: 'EmailSent',
  100000003: 'Redeemed',
  100000004: 'Expired',
  100000005: 'Replaced',
};
const INVITATION_DELIVERY_MODE_LABELS: Record<number, NonNullable<UserOnboardingAccessResult['invitationDeliveryMode']>> = {
  100000000: 'Email',
  100000001: 'ManualCode',
  100000002: 'AssignmentNotification',
};
const ACCESS_WRITE_REQUIRED_GATES = [
  'AccessAuditLogs schema deployed through the governed solution process',
  'administrator table permissions approved for audit and assignment writes',
  'Power Pages Web API site settings enabled for the approved field set',
  'administrator, project manager, and data collector smoke tests passed',
];
const ACCESS_AUDIT_ACTION_CODES: Record<AccessWriteAction, number> = {
  InviteUser: 100000000,
  AssignProject: 100000001,
  AssignForm: 100000002,
  ChangeRole: 100000003,
  CorrectEmail: 100000003,
  SuspendAccess: 100000004,
  ReactivateAccess: 100000005,
  RemoveAssignment: 100000006,
  RollbackAccessChange: 100000007,
};
const ACCESS_AUDIT_RESULT_STATUS_CODES = {
  Requested: 100000000,
  Succeeded: 100000001,
  Failed: 100000002,
  Rejected: 100000003,
  RolledBack: 100000004,
} as const;
const ACCESS_AUDIT_SCOPE_TYPE_CODES: Record<AccessWriteScopeType, number> = {
  Platform: 100000000,
  Project: 100000001,
  Form: 100000002,
  FormVersion: 100000003,
  Assignment: 100000004,
};

interface OdkInstancePayload {
  payloadType?: string;
  status?: string;
  violations?: unknown;
  submissionMeta?: unknown;
  data?: Array<FormData>;
}

interface InstancePayloadSummary {
  payloadType?: string;
  status?: string;
  violationCount: number;
  instanceName?: string;
  attachmentNames: string[];
  attachmentDetails: AttachmentPayloadSummary[];
  submissionMeta?: unknown;
  repeatPaths: string[];
}

interface AttachmentPayloadSummary {
  fieldName: string;
  fileName: string;
  mediaType: string;
  size: number;
}

interface AttachmentPayload extends AttachmentPayloadSummary {
  file: File;
}

interface OnboardingRequestRow {
  mp_requestkey?: string;
  mp_requestid?: string;
  mp_status?: number;
  mp_requesttype?: number;
  mp_contactid?: string;
  mp_resultmessage?: string;
  mp_invitationid?: string;
  mp_invitationcode?: string;
  mp_invitationredeemurl?: string;
  mp_invitationexpiresat?: string;
  mp_invitationstatus?: number;
  mp_invitationdeliverymode?: number;
  mp_replacementofrequestid?: string;
}

interface InvitationDiagnosticRow {
  adx_invitationid?: string;
  adx_name?: string;
  adx_expirydate?: string;
  statuscode?: number;
  statecode?: number;
  createdon?: string;
  modifiedon?: string;
  _adx_invitecontact_value?: string;
}

interface ExternalIdentityDiagnosticRow {
  adx_externalidentityid?: string;
  adx_username?: string;
  createdon?: string;
  _adx_contactid_value?: string;
}

interface PowerPageRoleRow {
  powerpagecomponentid?: string;
  name?: string;
  powerpagecomponenttype?: number;
}

interface NotificationDeliverySettingRow {
  mp_notificationdeliverysettingid?: string;
  mp_settingkey?: string;
  mp_deliverymode?: number;
  mp_sendermailbox?: string;
  mp_mailboxstatus?: number;
  mp_nativeinvitationworkflowid?: string;
  mp_lasttestedat?: string;
  mp_lasttestresult?: string;
  mp_instructions?: string;
  mp_updatedbyemail?: string;
  mp_updatedat?: string;
}

interface AttachmentPersistResult {
  attachmentId: string;
  binaryUploaded: boolean;
  warning?: string;
}

export class AccessWriteDisabledError extends Error {
  constructor(message = ACCESS_WRITE_DISABLED_MESSAGE) {
    super(message);
    this.name = 'AccessWriteDisabledError';
  }
}

declare global {
  interface Window {
    __TACATDP_POWERPAGES__?: {
      isAuthenticated?: boolean;
      userEmail?: string;
      userName?: string;
      roles?: string[];
    };
    shell?: {
      getTokenDeferred?: () => {
        done: (callback: (token: string) => void) => { fail: (callback: () => void) => void };
      };
    };
  }
}

export class PowerPagesApiClient {
  private formVersionMetadataCache = new Map<string, FormVersionRow>();
  private formVersionRuntimeCache = new Map<string, FormVersionRow>();
  private formCache = new Map<string, FormRow>();

  hasPowerPagesSession(): boolean {
    return this.shouldUseLocalFixture() || Boolean(window.__TACATDP_POWERPAGES__?.isAuthenticated);
  }

  getSignedInUserLabel(): string {
    if (this.shouldUseLocalFixture()) {
      return 'local.dev@example.test';
    }

    return window.__TACATDP_POWERPAGES__?.userEmail
      || window.__TACATDP_POWERPAGES__?.userName
      || 'Signed in';
  }

  getSignedInUserEmail(): string {
    if (this.shouldUseLocalFixture()) {
      return 'local.dev@example.test';
    }

    return window.__TACATDP_POWERPAGES__?.userEmail?.trim() ?? '';
  }

  areAccessWritesEnabled(): boolean {
    return ACCESS_WRITE_ACTIONS_ENABLED;
  }

  getAccessWriteReadiness(): AccessWriteReadiness {
    return {
      enabled: ACCESS_WRITE_ACTIONS_ENABLED,
      statusLabel: ACCESS_WRITE_ACTIONS_ENABLED ? 'Write actions enabled' : 'Write actions disabled',
      disabledReason: ACCESS_WRITE_ACTIONS_ENABLED ? '' : ACCESS_WRITE_DISABLED_MESSAGE,
      requiredGates: ACCESS_WRITE_REQUIRED_GATES,
    };
  }

  areAssignFormWritesEnabled(): boolean {
    return ACCESS_WRITE_ACTIONS_ENABLED && ACCESS_ASSIGN_FORM_WRITE_ENABLED;
  }

  getAssignFormAccessReadiness(): AssignFormAccessReadiness {
    return {
      enabled: this.areAssignFormWritesEnabled(),
      statusLabel: this.areAssignFormWritesEnabled() ? 'AssignForm enabled' : 'AssignForm disabled',
      disabledReason: this.areAssignFormWritesEnabled() ? '' : ACCESS_ASSIGN_FORM_DISABLED_MESSAGE,
      requiredGates: [
        'AccessAuditLogs schema exists in the target environment',
        'Platform Administrator audit create/read permission verified',
        'Platform Administrator form-assignment create/read permission verified',
        'Data Collector denied audit read smoke test passed',
        'AssignForm duplicate-detection smoke test passed',
      ],
    };
  }

  getUserOnboardingReadiness(): AccessWriteReadiness {
    const enabled = ACCESS_ONBOARDING_AUTOMATION_ENABLED;
    return {
      enabled,
      statusLabel: enabled ? 'Onboarding queue enabled' : 'Create, invite and assign disabled',
      disabledReason: enabled ? '' : ACCESS_ONBOARDING_DISABLED_MESSAGE,
      requiredGates: [
        'OnboardingRequests queue table exists in the target environment',
        'Platform Administrator can create and read onboarding request rows through Power Pages Web API',
        'Dataverse-triggered onboarding processor is registered in the same environment',
        'Processor creates or reuses Power Pages contacts by primary email',
        'Processor sends native Power Pages invitation for new users and assignment notification for existing users',
        'Processor creates TACATDP project/form assignments only after audit create succeeds',
        'Request status is updated to Completed or Failed with a business-readable result',
      ],
    };
  }

  async importBaselineBridgeAsset(
    asset: BaselineBridgeImportAsset,
    options: BaselineBridgeImportOptions = {},
  ): Promise<BaselineBridgeImportResult> {
    if (!this.isCurrentUserAccessAdmin()) {
      throw new Error('Baseline import requires the Platform Administrator web role.');
    }
    if (asset.assetType !== 'tacatdp-baseline-bridge-import') {
      throw new Error('Selected file is not a TACATDP baseline bridge import asset.');
    }
    if (asset.projectCode !== 'TACATDP') {
      throw new Error(`Unsupported project code: ${asset.projectCode || '<empty>'}.`);
    }
    if (asset.formId !== 'tacatdp_impact_evaluation') {
      throw new Error(`Unsupported form id: ${asset.formId || '<empty>'}.`);
    }
    if (asset.formVersion !== '2608130924') {
      throw new Error(`Unsupported form version: ${asset.formVersion || '<empty>'}. Expected 2608130924.`);
    }
    if (!Array.isArray(asset.rows) || asset.rows.length === 0) {
      throw new Error('Baseline import asset has no rows.');
    }

    const mode = options.mode ?? 'append';
    const rows = asset.rows.slice(0, options.limit ?? asset.rows.length);
    const result: BaselineBridgeImportResult = {
      status: options.dryRun ? 'validated' : 'executed',
      mode,
      rowsProcessed: 0,
      totalRows: asset.rows.length,
      limit: options.limit,
      counts: {},
      duplicateReviewGroups: asset.counts?.duplicateReviewGroups ?? 0,
      duplicateReviewRows: asset.counts?.duplicateReviewRows ?? 0,
      messages: [],
    };
    result.messages.push(`Asset validated: ${asset.rows.length} rows, version ${asset.formVersion}.`);
    result.messages.push(mode === 'append'
      ? 'Mode: append. Existing baseline submissions keep history through a new submission version where a matching row already exists.'
      : 'Mode: replace. Matching baseline rows are updated in place; unrelated project records are not deleted.');
    if (options.dryRun) {
      return result;
    }

    const projectId = await this.requireProjectId(asset.projectCode);
    const formVersionId = await this.requireFormVersionId(asset.formVersion);
    const now = new Date().toISOString();

    for (const row of rows) {
      const rowNumber = Number(row.rowNumber || result.rowsProcessed + 1);
      options.onProgress?.({
        processedRows: result.rowsProcessed,
        totalRows: rows.length,
        currentRowNumber: rowNumber,
        message: `Importing row ${rowNumber}`,
      });

      const submissionId = await this.runBaselineImportStep(rowNumber, 'mp_Submission upsert', () => this.upsertSubmissionForBaseline(row, formVersionId, now));
      this.bumpImportCount(result, 'mp_Submission');
      const submissionVersion = await this.runBaselineImportStep(rowNumber, 'mp_SubmissionVersion upsert', () => this.upsertSubmissionVersionForBaseline(row, submissionId, now, mode));
      this.bumpImportCount(result, 'mp_SubmissionVersion');
      const trackedEntityId = await this.runBaselineImportStep(rowNumber, 'mp_TrackedEntity upsert', () => this.upsertTrackedEntityForBaseline(row, projectId));
      this.bumpImportCount(result, 'mp_TrackedEntity');
      const identifierCount = await this.runBaselineImportStep(rowNumber, 'mp_EntityIdentifier upsert', () => this.upsertIdentifiersForBaseline(row, trackedEntityId));
      result.counts.mp_EntityIdentifier = (result.counts.mp_EntityIdentifier ?? 0) + identifierCount;
      await this.runBaselineImportStep(rowNumber, 'mp_BeneficiaryProfile upsert', () => this.upsertBeneficiaryProfileForBaseline(row, trackedEntityId, projectId, now));
      this.bumpImportCount(result, 'mp_BeneficiaryProfile');
      await this.runBaselineImportStep(rowNumber, 'mp_BeneficiarySubmissionLink upsert', () => this.upsertBeneficiarySubmissionLinkForBaseline(row, trackedEntityId, submissionId));
      this.bumpImportCount(result, 'mp_BeneficiarySubmissionLink');
      await this.runBaselineImportStep(rowNumber, 'mp_SubmissionReportRow upsert', () => this.upsertBaselineReportRow(row, submissionId, submissionVersion.submissionVersionId, submissionVersion.versionNumber, formVersionId, now));
      this.bumpImportCount(result, 'mp_SubmissionReportRow');
      result.rowsProcessed += 1;

      if (result.rowsProcessed % 50 === 0) {
        options.onProgress?.({
          processedRows: result.rowsProcessed,
          totalRows: rows.length,
          currentRowNumber: rowNumber,
          message: `Imported ${result.rowsProcessed} of ${rows.length} rows`,
        });
      }
    }

    options.onProgress?.({
      processedRows: result.rowsProcessed,
      totalRows: rows.length,
      message: `Imported ${result.rowsProcessed} rows`,
    });
    result.messages.push(`${mode === 'append' ? 'Appended' : 'Replaced matching'} ${result.rowsProcessed} rows through Power Pages Web API.`);
    return result;
  }

  async rebuildBaselineReportRowsFromCanonical(options: { limit?: number; onProgress?: (progress: BaselineBridgeImportProgress) => void } = {}): Promise<BaselineBridgeImportResult> {
    if (!this.isCurrentUserAccessAdmin()) {
      throw new Error('Baseline report projection repair requires the Platform Administrator web role.');
    }
    const formVersionId = await this.requireFormVersionId('2608130924');
    const now = new Date().toISOString();
    const submissions = await this.get<DataverseCollection<SubmissionRow>>(
      `/_api/mp_submissions?$select=mp_submissionid,mp_instanceid,mp_useremail,mp_submittedat,mp_updatedat,mp_lifecyclestatus,mp_reviewstate,_mp_formversion_value&$filter=mp_lifecyclestatus eq ${SUBMISSION_LIFECYCLE_SUBMITTED} and _mp_formversion_value eq ${formVersionId}&$orderby=mp_updatedat desc&$top=5000`,
    );
    const rows = submissions.value.slice(0, options.limit ?? submissions.value.length);
    const result: BaselineBridgeImportResult = {
      status: 'executed',
      mode: 'replace',
      rowsProcessed: 0,
      totalRows: submissions.value.length,
      limit: options.limit,
      counts: {},
      duplicateReviewGroups: 0,
      duplicateReviewRows: 0,
      messages: ['Rebuilt reporting rows from canonical baseline submissions.'],
    };
    for (const submission of rows) {
      options.onProgress?.({
        processedRows: result.rowsProcessed,
        totalRows: rows.length,
        message: `Projecting ${result.rowsProcessed + 1} of ${rows.length} baseline submissions`,
      });
      const version = await this.getLatestSubmissionVersionByInstanceId(submission.mp_instanceid);
      if (!version?.mp_submissionversionid) {
        result.messages.push(`Skipped ${submission.mp_instanceid}: no submission version found.`);
        result.rowsProcessed += 1;
        continue;
      }
      await this.upsertCanonicalReportRow(submission, version, formVersionId, now);
      this.bumpImportCount(result, 'mp_SubmissionReportRow');
      result.rowsProcessed += 1;
      if (result.rowsProcessed % 50 === 0) {
        options.onProgress?.({
          processedRows: result.rowsProcessed,
          totalRows: rows.length,
          message: `Projected ${result.rowsProcessed} of ${rows.length} baseline submissions`,
        });
      }
    }
    options.onProgress?.({
      processedRows: result.rowsProcessed,
      totalRows: rows.length,
      message: `Projected ${result.rowsProcessed} baseline submissions`,
    });
    return result;
  }

  async runBaselineTrackedEntityDiagnostics(projectCode = 'TACATDP'): Promise<BaselineImportDiagnosticStep[]> {
    const steps: BaselineImportDiagnosticStep[] = [];
    const run = async (name: string, operation: string, action: () => Promise<string>): Promise<void> => {
      try {
        const detail = await action();
        steps.push({ name, operation, status: 'passed', detail });
      } catch (caught) {
        const message = caught instanceof Error ? caught.message : 'Unknown diagnostic failure.';
        steps.push({ name, operation, status: 'failed', detail: this.sanitizeBaselineImportDiagnostic(message) });
      }
    };

    let projectId = '';
    await run('Project lookup', 'GET /_api/mp_projects', async () => {
      projectId = await this.requireProjectId(projectCode);
      return `Resolved project ${projectCode} to ${projectId}.`;
    });

    await run('Tracked entity read without id', 'GET /_api/mp_trackedentitys?$select=mp_entitykey', async () => {
      const result = await this.get<DataverseCollection<{ mp_entitykey?: string }>>(
        '/_api/mp_trackedentitys?$select=mp_entitykey&$top=1',
      );
      return `Read succeeded; returned ${result.value.length} row(s).`;
    });

    await run('Tracked entity read with id', 'GET /_api/mp_trackedentitys?$select=mp_trackedentityid,mp_entitykey', async () => {
      const result = await this.get<DataverseCollection<{ mp_trackedentityid?: string }>>(
        '/_api/mp_trackedentitys?$select=mp_trackedentityid,mp_entitykey&$top=1',
      );
      return `Read with primary id succeeded; returned ${result.value.length} row(s).`;
    });

    await run('Tracked entity FetchXML lookup', 'GET /_api/mp_trackedentitys?fetchXml=...', async () => {
      const result = await this.findOneByFetchXml<{ mp_trackedentityid?: string }>(
        '/_api/mp_trackedentitys',
        'mp_trackedentity',
        ['mp_trackedentityid', 'mp_entitykey'],
        [['mp_entitytype', 'eq', TRACKED_ENTITY_TYPE_BENEFICIARY]],
      );
      return `FetchXML lookup succeeded; matched ${result?.mp_trackedentityid ? 'one row' : 'no rows'}.`;
    });

    const timestamp = Date.now();
    const createBasePayload = {
      mp_entitytype: TRACKED_ENTITY_TYPE_BENEFICIARY,
      mp_status: TRACKED_ENTITY_STATUS_ACTIVE,
    };

    await run('Tracked entity create without project bind', 'POST /_api/mp_trackedentitys', async () => {
      const id = await this.createRecord('/_api/mp_trackedentitys', {
        ...createBasePayload,
        mp_entitykey: `diagnostic:unbound:${timestamp}`,
        mp_displayname: 'Diagnostic tracked entity unbound import path',
      });
      return `Create succeeded without project lookup bind; id ${id}.`;
    });

    return steps;
  }

  async seedLatestTacatdpXForm(xml: string): Promise<string> {
    if (!this.isCurrentUserAccessAdmin()) {
      throw new Error('XForm seed requires the Platform Administrator web role.');
    }
    if (!xml.includes('id="tacatdp_impact_evaluation"') || !xml.includes('version="2608130924"')) {
      throw new Error('Selected XML does not match TACATDP form id tacatdp_impact_evaluation and version 2608130924.');
    }
    const form = await this.findOne<{ mp_formid: string }>(
      '/_api/mp_forms',
      'mp_formid,mp_xmlformid',
      "mp_xmlformid eq 'tacatdp_impact_evaluation'",
    );
    if (!form?.mp_formid) {
      throw new Error('TACATDP form row was not found. Seed mp_form before seeding the latest form version.');
    }
    const existing = await this.findOne<{ mp_formversionid: string }>(
      '/_api/mp_formversions',
      'mp_formversionid,mp_version',
      "mp_version eq '2608130924'",
    );
    const payload = {
      mp_version: '2608130924',
      mp_hash: 'xlsform-2608130924-browser-seed',
      mp_xformxml: xml,
      mp_webformsenabled: true,
      mp_lifecyclestatus: FORM_VERSION_LIFECYCLE_PUBLISHED,
      mp_publishedat: new Date().toISOString(),
    };
    if (existing?.mp_formversionid) {
      await this.send(`/_api/mp_formversions(${encodeURIComponent(existing.mp_formversionid)})`, { method: 'PATCH', body: payload });
      return existing.mp_formversionid;
    }
    return this.createRecord('/_api/mp_formversions', {
      ...payload,
      'mp_Form@odata.bind': `/mp_forms(${form.mp_formid})`,
    });
  }

  async getNotificationDeliverySetting(): Promise<NotificationDeliverySetting> {
    if (this.shouldUseLocalFixture()) {
      return this.getDefaultNotificationDeliverySetting();
    }

    try {
      const rows = await this.get<DataverseCollection<NotificationDeliverySettingRow>>(
        `${NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH}?$select=mp_notificationdeliverysettingid,mp_settingkey,mp_deliverymode,mp_sendermailbox,mp_mailboxstatus,mp_nativeinvitationworkflowid,mp_lasttestedat,mp_lasttestresult,mp_instructions,mp_updatedbyemail,mp_updatedat&$filter=mp_settingkey eq '${NOTIFICATION_DELIVERY_SETTING_KEY}'&$top=1`,
      );
      const row = rows.value[0];
      return row ? this.toNotificationDeliverySetting(row) : this.getDefaultNotificationDeliverySetting();
    } catch {
      return this.getDefaultNotificationDeliverySetting();
    }
  }

  async saveNotificationDeliverySetting(input: NotificationDeliverySettingInput, existingId?: string): Promise<NotificationDeliverySetting> {
    if (input.deliveryMode === 'email' && (input.mailboxStatus !== 'tested-and-enabled' || !input.senderMailbox?.trim())) {
      throw new Error('Mailbox email delivery requires a sender mailbox with Tested and enabled readiness.');
    }
    if (this.shouldUseLocalFixture()) {
      return {
        ...this.getDefaultNotificationDeliverySetting(),
        ...input,
        settingKey: NOTIFICATION_DELIVERY_SETTING_KEY,
        source: 'default',
        updatedByEmail: this.getSignedInUserEmail(),
        updatedAt: new Date().toISOString(),
      };
    }

    const payload = this.toNotificationDeliverySettingWebApiPayload(input);
    const recordId = existingId || await this.findNotificationDeliverySettingId();
    if (recordId) {
      await this.send(`${NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH}(${recordId})`, {
        method: 'PATCH',
        body: payload,
      });
      return this.getNotificationDeliverySetting();
    }

    const createdId = await this.createRecord(NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH, payload);
    const row = await this.get<NotificationDeliverySettingRow>(
      `${NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH}(${createdId})?$select=mp_notificationdeliverysettingid,mp_settingkey,mp_deliverymode,mp_sendermailbox,mp_mailboxstatus,mp_nativeinvitationworkflowid,mp_lasttestedat,mp_lasttestresult,mp_instructions,mp_updatedbyemail,mp_updatedat`,
    );
    return this.toNotificationDeliverySetting(row);
  }

  getSignInUrl(): string {
    const returnUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;
    return `/SignIn?returnUrl=${encodeURIComponent(returnUrl)}`;
  }

  isCurrentUserAccessAdmin(): boolean {
    return this.getCurrentUserAccessAuthorization().allowed;
  }

  getCurrentUserAccessAuthorization(): AccessAuthorizationDecision {
    const detectedRoles = this.getPowerPagesRoles();
    if (this.shouldUseLocalFixture()) {
      return {
        allowed: true,
        source: 'local-dev-fixture',
        matchedRoles: ['local-dev-fixture'],
        detectedRoles,
        requiredRoles: ACCESS_ADMIN_POWERPAGES_ROLES,
      };
    }

    const matchedRoles = this.matchPowerPagesRoles(ACCESS_ADMIN_POWERPAGES_ROLES);
    return {
      allowed: matchedRoles.length > 0,
      source: matchedRoles.length > 0 ? 'power-pages-web-role' : 'none',
      matchedRoles,
      detectedRoles,
      requiredRoles: ACCESS_ADMIN_POWERPAGES_ROLES,
    };
  }

  buildAccessWritePreview(command: AccessWriteCommand): AccessWritePreview {
    const reason = command.reason.trim();
    const affectedEmail = command.affectedEmail.trim().toLowerCase();
    if (!affectedEmail) {
      throw new Error('Affected user email is required before preparing an access write.');
    }
    if (!reason) {
      throw new Error('Business reason is required before preparing an access write.');
    }

    const occurredAt = new Date().toISOString();
    const requestId = this.buildAccessRequestId(command.action, affectedEmail, occurredAt);
    const actorEmail = this.getSignedInUserEmail() || this.getSignedInUserLabel();
    const actorRoles = this.getCurrentUserAccessAuthorization().detectedRoles;
    const auditKey = `access:${occurredAt}:${this.slugify(actorEmail)}:${command.action}:${this.slugify(affectedEmail)}:${requestId}`;
    const auditPayload: AccessAuditPreviewPayload = {
      AuditKey: auditKey,
      Action: command.action,
      ResultStatus: 'Requested',
      ActorEmail: actorEmail,
      ActorRolesJson: JSON.stringify(actorRoles),
      AffectedEmail: affectedEmail,
      TargetRole: command.targetRole,
      ScopeType: command.scopeType,
      PreviousStateJson: command.previousState ? JSON.stringify(command.previousState) : undefined,
      NewStateJson: command.newState ? JSON.stringify(command.newState) : undefined,
      Reason: reason,
      SourceRoute: command.sourceRoute,
      RequestId: requestId,
      OccurredAt: occurredAt,
      ResultMessage: ACCESS_WRITE_ACTIONS_ENABLED ? 'Prepared for governed access write.' : ACCESS_WRITE_DISABLED_MESSAGE,
    };

    return {
      requestId,
      auditKey,
      enabled: ACCESS_WRITE_ACTIONS_ENABLED,
      statusLabel: ACCESS_WRITE_ACTIONS_ENABLED ? 'Write actions enabled' : 'Write actions disabled',
      disabledReason: ACCESS_WRITE_ACTIONS_ENABLED ? '' : ACCESS_WRITE_DISABLED_MESSAGE,
      auditPayload,
      mutationPayload: this.buildAccessMutationPayload(command, affectedEmail),
    };
  }

  async submitAccessWrite(command: AccessWriteCommand): Promise<AccessWritePreview> {
    const preview = this.buildAccessWritePreview(command);
    if (!this.areAccessWritesEnabled()) {
      throw new AccessWriteDisabledError();
    }

    return preview;
  }

  buildAssignFormAccessCommand(input: AssignFormAccessInput): AccessWriteCommand {
    const affectedEmail = input.affectedEmail.trim().toLowerCase();
    const assignmentKey = this.buildFormAssignmentKey(affectedEmail, input.formVersionId);
    return {
      action: 'AssignForm',
      affectedEmail,
      targetRole: input.targetRole ?? 'Data Collector / Bank Officer',
      scopeType: 'FormVersion',
      reason: input.reason,
      sourceRoute: input.sourceRoute,
      projectId: input.projectId,
      formId: input.formId,
      formVersionId: input.formVersionId,
      previousState: {
        userEmail: affectedEmail,
        contactId: input.contactId,
        status: 'No active assignment detected',
        projectId: input.projectId,
        projectName: input.projectName,
        formId: input.formId,
        formName: input.formName,
        formVersionId: input.formVersionId,
      },
      newState: {
        userEmail: affectedEmail,
        contactId: input.contactId,
        role: input.targetRole ?? 'Data Collector / Bank Officer',
        status: 'Active',
        projectId: input.projectId,
        projectName: input.projectName,
        formId: input.formId,
        formName: input.formName,
        formVersionId: input.formVersionId,
        assignmentId: assignmentKey,
      },
    };
  }

  buildAssignFormAccessPreview(input: AssignFormAccessInput): AccessWritePreview {
    return this.buildAccessWritePreview(this.buildAssignFormAccessCommand(input));
  }

  async submitAssignFormAccess(input: AssignFormAccessInput): Promise<AssignFormAccessResult> {
    const preview = this.buildAssignFormAccessPreview(input);
    if (!this.areAssignFormWritesEnabled()) {
      throw new AccessWriteDisabledError(ACCESS_ASSIGN_FORM_DISABLED_MESSAGE);
    }

    const affectedEmail = input.affectedEmail.trim().toLowerCase();
    const existingAssignment = await this.findFormAssignmentByEmailAndVersion(affectedEmail, input.formVersionId);
    if (existingAssignment) {
      if (existingAssignment.mp_lifecyclestatus !== FORM_ASSIGNMENT_LIFECYCLE_ACTIVE) {
        await this.reactivateFormAssignment(existingAssignment.mp_formassignmentid, affectedEmail, input.formVersionId);
        const auditId = await this.createAccessAuditRequested(preview);
        await this.updateAccessAuditResult(auditId, 'Succeeded', 'Existing form assignment was reactivated.');
        return {
          status: 'created',
          requestId: preview.requestId,
          auditKey: preview.auditKey,
          assignmentId: existingAssignment.mp_formassignmentid,
          preview,
        };
      }

      const auditId = await this.createAccessAuditRequested(preview);
      await this.updateAccessAuditResult(auditId, 'Succeeded', 'Access already existed; no duplicate assignment row was created.');
      return {
        status: 'already-assigned',
        requestId: preview.requestId,
        auditKey: preview.auditKey,
        existingAssignmentId: existingAssignment.mp_formassignmentid,
        preview,
      };
    }

    const auditId = await this.createAccessAuditRequested(preview);
    try {
      const assignmentId = await this.createAssignFormAssignment(preview);
      await this.updateAccessAuditResult(auditId, 'Succeeded', 'Form assignment created.');
      return {
        status: 'created',
        requestId: preview.requestId,
        auditKey: preview.auditKey,
        assignmentId,
        preview,
      };
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'Unknown assignment create failure.';
      await this.updateAccessAuditResult(auditId, 'Failed', message);
      throw caught;
    }
  }

  async submitManageAccessUser(input: ManageAccessUserInput): Promise<ManageAccessUserResult> {
    if (!this.areAccessWritesEnabled()) {
      throw new AccessWriteDisabledError();
    }

    const reason = input.reason.trim();
    if (!reason) {
      throw new Error('Business reason is required before changing user access.');
    }

    const affectedEmail = input.user.email.trim().toLowerCase();
    const normalizedNewEmail = input.newEmail?.trim().toLowerCase();
    if (input.action === 'CorrectEmail' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedNewEmail ?? '')) {
      throw new Error('Enter the corrected email address before applying the change.');
    }
    if (input.action === 'CorrectEmail' && normalizedNewEmail === affectedEmail) {
      throw new Error('The corrected email must be different from the current email.');
    }
    if (input.user.assignments.length === 0) {
      throw new Error('No assignment rows were found for this user.');
    }
    if (input.action === 'CorrectEmail' && normalizedNewEmail) {
      await this.assertEmailCorrectionTargetIsAvailable(input.user.assignments, normalizedNewEmail);
    }

    const command: AccessWriteCommand = {
      action: input.action === 'CorrectEmail' ? 'CorrectEmail' : 'RemoveAssignment',
      affectedEmail,
      targetRole: input.user.role,
      scopeType: 'Assignment',
      reason,
      sourceRoute: input.sourceRoute,
      formAssignmentId: input.user.assignments[0]?.assignmentId,
      formVersionId: input.user.assignments[0]?.formVersionId,
      previousState: {
        userEmail: affectedEmail,
        contactId: input.user.contactId,
        role: input.user.role,
        status: input.user.accessStatus,
        assignmentId: input.user.assignments[0]?.assignmentId,
      },
      newState: {
        userEmail: normalizedNewEmail ?? affectedEmail,
        contactId: input.user.contactId,
        role: input.user.role,
        status: input.action === 'CorrectEmail' ? input.user.accessStatus : 'Inactive',
        assignmentId: input.user.assignments[0]?.assignmentId,
      },
    };
    const preview = this.buildAccessWritePreview(command);
    const auditId = await this.createAccessAuditRequested(preview);

    try {
      let updatedContact = false;
      if (input.action === 'CorrectEmail' && normalizedNewEmail) {
        if (input.user.contactId) {
          await this.updateContactEmail(input.user.contactId, normalizedNewEmail);
          updatedContact = true;
        }
        await Promise.all(input.user.assignments.map((assignment) => this.updateFormAssignmentEmail(assignment, normalizedNewEmail)));
      } else {
        await Promise.all(input.user.assignments.map((assignment) => this.deactivateFormAssignment(assignment.assignmentId)));
      }

      const updatedAssignments = input.user.assignments.length;
      const resultMessage = input.action === 'CorrectEmail'
        ? `Email corrected to ${normalizedNewEmail}; ${updatedAssignments} assignment row${updatedAssignments === 1 ? '' : 's'} updated.`
        : `${updatedAssignments} assignment row${updatedAssignments === 1 ? '' : 's'} deactivated.`;
      await this.updateAccessAuditResult(auditId, 'Succeeded', resultMessage);
      return {
        requestId: preview.requestId,
        auditKey: preview.auditKey,
        action: input.action,
        affectedEmail,
        newEmail: normalizedNewEmail,
        updatedContact,
        updatedAssignments,
        preview,
      };
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'Unknown user lifecycle update failure.';
      await this.updateAccessAuditResult(auditId, 'Failed', message);
      throw caught;
    }
  }

  async submitUserOnboardingAccess(input: UserOnboardingAccessInput): Promise<UserOnboardingAccessResult> {
    if (!this.getUserOnboardingReadiness().enabled) {
      throw new AccessWriteDisabledError(ACCESS_ONBOARDING_DISABLED_MESSAGE);
    }
    if (input.forms.length === 0) {
      throw new Error('At least one form must be selected before creating access.');
    }

    const email = input.affectedEmail.trim().toLowerCase();
    const fullName = input.fullName.trim();
    if (!email || !fullName) {
      throw new Error('Full name and email are required before creating access.');
    }

    const occurredAt = new Date().toISOString();
    const requestId = this.buildOnboardingRequestId(email, occurredAt);
    const requestKey = this.buildOnboardingRequestKey(email, requestId);
    const queueRecordId = await this.createOnboardingRequest({
      ...input,
      affectedEmail: email,
      fullName,
      requestId,
      requestKey,
    });
    const isExistingUser = input.requestType === 'ExistingUser';
    return {
      status: 'queued',
      requestId,
      requestKey,
      queueRecordId,
      queueStatus: 'Pending',
      requestType: input.requestType,
      contactCreated: false,
      emailDelivery: isExistingUser ? 'queued-for-assignment-notification' : 'queued-for-invitation',
      emailMessage: isExistingUser
        ? 'Assignment notification and access writes are queued for server-side processing.'
        : 'Power Pages invitation and access writes are queued for server-side processing.',
      assignmentResults: [],
    };
  }

  async getUserOnboardingRequestResult(queueRecordId: string): Promise<UserOnboardingAccessResult> {
    if (this.shouldUseLocalFixture()) {
      throw new Error('Onboarding request refresh is unavailable in local fixture mode.');
    }

    const row = await this.get<OnboardingRequestRow>(
      `${ACCESS_ONBOARDING_QUEUE_WEB_API_PATH}(${encodeURIComponent(queueRecordId)})?$select=mp_requestkey,mp_requestid,mp_status,mp_requesttype,mp_contactid,mp_resultmessage,mp_invitationid,mp_invitationcode,mp_invitationredeemurl,mp_invitationexpiresat,mp_invitationstatus,mp_invitationdeliverymode,mp_replacementofrequestid`,
    );
    return this.toUserOnboardingAccessResult(queueRecordId, row);
  }

  async listAssignedForms(): Promise<FormAssignmentSummary[]> {
    return measureAsync('api:listAssignedForms', async () => {
      if (this.shouldUseLocalFixture()) {
        return devAssignedForms;
      }

      const signedInEmail = this.getSignedInUserEmail();
      if (!signedInEmail) {
        throw new Error('Power Pages session did not provide a signed-in email for assignment filtering.');
      }

      try {
        const assignments = await this.get<DataverseCollection<FormAssignmentMetadataRow>>(
          `/_api/mp_formassignments?fetchXml=${encodeURIComponent(this.buildAssignedFormsFetchXml(signedInEmail, 20))}`,
        );
        return assignments.value.map((assignment) => this.toLinkedSummary(assignment));
      } catch {
        console.warn('[TACATDP perf] Linked assignment metadata query failed; falling back to metadata hydration.');
      }

      const assignments = await this.get<DataverseCollection<FormAssignmentRow>>(
        `/_api/mp_formassignments?$select=mp_formassignmentid,mp_assignmentkey,mp_useremail,mp_lifecyclestatus,_mp_formversion_value&$filter=mp_useremail eq '${this.escapeODataString(signedInEmail)}' and mp_lifecyclestatus eq ${FORM_ASSIGNMENT_LIFECYCLE_ACTIVE}&$top=20`,
      );

      return Promise.all(assignments.value.map((assignment) => this.toSummary(assignment)));
    });
  }

  async listAccessUsers(): Promise<AccessUserSummary[]> {
    return measureAsync('api:listAccessUsers', async () => {
      const assignmentSummaries = this.shouldUseLocalFixture()
        ? devAssignedForms
        : await this.listAllFormAssignments({ includeInactive: true });
      const emails = Array.from(new Set(assignmentSummaries
        .map((assignment) => assignment.userEmail?.trim())
        .filter((value): value is string => Boolean(value))))
        .sort((left, right) => left.localeCompare(right));
      const contacts = await this.listContactsByEmail(emails);
      const roleMap = contacts
        ? await this.listPowerPageRolesByContact(Array.from(contacts.values()).map((contact) => contact.contactid))
        : null;

      return emails.map((email) => {
        const userAssignments = assignmentSummaries.filter((assignment) => assignment.userEmail?.trim() === email);
        const contact = contacts?.get(email.toLowerCase());
        const activeAssignmentCount = userAssignments.filter((assignment) => this.isActiveFormAssignment(assignment)).length;
        return {
          id: contact?.contactid ?? email,
          name: contact?.fullname || email,
          email,
          contactId: contact?.contactid,
          contactState: contact ? 'active' : contacts === null ? 'unavailable' : 'missing',
          role: this.resolveAccessUserRole(email, contact, roleMap),
          accessStatus: contact || contacts === null
            ? activeAssignmentCount > 0 ? 'Active' : 'Needs admin review'
            : 'Needs contact check',
          assignments: userAssignments,
          projectCount: activeAssignmentCount > 0 ? 1 : 0,
          formCount: activeAssignmentCount,
        };
      });
    });
  }

  async listUserActivationDiagnostics(): Promise<UserActivationDiagnostic[]> {
    return measureAsync('api:listUserActivationDiagnostics', async () => {
      const assignmentSummaries = this.shouldUseLocalFixture()
        ? devAssignedForms
        : await this.listAllFormAssignments({ includeInactive: true });
      const emails = Array.from(new Set(assignmentSummaries
        .map((assignment) => assignment.userEmail?.trim())
        .filter((value): value is string => Boolean(value))))
        .sort((left, right) => left.localeCompare(right));

      if (this.shouldUseLocalFixture()) {
        return emails.map((email) => {
          const userAssignments = assignmentSummaries.filter((assignment) => assignment.userEmail?.trim() === email);
          return {
            id: `activation:${email.toLowerCase()}`,
            name: email.split('@')[0]?.replace(/[._-]+/g, ' ') || email,
            email,
            contactId: `local-contact:${email.toLowerCase()}`,
            contactStatus: 'ready',
            emailUniquenessStatus: 'ready',
            invitationStatus: 'ready',
            redemptionStatus: 'ready',
            externalIdentityStatus: 'ready',
            webRoleStatus: 'ready',
            assignmentStatus: userAssignments.length > 0 ? 'ready' : 'missing',
            nextAction: userAssignments.length > 0 ? 'Ready' : 'Needs admin review',
            detail: userAssignments.length > 0
              ? 'Local fixture user is treated as activated for UI review.'
              : 'Local fixture user has no active assignment.',
            contactCount: 1,
            activeInvitationCount: 0,
            externalIdentityCount: 1,
            activeAssignmentCount: userAssignments.length,
            latestInvitationStatus: 'Local fixture',
            source: 'local-fixture',
          };
        });
      }

      const contacts = await this.listContactDiagnosticsByEmail(emails);
      const contactIds = contacts ? Array.from(contacts.values()).flat().map((contact) => contact.contactid).filter(Boolean) : [];
      const [invitations, externalIdentities] = await Promise.all([
        this.listInvitationDiagnosticsByContact(contactIds),
        this.listExternalIdentityDiagnosticsByContact(contactIds),
      ]);

      return emails.map((email) => {
        const normalizedEmail = email.toLowerCase();
        const matchingContacts = contacts?.get(normalizedEmail) ?? [];
        const contact = matchingContacts[0];
        const userAssignments = assignmentSummaries.filter((assignment) => assignment.userEmail?.trim() === email);
        const contactInvitations = contact?.contactid
          ? invitations === null ? null : invitations.get(contact.contactid) ?? []
          : null;
        const contactExternalIdentities = contact?.contactid
          ? externalIdentities === null ? null : externalIdentities.get(contact.contactid) ?? []
          : null;
        return this.toActivationDiagnostic({
          email,
          assignments: userAssignments,
          contact,
          contactCount: contacts ? matchingContacts.length : null,
          invitations: contactInvitations,
          externalIdentities: contactExternalIdentities,
        });
      });
    });
  }

  async getFormVersion(formVersionId: string): Promise<FormVersionRow> {
    const cached = this.formVersionRuntimeCache.get(formVersionId);
    if (cached) {
      return cached;
    }

    return measureAsync('api:getFormVersionRuntime', async () => {
      const row = await this.get<FormVersionRow>(
        `/_api/mp_formversions(${encodeURIComponent(formVersionId)})?$select=mp_version,mp_webformsenabled,mp_xformxml,_mp_form_value`,
      );
      this.formVersionRuntimeCache.set(formVersionId, row);
      this.formVersionMetadataCache.set(formVersionId, row);
      return row;
    });
  }

  async getFormVersionMetadata(formVersionId: string): Promise<FormVersionRow> {
    const cached = this.formVersionMetadataCache.get(formVersionId);
    if (cached) {
      return cached;
    }

    return measureAsync('api:getFormVersionMetadata', async () => {
      const row = await this.get<FormVersionRow>(
        `/_api/mp_formversions(${encodeURIComponent(formVersionId)})?$select=mp_version,mp_webformsenabled,_mp_form_value`,
      );
      this.formVersionMetadataCache.set(formVersionId, row);
      return row;
    });
  }

  async getForm(formId: string): Promise<FormRow> {
    const cached = this.formCache.get(formId);
    if (cached) {
      return cached;
    }

    return measureAsync('api:getForm', async () => {
      const row = await this.get<FormRow>(
        `/_api/mp_forms(${encodeURIComponent(formId)})?$select=mp_name,mp_xmlformid`,
      );
      this.formCache.set(formId, row);
      return row;
    });
  }

  async hydrateAssignmentRuntime(assignment: FormAssignmentSummary): Promise<FormAssignmentSummary> {
    return measureAsync('api:hydrateAssignmentRuntime', async () => {
      if (assignment.xformXml) {
        return assignment;
      }

      const formVersion = await this.getFormVersion(assignment.formVersionId);
      if (!formVersion.mp_xformxml) {
        throw new Error(`Form version ${assignment.formVersionId} does not include XForm XML.`);
      }
      const cacheKey = this.buildXFormCacheKey(assignment.formVersionId, formVersion.mp_version, formVersion.mp_xformxml);
      const cached = await measureAsync('api:getCachedXForm', async () => this.getCachedXForm(cacheKey));
      const xformXml = cached ?? await this.resolveFormVersionXForm(assignment.formVersionId, formVersion.mp_xformxml);
      if (!cached) {
        await measureAsync('api:setCachedXForm', async () => this.setCachedXForm(cacheKey, xformXml));
      }
      return {
        ...assignment,
        formId: formVersion._mp_form_value || assignment.formId,
        version: formVersion.mp_version || assignment.version,
        xformXml,
      };
    });
  }


  async listBeneficiaries(): Promise<BeneficiaryListItem[]> {
    if (this.shouldUseLocalFixture()) {
      return [];
    }

    const [profiles, identifiers, submissionLinks] = await Promise.all([
      this.get<DataverseCollection<BeneficiaryProfileRow>>(
        '/_api/mp_beneficiaryprofiles?$select=mp_beneficiaryprofileid,mp_name,mp_beneficiarycategory,mp_region,mp_district,mp_verificationstatus,mp_datasource,mp_lastupdatedat,_mp_trackedentity_value&$orderby=mp_lastupdatedat desc&$top=5000',
      ),
      this.get<DataverseCollection<EntityIdentifierRow>>(
        '/_api/mp_entityidentifiers?$select=mp_entityidentifierid,mp_identifiertype,mp_identifiervalue,mp_status,_mp_trackedentity_value&$top=5000',
      ),
      this.get<DataverseCollection<BeneficiarySubmissionLinkRow>>(
        '/_api/mp_beneficiarysubmissionlinks?$select=mp_beneficiarysubmissionlinkid,mp_linkkey,mp_relationshiptype,mp_completeness,mp_reviewstatus,_mp_trackedentity_value,_mp_submission_value&$top=5000',
      ),
    ]);

    const identifiersByTrackedEntity = this.groupRowsByLookup(identifiers.value, '_mp_trackedentity_value');
    const linksByTrackedEntity = this.groupRowsByLookup(submissionLinks.value, '_mp_trackedentity_value');

    return profiles.value.map((profile, index) => {
      const trackedEntityId = profile._mp_trackedentity_value;
      const profileIdentifiers = trackedEntityId ? (identifiersByTrackedEntity.get(trackedEntityId) ?? []) : [];
      const profileLinks = trackedEntityId ? (linksByTrackedEntity.get(trackedEntityId) ?? []) : [];
      const customerId = profileIdentifiers.find((identifier) => identifier.mp_identifiertype === IDENTIFIER_CUSTOMER_ID)?.mp_identifiervalue;
      const phone = profileIdentifiers.find((identifier) => identifier.mp_identifiertype === IDENTIFIER_PHONE)?.mp_identifiervalue;
      const recordId = customerId || phone || trackedEntityId || profile.mp_beneficiaryprofileid || `BEN-${index + 1}`;
      const verificationStatus = this.mapBeneficiaryVerificationStatus(profile.mp_verificationstatus);
      const latestLink = profileLinks[0];
      const completeness = latestLink?.mp_completeness !== undefined ? `${latestLink.mp_completeness}%` : 'Not projected';
      const source = profile.mp_datasource || 'Dataverse baseline import';
      const updatedAt = profile.mp_lastupdatedat ? this.formatDisplayDate(profile.mp_lastupdatedat) : 'Not recorded';
      const name = profile.mp_name || `Beneficiary ${index + 1}`;

      return {
        id: recordId,
        name,
        category: this.mapBeneficiaryCategory(profile.mp_beneficiarycategory),
        region: profile.mp_region || 'Not recorded',
        district: profile.mp_district || 'Not recorded',
        borrowerStatus: 'Pending verification',
        loanType: 'Not financed',
        technology: 'Awaiting classification',
        projectParticipation: {
          programme: 'TACATDP',
          project: 'TACATDP baseline monitoring',
          implementationPartner: 'CRDB Sustainable Finance Unit',
          enrolmentDate: updatedAt,
          participationRole: 'Baseline beneficiary',
        },
        finance: {
          loanAccountRef: 'Not linked in minimal beneficiary schema',
          disbursedAmount: 'Not available',
          outstandingBalance: 'Not available',
          repaymentRate: 'Not available',
        },
        technologiesFinanced: [{
          name: 'Awaiting classification',
          category: 'Baseline import',
          adoptionStage: 'Planned',
        }],
        trainingSummary: {
          sessionsAttended: 0,
          lastTopic: 'Not captured in minimal beneficiary schema',
          completionRate: 'Not available',
          lastTrainingDate: 'Not available',
        },
        latestSubmission: {
          form: 'TACATDP baseline and monitoring',
          reportingPeriod: 'Baseline',
          status: latestLink ? 'Submitted' : 'Awaiting submission',
          completeness,
          dataSource: source,
        },
        identityGovernance: {
          matchState: 'Linked to tracked entity',
          matchSignals: [customerId ? 'Customer ID' : '', phone ? 'Phone' : '', trackedEntityId ? 'Tracked entity' : ''].filter(Boolean).join(' · ') || 'Tracked entity profile',
          reviewerDecision: verificationStatus === 'Verified' ? 'Accepted as beneficiary entity' : 'Pending review',
        },
        groupMembership: {
          membershipType: 'Individual beneficiary',
          membersLinked: 'Not modelled in minimal schema',
          membershipStatus: verificationStatus === 'Verified' ? 'Active' : 'Pending verification',
        },
        locationHistory: {
          currentLocation: `${profile.mp_region || 'Not recorded'} · ${profile.mp_district || 'Not recorded'}`,
          source,
          effectiveFrom: updatedAt,
          historyState: 'Current profile location',
        },
        outcomeSnapshot: {
          areaUnderImprovedPractices: 'Not calculated',
          yieldIncrease: 'Not calculated',
          climateEstimate: 'Not calculated',
        },
        futureDataverseMapping: {
          table: 'mp_TrackedEntity + mp_BeneficiaryProfile',
          recordId: profile.mp_beneficiaryprofileid,
          relationshipNotes: latestLink
            ? 'mp_BeneficiarySubmissionLink connects this beneficiary to the imported baseline submission.'
            : 'No baseline submission link was found for this beneficiary.',
        },
        trained: false,
        verificationStatus,
        lastUpdated: updatedAt,
        source: 'dataverse',
      } satisfies BeneficiaryListItem;
    });
  }

  async listSavedSubmissions(): Promise<SubmissionSummary[]> {
    return measureAsync('api:listSavedSubmissions', async () => {
      if (this.shouldUseLocalFixture()) {
        return [];
      }

      const submissions = await this.get<DataverseCollection<SubmissionRow>>(
        `/_api/mp_submissions?$select=mp_submissionid,mp_instanceid,mp_useremail,mp_submittedat,mp_updatedat,mp_lifecyclestatus,mp_reviewstate&$filter=mp_lifecyclestatus eq ${SUBMISSION_LIFECYCLE_SUBMITTED}&$orderby=mp_updatedat desc&$top=5000`,
      );

      return Promise.all(submissions.value.map(async (submission) => {
        const latestVersion = await this.getLatestSubmissionVersionByInstanceId(submission.mp_instanceid);
        const metadata = this.parseSubmissionMetadata(latestVersion?.mp_submissionjson);
        return {
          submissionId: submission.mp_submissionid,
          instanceId: submission.mp_instanceid,
          displayName: metadata.instanceName,
          userEmail: submission.mp_useremail,
          submittedAt: submission.mp_submittedat,
          updatedAt: submission.mp_updatedat,
          lifecycleStatus: submission.mp_lifecyclestatus,
          reviewState: submission.mp_reviewstate,
          assignmentKey: metadata.assignmentKey,
          formVersionId: metadata.formVersionId,
          xmlFormId: metadata.xmlFormId,
          versionNumber: latestVersion?.mp_versionnumber,
        };
      }));
    });
  }

  async listSubmissionReportRows(input: {
    page: number;
    pageSize: number;
    filters?: ReportingFilters;
  }): Promise<SubmissionReportPage> {
    if (this.shouldUseLocalFixture()) {
      const query = input.filters?.search?.trim().toLowerCase();
      const scope = this.getReportingAccessScope();
      const rows = devReportingRows
        .filter((row) => scope.mode === 'all-records' || row.mp_useremail?.trim().toLowerCase() === scope.ownerEmail?.trim().toLowerCase())
        .filter((row) => !query || [row.mp_displayname, row.mp_instanceid, row.mp_useremail]
          .some((value) => value?.toLowerCase().includes(query)));
      const start = (input.page - 1) * input.pageSize;
      return { rows: rows.slice(start, start + input.pageSize), total: rows.length, page: input.page, pageSize: input.pageSize };
    }

    const page = Math.max(1, input.page);
    const pageSize = Math.min(Math.max(1, input.pageSize), 100);
    const fetchXml = this.buildReportingFetchXml(page, pageSize, input.filters ?? {}, this.getReportingAccessScope());

    const result = await this.get<DataverseCollection<SubmissionReportRow>>(
      `/_api/mp_submissionreportrows?fetchXml=${encodeURIComponent(fetchXml)}`,
    );
    return {
      rows: result.value,
      total: result['@odata.count'] ?? result.value.length,
      page,
      pageSize,
    };
  }

  async listAllSubmissionReportRows(filters: ReportingFilters = {}): Promise<SubmissionReportRow[]> {
    const result = await this.listSubmissionReportRows({ page: 1, pageSize: 100, filters });
    if (result.total > result.rows.length) {
      throw new Error(`This export contains ${result.total} rows. The browser CSV limit is 100 rows for this prototype; narrow the filters before exporting.`);
    }
    return result.rows;
  }

  getReportingAccessScope(): ReportingAccessScope {
    if (this.isCurrentUserAccessAdmin()) {
      return { mode: 'all-records' };
    }

    const ownerEmail = this.getSignedInUserEmail();
    if (!ownerEmail) {
      throw new Error('Signed-in user email is required before reading reporting rows.');
    }
    return { mode: 'own-records', ownerEmail };
  }

  async listSubmissionAnswers(reportRowId: string): Promise<SubmissionAnswerRow[]> {
    if (this.shouldUseLocalFixture()) {
      return devSubmissionAnswers.filter((answer) => answer._mp_submissionreportrow_value === reportRowId);
    }

    const query = new URLSearchParams({
      '$select': [
        'mp_submissionanswerid',
        'mp_answerkey',
        'mp_instanceid',
        'mp_fieldpath',
        'mp_fieldname',
        'mp_fieldlabel',
        'mp_valuetext',
        'mp_valuedecimal',
        'mp_valuedate',
        'mp_valueboolean',
        'mp_valuejson',
        '_mp_submissionreportrow_value',
        '_mp_submissionrepeatrow_value',
      ].join(','),
      '$filter': `_mp_submissionreportrow_value eq ${reportRowId}`,
      '$orderby': 'mp_fieldpath asc',
      '$top': '5000',
    });
    const result = await this.get<DataverseCollection<SubmissionAnswerRow>>(
      `/_api/mp_submissionanswers?${query.toString()}`,
    );
    return result.value;
  }

  async listExportSettings(): Promise<ExportSettingRow[]> {
    const accessScope = this.getReportingAccessScope();
    if (this.shouldUseLocalFixture()) {
      return accessScope.mode === 'all-records'
        ? devExportSettings
        : devExportSettings.filter((setting) => setting.mp_createdbyemail?.trim().toLowerCase() === accessScope.ownerEmail?.trim().toLowerCase());
    }

    const ownerFilter = accessScope.mode === 'own-records'
      ? `&$filter=mp_createdbyemail eq '${this.escapeODataString(accessScope.ownerEmail ?? '')}'`
      : '';
    const result = await this.get<DataverseCollection<ExportSettingRow>>(
      `/_api/mp_exportsettings?$select=mp_exportsettingid,mp_exportkey,mp_name,mp_format,mp_scope,mp_filterjson,mp_createdbyemail,mp_createdat,mp_updatedat${ownerFilter}&$orderby=mp_updatedat desc&$top=100`,
    );
    return result.value;
  }

  async createCsvExportSetting(input: CreateCsvExportSettingInput): Promise<string> {
    const normalizedName = input.name.trim();
    if (!normalizedName) {
      throw new Error('Enter an export name before saving.');
    }

    const now = new Date().toISOString();
    const exportKey = `tacatdp:${input.formVersionId || 'all'}:${this.slugify(normalizedName)}:${Date.now()}`;
    if (this.shouldUseLocalFixture()) {
      const id = `local-export-${Date.now()}`;
      devExportSettings.unshift({
        mp_exportsettingid: id,
        mp_exportkey: exportKey,
        mp_name: normalizedName,
        mp_format: EXPORT_FORMAT_CSV,
        mp_scope: EXPORT_SCOPE_CURRENT_FILTERS,
        mp_filterjson: JSON.stringify({ ...input.filters, formVersionId: input.formVersionId }),
        mp_createdbyemail: this.getSignedInUserEmail(),
        mp_createdat: now,
        mp_updatedat: now,
      });
      return id;
    }
    return this.createRecord('/_api/mp_exportsettings', {
      mp_exportkey: exportKey,
      mp_name: normalizedName,
      mp_format: EXPORT_FORMAT_CSV,
      mp_scope: EXPORT_SCOPE_CURRENT_FILTERS,
      mp_includerepeats: false,
      mp_uselabels: true,
      mp_includemedialinks: false,
      mp_filterjson: JSON.stringify({ ...input.filters, formVersionId: input.formVersionId }),
      mp_columnjson: JSON.stringify(['record', 'instance_id', 'owner', 'submitted_at', 'updated_at', 'version', 'lifecycle', 'review', 'projection_status']),
      mp_createdbyemail: this.getSignedInUserEmail(),
      mp_createdat: now,
      mp_updatedat: now,
    });
  }

  async getSubmissionFormContext(submission: SubmissionSummary): Promise<FormAssignmentSummary> {
    if (!submission.formVersionId) {
      throw new Error(`Submission ${submission.instanceId} does not include formVersionId metadata for edit mode.`);
    }

    const formVersion = await this.getFormVersion(submission.formVersionId);
    const form = await this.getForm(formVersion._mp_form_value);
    if (!formVersion.mp_xformxml) {
      throw new Error(`Form version ${submission.formVersionId} does not include XForm XML.`);
    }
    const xformXml = await this.resolveFormVersionXForm(submission.formVersionId, formVersion.mp_xformxml);

    return {
      assignmentId: `submission:${submission.submissionId}`,
      assignmentKey: submission.assignmentKey ?? `submission:${submission.instanceId}`,
      userEmail: submission.userEmail,
      formVersionId: submission.formVersionId,
      formId: formVersion._mp_form_value,
      formName: form.mp_name,
      xmlFormId: form.mp_xmlformid,
      version: formVersion.mp_version,
      xformXml,
    };
  }

  async getLatestSubmissionXml(instanceId: string): Promise<string> {
    const latestVersion = await this.getLatestSubmissionVersionByInstanceId(instanceId);
    if (!latestVersion?.mp_xformsubmissionxml) {
      throw new Error(`No saved XForm submission XML was found for ${instanceId}.`);
    }

    return latestVersion.mp_xformsubmissionxml;
  }

  async submitOdkSubmission(
    assignment: FormAssignmentSummary,
    payload: unknown,
    options: { existingSubmission?: SubmissionSummary | null } = {},
  ): Promise<OdkSubmitResult> {
    if (this.shouldUseLocalFixture()) {
      return {
        instanceId: `local:${crypto.randomUUID()}`,
        displayName: 'Local development record',
        submissionId: 'local-submission',
        submissionVersionId: 'local-submission-version',
        versionNumber: 1,
        attachmentCount: 0,
        attachmentBinaryUploadCount: 0,
        attachmentWarnings: [],
      };
    }

    const xml = await this.extractSubmittedXml(payload);
    const attachments = this.extractAttachmentPayloads(payload);
    const submittedInstanceId = this.extractInstanceId(xml) ?? `uuid:${crypto.randomUUID()}`;
    const instanceId = options.existingSubmission?.instanceId ?? submittedInstanceId;
    const canonicalXml = this.normalizeInstanceId(xml, instanceId);
    const now = new Date().toISOString();
    const existingSubmission = options.existingSubmission
      ? { mp_submissionid: options.existingSubmission.submissionId, mp_instanceid: options.existingSubmission.instanceId }
      : await this.findSubmissionByInstanceId(instanceId);
    const submissionId = existingSubmission?.mp_submissionid ?? await this.createSubmission(assignment, instanceId, now);
    const versionNumber = await this.nextSubmissionVersionNumber(instanceId);
    const submissionVersionId = await this.createSubmissionVersion({
      assignment,
      instanceId,
      now,
      payload,
      submissionId,
      versionNumber,
      xml: canonicalXml,
    });
    if (existingSubmission) {
      await this.updateSubmission(existingSubmission.mp_submissionid, now);
    }
    const attachmentResults = await this.createSubmissionAttachments(submissionVersionId, attachments, now);

    return {
      instanceId,
      displayName: this.resolveInstanceName(canonicalXml),
      submissionId,
      submissionVersionId,
      versionNumber,
      attachmentCount: attachmentResults.length,
      attachmentBinaryUploadCount: attachmentResults.filter((result) => result.binaryUploaded).length,
      attachmentWarnings: attachmentResults.flatMap((result) => result.warning ? [result.warning] : []),
    };
  }

  private async toSummary(assignment: FormAssignmentRow): Promise<FormAssignmentSummary> {
    const formVersion = await this.getFormVersionMetadata(assignment._mp_formversion_value);
    const form = await this.getForm(formVersion._mp_form_value);

    return {
      assignmentId: assignment.mp_formassignmentid,
      assignmentKey: assignment.mp_assignmentkey,
      userEmail: assignment.mp_useremail,
      lifecycleStatus: assignment.mp_lifecyclestatus,
      formVersionId: assignment._mp_formversion_value,
      formId: formVersion._mp_form_value,
      formName: form.mp_name,
      xmlFormId: form.mp_xmlformid,
      version: formVersion.mp_version,
    };
  }

  private toLinkedSummary(assignment: FormAssignmentMetadataRow): FormAssignmentSummary {
    const formVersionId = assignment._mp_formversion_value;
    const formId = this.getAliasedString(assignment, 'fv.mp_form', '_fv.mp_form_value');
    const formName = this.getAliasedString(assignment, 'form.mp_name');
    const xmlFormId = this.getAliasedString(assignment, 'form.mp_xmlformid');
    const version = this.getAliasedString(assignment, 'fv.mp_version');

    if (!formVersionId || !formId || !formName || !xmlFormId || !version) {
      throw new Error('Linked assignment metadata response was missing form or form-version aliases.');
    }

    return {
      assignmentId: assignment.mp_formassignmentid,
      assignmentKey: assignment.mp_assignmentkey,
      userEmail: assignment.mp_useremail,
      lifecycleStatus: assignment.mp_lifecyclestatus,
      formVersionId,
      formId,
      formName,
      xmlFormId,
      version,
    };
  }

  private async listAllFormAssignments(options: { includeInactive?: boolean } = {}): Promise<FormAssignmentSummary[]> {
    const filter = options.includeInactive ? '' : `&$filter=mp_lifecyclestatus eq ${FORM_ASSIGNMENT_LIFECYCLE_ACTIVE}`;
    const assignments = await this.get<DataverseCollection<FormAssignmentRow>>(
      `/_api/mp_formassignments?$select=mp_formassignmentid,mp_assignmentkey,mp_useremail,mp_lifecyclestatus,_mp_formversion_value${filter}&$orderby=mp_useremail asc&$top=200`,
    );
    return Promise.all(assignments.value.map((assignment) => this.toSummary(assignment)));
  }

  private isActiveFormAssignment(assignment: Pick<FormAssignmentSummary, 'lifecycleStatus'>): boolean {
    return assignment.lifecycleStatus === FORM_ASSIGNMENT_LIFECYCLE_ACTIVE;
  }

  private async listContactsByEmail(emails: string[]): Promise<Map<string, ContactRow> | null> {
    const contacts = new Map<string, ContactRow>();
    if (emails.length === 0) {
      return contacts;
    }

    if (this.shouldUseLocalFixture()) {
      for (const email of emails) {
        contacts.set(email.toLowerCase(), {
          contactid: `local-contact:${email.toLowerCase()}`,
          fullname: email.split('@')[0]?.replace(/[._-]+/g, ' ') || email,
          emailaddress1: email,
          statecode: 0,
        });
      }
      return contacts;
    }

    const filter = emails
      .slice(0, 50)
      .map((email) => `emailaddress1 eq '${this.escapeODataString(email)}'`)
      .join(' or ');
    try {
      const result = await this.get<DataverseCollection<ContactRow>>(
        `/_api/contacts?$select=contactid,fullname,emailaddress1,statecode&$filter=${encodeURIComponent(filter)}&$top=50`,
      );
      for (const contact of result.value) {
        if (contact.emailaddress1) {
          contacts.set(contact.emailaddress1.toLowerCase(), contact);
        }
      }
    } catch {
      return null;
    }

    return contacts;
  }

  private async listPowerPageRolesByContact(contactIds: string[]): Promise<Map<string, string[]> | null> {
    const rolesByContact = new Map<string, string[]>();
    const uniqueContactIds = Array.from(new Set(contactIds.filter(Boolean))).slice(0, 50);
    if (uniqueContactIds.length === 0) {
      return rolesByContact;
    }

    try {
      await Promise.all(uniqueContactIds.map(async (contactId) => {
        const result = await this.get<DataverseCollection<PowerPageRoleRow>>(
          `/_api/contacts(${encodeURIComponent(contactId)})/powerpagecomponent_mspp_webrole_contact?$select=powerpagecomponentid,name,powerpagecomponenttype&$top=50`,
        );
        rolesByContact.set(
          contactId,
          result.value
            .filter((role) => role.powerpagecomponenttype === 11 && role.name)
            .map((role) => role.name as string),
        );
      }));
      return rolesByContact;
    } catch {
      return null;
    }
  }

  private resolveAccessUserRole(
    email: string,
    contact: ContactRow | undefined,
    rolesByContact: Map<string, string[]> | null,
  ): AccessUserSummary['role'] {
    const roles = contact?.contactid ? rolesByContact?.get(contact.contactid) ?? [] : [];
    if (roles.some((role) => ACCESS_ADMIN_POWERPAGES_ROLES.includes(role))) {
      return 'Platform Administrator';
    }
    if (rolesByContact === null && this.isCurrentSessionEmail(email) && this.isCurrentUserAccessAdmin()) {
      return 'Platform Administrator';
    }
    return 'Data Collector / Bank Officer';
  }

  private async listContactDiagnosticsByEmail(emails: string[]): Promise<Map<string, ContactRow[]> | null> {
    const contacts = new Map<string, ContactRow[]>();
    if (emails.length === 0) {
      return contacts;
    }

    const filter = emails
      .slice(0, 50)
      .map((email) => `emailaddress1 eq '${this.escapeODataString(email)}'`)
      .join(' or ');
    try {
      const result = await this.get<DataverseCollection<ContactRow>>(
        `/_api/contacts?$select=contactid,fullname,emailaddress1,statecode,adx_identity_username,adx_identity_logonenabled,adx_identity_emailaddress1confirmed&$filter=${encodeURIComponent(filter)}&$top=100`,
      );
      for (const contact of result.value) {
        if (!contact.emailaddress1) continue;
        const key = contact.emailaddress1.toLowerCase();
        contacts.set(key, [...(contacts.get(key) ?? []), contact]);
      }
    } catch {
      return null;
    }

    return contacts;
  }

  private async listInvitationDiagnosticsByContact(contactIds: string[]): Promise<Map<string, InvitationDiagnosticRow[]> | null> {
    const invitations = new Map<string, InvitationDiagnosticRow[]>();
    if (contactIds.length === 0) {
      return invitations;
    }

    const filter = contactIds
      .slice(0, 50)
      .map((contactId) => `_adx_invitecontact_value eq ${contactId}`)
      .join(' or ');
    try {
      const result = await this.get<DataverseCollection<InvitationDiagnosticRow>>(
        `/_api/adx_invitations?$select=adx_invitationid,adx_name,adx_expirydate,statuscode,statecode,createdon,modifiedon,_adx_invitecontact_value&$filter=${encodeURIComponent(filter)}&$orderby=createdon desc&$top=100`,
      );
      for (const invitation of result.value) {
        const contactId = invitation._adx_invitecontact_value;
        if (!contactId) continue;
        invitations.set(contactId, [...(invitations.get(contactId) ?? []), invitation]);
      }
      return invitations;
    } catch {
      return null;
    }
  }

  private async listExternalIdentityDiagnosticsByContact(contactIds: string[]): Promise<Map<string, ExternalIdentityDiagnosticRow[]> | null> {
    const identities = new Map<string, ExternalIdentityDiagnosticRow[]>();
    if (contactIds.length === 0) {
      return identities;
    }

    const filter = contactIds
      .slice(0, 50)
      .map((contactId) => `_adx_contactid_value eq ${contactId}`)
      .join(' or ');
    try {
      const result = await this.get<DataverseCollection<ExternalIdentityDiagnosticRow>>(
        `/_api/adx_externalidentities?$select=adx_externalidentityid,adx_username,createdon,_adx_contactid_value&$filter=${encodeURIComponent(filter)}&$top=100`,
      );
      for (const identity of result.value) {
        const contactId = identity._adx_contactid_value;
        if (!contactId) continue;
        identities.set(contactId, [...(identities.get(contactId) ?? []), identity]);
      }
      return identities;
    } catch {
      return null;
    }
  }

  private toActivationDiagnostic(input: {
    email: string;
    assignments: FormAssignmentSummary[];
    contact?: ContactRow;
    contactCount: number | null;
    invitations: InvitationDiagnosticRow[] | null | undefined;
    externalIdentities: ExternalIdentityDiagnosticRow[] | null | undefined;
  }): UserActivationDiagnostic {
    const contactUnavailable = input.contactCount === null;
    const contactActive = input.contact?.statecode === 0;
    const contactStatus = input.contact
      ? contactActive ? 'ready' : 'review'
      : contactUnavailable ? 'unavailable' : 'missing';
    const emailUniquenessStatus = input.contactCount === null
      ? 'unavailable'
      : input.contactCount === 1
      ? 'ready'
      : input.contactCount === 0 ? 'missing' : 'review';
    const invitationRows = input.invitations;
    const identityRows = input.externalIdentities;
    const invitationUnavailable = invitationRows === null || invitationRows === undefined;
    const identityUnavailable = identityRows === null || identityRows === undefined;
    const activeInvitations = invitationRows?.filter((invitation) => invitation.statecode === 0) ?? [];
    const latestInvitation = invitationRows?.[0];
    const invitationExpired = Boolean(latestInvitation?.adx_expirydate && new Date(latestInvitation.adx_expirydate).getTime() <= Date.now());
    const externalIdentityCount = identityRows?.length ?? null;
    const hasExternalIdentity = Boolean(externalIdentityCount && externalIdentityCount > 0);
    const invitationStatus = invitationUnavailable
      ? 'unavailable'
      : hasExternalIdentity
        ? 'ready'
        : activeInvitations.length > 0 && !invitationExpired
          ? 'pending'
          : 'missing';
    const externalIdentityStatus = identityUnavailable
      ? 'unavailable'
      : hasExternalIdentity ? 'ready' : 'missing';
    const redemptionStatus = hasExternalIdentity
      ? 'ready'
      : invitationStatus === 'pending'
        ? 'pending'
        : invitationStatus === 'unavailable'
          ? 'unavailable'
          : 'missing';
    const activeAssignmentCount = input.assignments.filter((assignment) => this.isActiveFormAssignment(assignment)).length;
    const assignmentStatus = activeAssignmentCount > 0
      ? 'ready'
      : input.assignments.length > 0 ? 'review' : 'missing';
    const webRoleStatus = hasExternalIdentity
      ? 'ready'
      : externalIdentityStatus === 'unavailable' ? 'unavailable' : 'pending';
    const nextAction = this.resolveActivationNextAction({
      contactStatus,
      emailUniquenessStatus,
      invitationStatus,
      externalIdentityStatus,
      assignmentStatus,
    });

    return {
      id: `activation:${input.contact?.contactid ?? input.email.toLowerCase()}`,
      name: input.contact?.fullname || input.email,
      email: input.email,
      contactId: input.contact?.contactid,
      contactStatus,
      emailUniquenessStatus,
      invitationStatus,
      redemptionStatus,
      externalIdentityStatus,
      webRoleStatus,
      assignmentStatus,
      nextAction,
      detail: this.describeActivationDiagnostic(nextAction, {
        contactCount: input.contactCount,
        hasExternalIdentity,
        invitationUnavailable,
        identityUnavailable,
        activeInvitationCount: activeInvitations.length,
        assignmentCount: activeAssignmentCount,
      }),
      contactCount: input.contactCount,
      activeInvitationCount: invitationUnavailable ? null : activeInvitations.length,
      externalIdentityCount,
      activeAssignmentCount,
      latestInvitationStatus: latestInvitation?.statuscode === undefined ? undefined : `Status ${latestInvitation.statuscode}`,
      latestInvitationExpiresAt: latestInvitation?.adx_expirydate,
      source: invitationUnavailable || identityUnavailable ? 'partial' : 'dataverse',
    };
  }

  private resolveActivationNextAction(states: {
    contactStatus: UserActivationDiagnostic['contactStatus'];
    emailUniquenessStatus: UserActivationDiagnostic['emailUniquenessStatus'];
    invitationStatus: UserActivationDiagnostic['invitationStatus'];
    externalIdentityStatus: UserActivationDiagnostic['externalIdentityStatus'];
    assignmentStatus: UserActivationDiagnostic['assignmentStatus'];
  }): UserActivationDiagnostic['nextAction'] {
    if (states.contactStatus === 'unavailable' || states.emailUniquenessStatus === 'unavailable') {
      return 'Needs admin review';
    }
    if (states.contactStatus === 'review' || states.emailUniquenessStatus === 'review' || states.assignmentStatus === 'missing') {
      return 'Needs admin review';
    }
    if (states.contactStatus === 'missing') {
      return 'Needs admin review';
    }
    if (states.externalIdentityStatus === 'ready' && states.assignmentStatus === 'ready') {
      return 'Ready';
    }
    if (states.invitationStatus === 'missing') {
      return 'Send code';
    }
    if (states.invitationStatus === 'pending') {
      return 'Await redemption';
    }
    return 'Needs admin review';
  }

  private describeActivationDiagnostic(nextAction: UserActivationDiagnostic['nextAction'], context: {
    contactCount: number | null;
    hasExternalIdentity: boolean;
    invitationUnavailable: boolean;
    identityUnavailable: boolean;
    activeInvitationCount: number;
    assignmentCount: number;
  }): string {
    if (context.contactCount === null) {
      return 'Contact diagnostics are not exposed to the portal. Verify Power Pages Web API settings and table permissions.';
    }
    if (context.contactCount > 1) {
      return 'Multiple contacts use this email. Resolve duplicates before issuing another invitation.';
    }
    if (context.assignmentCount === 0) {
      return 'No active TACATDP form assignment was found for this email.';
    }
    if (context.identityUnavailable || context.invitationUnavailable) {
      return 'One or more diagnostic tables are not exposed to the portal. Verify Power Pages Web API settings and table permissions.';
    }
    if (context.hasExternalIdentity) {
      return 'The contact has a Power Pages external identity and active assignment.';
    }
    if (nextAction === 'Send code') {
      return 'No active invitation was found. Create a fresh invitation before asking the user to sign in.';
    }
    if (nextAction === 'Await redemption') {
      return 'An active invitation exists, but no external identity is bound yet. Ask the user to redeem the link, then refresh diagnostics.';
    }
    return 'Activation state is incomplete. Review contact, invitation, identity, web role, and assignment together.';
  }

  private async createOnboardingRequest(input: UserOnboardingAccessInput & {
    requestId: string;
    requestKey: string;
  }): Promise<string> {
    if (this.shouldUseLocalFixture()) {
      return `local-onboarding-request:${input.requestId}`;
    }

    return this.createRecord(ACCESS_ONBOARDING_QUEUE_WEB_API_PATH, this.toOnboardingRequestWebApiPayload(input));
  }

  private toOnboardingRequestWebApiPayload(input: UserOnboardingAccessInput & {
    requestId: string;
    requestKey: string;
  }): Record<string, unknown> {
    return {
      mp_requestkey: input.requestKey,
      mp_requestid: input.requestId,
      mp_status: ONBOARDING_STATUS_PENDING,
      mp_requesttype: ONBOARDING_REQUEST_TYPE_CODES[input.requestType],
      mp_fullname: input.fullName,
      mp_email: input.affectedEmail,
      mp_targetrole: input.targetRole,
      mp_projectid: input.projectId,
      mp_projectname: input.projectName,
      mp_formscopejson: JSON.stringify(input.forms.map((form) => ({
        formId: form.formId,
        formName: form.formName,
        formVersionId: form.formVersionId,
      }))),
      mp_reason: input.reason,
      mp_actoremail: this.getSignedInUserEmail() || this.getSignedInUserLabel(),
      mp_actorrolesjson: JSON.stringify(this.getCurrentUserAccessAuthorization().detectedRoles),
      mp_sourceroute: input.sourceRoute,
      mp_replacementofrequestid: input.replacementOfRequestId,
      mp_processingattempts: 0,
      mp_resultmessage: 'Queued for server-side onboarding processing.',
    };
  }

  private toUserOnboardingAccessResult(queueRecordId: string, row: OnboardingRequestRow): UserOnboardingAccessResult {
    const requestType = ONBOARDING_REQUEST_TYPE_LABELS[row.mp_requesttype ?? ONBOARDING_REQUEST_TYPE_CODES.Unresolved] ?? 'Unresolved';
    const invitationDeliveryMode = row.mp_invitationdeliverymode === undefined ? undefined : INVITATION_DELIVERY_MODE_LABELS[row.mp_invitationdeliverymode];
    const invitationStatus = row.mp_invitationstatus === undefined ? undefined : INVITATION_STATUS_LABELS[row.mp_invitationstatus];
    const emailDelivery: UserOnboardingAccessResult['emailDelivery'] = invitationDeliveryMode === 'ManualCode'
      ? 'manual-code-required'
      : invitationDeliveryMode === 'Email'
        ? 'email-sent'
        : requestType === 'NewUser'
          ? 'queued-for-invitation'
          : 'queued-for-assignment-notification';
    return {
      status: 'queued',
      requestId: row.mp_requestid ?? queueRecordId,
      requestKey: row.mp_requestkey ?? queueRecordId,
      queueRecordId,
      queueStatus: ONBOARDING_STATUS_LABELS[row.mp_status ?? ONBOARDING_STATUS_PENDING] ?? 'Pending',
      requestType,
      contactId: row.mp_contactid,
      contactCreated: false,
      emailDelivery,
      emailMessage: row.mp_resultmessage || 'Onboarding request status was refreshed from Dataverse.',
      invitationId: row.mp_invitationid,
      invitationCode: row.mp_invitationcode,
      invitationRedeemUrl: row.mp_invitationredeemurl,
      invitationExpiresAt: row.mp_invitationexpiresat,
      invitationStatus,
      invitationDeliveryMode,
      replacementOfRequestId: row.mp_replacementofrequestid,
      assignmentResults: [],
    };
  }

  private async findNotificationDeliverySettingId(): Promise<string | undefined> {
    const rows = await this.get<DataverseCollection<NotificationDeliverySettingRow>>(
      `${NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH}?$select=mp_notificationdeliverysettingid&$filter=mp_settingkey eq '${NOTIFICATION_DELIVERY_SETTING_KEY}'&$top=1`,
    );
    return rows.value[0]?.mp_notificationdeliverysettingid;
  }

  private getDefaultNotificationDeliverySetting(): NotificationDeliverySetting {
    return {
      settingKey: NOTIFICATION_DELIVERY_SETTING_KEY,
      deliveryMode: 'manual-code',
      mailboxStatus: 'not-configured',
      lastTestResult: 'Mailbox delivery is not configured. Administrators can issue invitation code and redeem link through an approved internal channel.',
      instructions: 'Use manual invitation code until an approved mailbox is tested and enabled.',
      source: 'default',
    };
  }

  private toNotificationDeliverySetting(row: NotificationDeliverySettingRow): NotificationDeliverySetting {
    return {
      id: row.mp_notificationdeliverysettingid,
      settingKey: row.mp_settingkey || NOTIFICATION_DELIVERY_SETTING_KEY,
      deliveryMode: NOTIFICATION_DELIVERY_MODE_LABELS[row.mp_deliverymode ?? NOTIFICATION_DELIVERY_MODE_CODES['manual-code']] ?? 'manual-code',
      senderMailbox: row.mp_sendermailbox,
      mailboxStatus: MAILBOX_STATUS_LABELS[row.mp_mailboxstatus ?? MAILBOX_STATUS_CODES['not-configured']] ?? 'not-configured',
      nativeInvitationWorkflowId: row.mp_nativeinvitationworkflowid,
      lastTestedAt: row.mp_lasttestedat,
      lastTestResult: row.mp_lasttestresult,
      instructions: row.mp_instructions,
      updatedByEmail: row.mp_updatedbyemail,
      updatedAt: row.mp_updatedat,
      source: 'dataverse',
    };
  }

  private toNotificationDeliverySettingWebApiPayload(input: NotificationDeliverySettingInput): Record<string, unknown> {
    return {
      mp_settingkey: NOTIFICATION_DELIVERY_SETTING_KEY,
      mp_deliverymode: NOTIFICATION_DELIVERY_MODE_CODES[input.deliveryMode],
      mp_sendermailbox: input.senderMailbox?.trim() || null,
      mp_mailboxstatus: MAILBOX_STATUS_CODES[input.mailboxStatus],
      mp_nativeinvitationworkflowid: input.nativeInvitationWorkflowId?.trim() || null,
      mp_lasttestedat: input.lastTestedAt || null,
      mp_lasttestresult: input.lastTestResult?.trim() || null,
      mp_instructions: input.instructions?.trim() || null,
      mp_updatedbyemail: this.getSignedInUserEmail() || this.getSignedInUserLabel(),
      mp_updatedat: new Date().toISOString(),
    };
  }

  private async resolveFormVersionXForm(formVersionId: string, markerOrXml: string): Promise<string> {
    if (!markerOrXml.startsWith(XFORM_FILE_MARKER_PREFIX)) {
      return markerOrXml;
    }

    const fileName = markerOrXml.slice(XFORM_FILE_MARKER_PREFIX.length);
    if (!fileName) {
      throw new Error(`Form version ${formVersionId} references an empty XForm file marker.`);
    }

    const attachments = await measureAsync('api:getXFormAttachment', () => this.get<DataverseCollection<FormAttachmentRow>>(
      `/_api/mp_formattachments?$select=mp_formattachmentid,mp_filename,mp_mediatype,_mp_formversion_value&$filter=_mp_formversion_value eq ${encodeURIComponent(formVersionId)} and mp_filename eq '${this.escapeODataString(fileName)}'&$top=1`,
    ));
    const attachment = attachments.value[0];
    if (!attachment) {
      throw new Error(`Form version ${formVersionId} references missing XForm file ${fileName}.`);
    }

    return measureAsync('api:downloadXFormXml', async () => {
      const response = await this.send(
        `/_api/mp_formattachments(${encodeURIComponent(attachment.mp_formattachmentid)})/mp_file/$value`,
        {
          method: 'GET',
          headers: {
            Accept: attachment.mp_mediatype || 'application/xml',
          },
        },
      );
      return response.text();
    });
  }

  private buildXFormCacheKey(formVersionId: string, version: string, markerOrXml: string): string {
    return `${XFORM_CACHE_PREFIX}:${formVersionId}:${version}:${this.hashString(markerOrXml)}`;
  }

  private async getCachedXForm(cacheKey: string): Promise<string | null> {
    try {
      return await xformCache.get(cacheKey);
    } catch {
      return null;
    }
  }

  private async setCachedXForm(cacheKey: string, xformXml: string): Promise<void> {
    try {
      await xformCache.set(cacheKey, xformXml);
    } catch {
      // Cache is an optimization only; form loading must still work if storage is full or disabled.
    }
  }

  private hashString(value: string): string {
    let hash = 0;
    for (let index = 0; index < value.length; index += 1) {
      hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0;
    }
    return Math.abs(hash).toString(36);
  }

  private async get<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'GET' });
  }

  private buildReportingFetchXml(page: number, pageSize: number, filters: ReportingFilters, accessScope: ReportingAccessScope): string {
    const attributes = [
      'mp_submissionreportrowid',
      'mp_reportkey',
      'mp_instanceid',
      'mp_displayname',
      'mp_useremail',
      'mp_submittedat',
      'mp_updatedat',
      'mp_versionnumber',
      'mp_lifecyclestatus',
      'mp_reviewstate',
      'mp_projectionstatus',
      'mp_projectedat',
      'mp_projectionerror',
      'mp_rootanswersjson',
      'mp_formversion',
    ].map((name) => `<attribute name="${name}" />`).join('');
    const conditions: string[] = [];
    const search = filters.search?.trim();
    if (search) {
      const value = this.escapeFetchXmlAttribute(`%${search}%`);
      conditions.push(
        `<filter type="or"><condition attribute="mp_displayname" operator="like" value="${value}" />`
        + `<condition attribute="mp_instanceid" operator="like" value="${value}" />`
        + `<condition attribute="mp_useremail" operator="like" value="${value}" /></filter>`,
      );
    }
    if (filters.dateFrom) {
      conditions.push(`<condition attribute="mp_updatedat" operator="on-or-after" value="${this.escapeFetchXmlAttribute(filters.dateFrom)}" />`);
    }
    if (filters.dateTo) {
      conditions.push(`<condition attribute="mp_updatedat" operator="on-or-before" value="${this.escapeFetchXmlAttribute(filters.dateTo)}" />`);
    }
    if (accessScope.mode === 'own-records') {
      conditions.push(`<condition attribute="mp_useremail" operator="eq" value="${this.escapeFetchXmlAttribute(accessScope.ownerEmail ?? '')}" />`);
    } else if (filters.submitter?.trim()) {
      conditions.push(`<condition attribute="mp_useremail" operator="eq" value="${this.escapeFetchXmlAttribute(filters.submitter.trim())}" />`);
    }
    if (filters.reviewState !== undefined) {
      conditions.push(`<condition attribute="mp_reviewstate" operator="eq" value="${filters.reviewState}" />`);
    }
    if (filters.formVersionId) {
      conditions.push(`<condition attribute="mp_formversion" operator="eq" value="${this.escapeFetchXmlAttribute(filters.formVersionId)}" />`);
    }
    const filter = conditions.length > 0 ? `<filter type="and">${conditions.join('')}</filter>` : '';
    return `<fetch count="${pageSize}" page="${page}" returntotalrecordcount="true">`
      + `<entity name="mp_submissionreportrow">${attributes}`
      + '<order attribute="mp_updatedat" descending="true" />'
      + '<order attribute="mp_submissionreportrowid" descending="false" />'
      + `${filter}</entity></fetch>`;
  }

  private buildAssignedFormsFetchXml(userEmail: string, count: number): string {
    const email = this.escapeFetchXmlAttribute(userEmail);
    return `<fetch count="${count}">`
      + '<entity name="mp_formassignment">'
      + '<attribute name="mp_formassignmentid" />'
      + '<attribute name="mp_assignmentkey" />'
      + '<attribute name="mp_useremail" />'
      + '<attribute name="mp_lifecyclestatus" />'
      + '<attribute name="mp_formversion" />'
      + `<filter type="and"><condition attribute="mp_useremail" operator="eq" value="${email}" /><condition attribute="mp_lifecyclestatus" operator="eq" value="${FORM_ASSIGNMENT_LIFECYCLE_ACTIVE}" /></filter>`
      + '<link-entity name="mp_formversion" from="mp_formversionid" to="mp_formversion" alias="fv" link-type="inner">'
      + '<attribute name="mp_version" />'
      + '<attribute name="mp_webformsenabled" />'
      + '<attribute name="mp_form" />'
      + '<link-entity name="mp_form" from="mp_formid" to="mp_form" alias="form" link-type="inner">'
      + '<attribute name="mp_name" />'
      + '<attribute name="mp_xmlformid" />'
      + '</link-entity>'
      + '</link-entity>'
      + '</entity></fetch>';
  }

  private getAliasedString(row: object, ...keys: string[]): string {
    const values = row as Record<string, unknown>;
    for (const key of keys) {
      const value = values[key];
      if (typeof value === 'string' && value.trim()) {
        return value;
      }
      if (value && typeof value === 'object' && 'value' in value) {
        const nested = (value as { value?: unknown }).value;
        if (typeof nested === 'string' && nested.trim()) {
          return nested;
        }
      }
    }
    return '';
  }

  private escapeFetchXmlAttribute(value: string): string {
    return value
      .replaceAll('&', '&amp;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&apos;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
  }

  private slugify(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'export';
  }

  private buildAccessRequestId(action: string, affectedEmail: string, occurredAt: string): string {
    const randomId = window.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
    return `access:${occurredAt}:${action}:${this.slugify(affectedEmail)}:${randomId}`;
  }

  private buildOnboardingRequestId(affectedEmail: string, occurredAt: string): string {
    const timestamp = occurredAt.replace(/[-:.TZ]/g, '').slice(0, 14);
    return `ONB-${timestamp}-${this.slugify(affectedEmail)}`;
  }

  private buildOnboardingRequestKey(affectedEmail: string, requestId: string): string {
    return `onboarding:${this.slugify(affectedEmail)}:${requestId}`;
  }

  private buildFormAssignmentKey(affectedEmail: string, formVersionId: string): string {
    return `${affectedEmail}:${formVersionId}`;
  }

  private buildAccessMutationPayload(command: AccessWriteCommand, affectedEmail: string): Record<string, unknown> | null {
    if (command.action === 'AssignForm') {
      return {
        mp_useremail: affectedEmail,
        mp_assignmentkey: command.formVersionId ? this.buildFormAssignmentKey(affectedEmail, command.formVersionId) : undefined,
        mp_lifecyclestatus: FORM_ASSIGNMENT_LIFECYCLE_ACTIVE,
        'mp_FormVersion@odata.bind': command.formVersionId ? `/mp_formversions(${command.formVersionId})` : undefined,
      };
    }

    if (command.action === 'ChangeRole') {
      return {
        role: command.targetRole,
        affectedEmail,
        scopeType: command.scopeType,
      };
    }

    if (command.action === 'CorrectEmail') {
      return {
        affectedEmail,
        correctedEmail: command.newState?.userEmail,
        assignments: command.formAssignmentId,
      };
    }

    if (command.action === 'SuspendAccess' || command.action === 'ReactivateAccess' || command.action === 'RemoveAssignment') {
      return {
        affectedEmail,
        status: command.newState?.status,
        assignmentId: command.formAssignmentId,
      };
    }

    return null;
  }

  private async findFormAssignmentByEmailAndVersion(affectedEmail: string, formVersionId: string): Promise<FormAssignmentRow | null> {
    const result = await this.get<DataverseCollection<FormAssignmentRow>>(
      `/_api/mp_formassignments?$select=mp_formassignmentid,mp_assignmentkey,mp_useremail,mp_lifecyclestatus,_mp_formversion_value&$filter=mp_useremail eq '${this.escapeODataString(affectedEmail)}' and _mp_formversion_value eq ${encodeURIComponent(formVersionId)}&$top=1`,
    );
    return result.value[0] ?? null;
  }

  private async assertEmailCorrectionTargetIsAvailable(assignments: FormAssignmentSummary[], newEmail: string): Promise<void> {
    for (const assignment of assignments) {
      const result = await this.get<DataverseCollection<FormAssignmentRow>>(
        `/_api/mp_formassignments?$select=mp_formassignmentid,mp_assignmentkey,mp_useremail,_mp_formversion_value&$filter=mp_useremail eq '${this.escapeODataString(newEmail)}' and _mp_formversion_value eq ${encodeURIComponent(assignment.formVersionId)} and mp_lifecyclestatus eq ${FORM_ASSIGNMENT_LIFECYCLE_ACTIVE}&$top=1`,
      );
      const conflict = result.value.find((row) => row.mp_formassignmentid !== assignment.assignmentId);
      if (conflict) {
        throw new Error(`Cannot correct this email to ${newEmail} because that user already has active access to ${assignment.formName}. Remove the duplicate access row first, then retry if needed.`);
      }
    }
  }

  private async createAccessAuditRequested(preview: AccessWritePreview): Promise<string> {
    return this.createRecord(ACCESS_AUDIT_WEB_API_PATH, this.toAccessAuditWebApiPayload(preview.auditPayload));
  }

  private async updateAccessAuditResult(auditId: string, resultStatus: 'Succeeded' | 'Failed', resultMessage: string): Promise<void> {
    if (!ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED) {
      return;
    }

    await this.send(`${ACCESS_AUDIT_WEB_API_PATH}(${encodeURIComponent(auditId)})`, {
      method: 'PATCH',
      body: {
        mp_resultstatus: ACCESS_AUDIT_RESULT_STATUS_CODES[resultStatus],
        mp_resultmessage: resultMessage.slice(0, 1900),
      },
    });
  }

  private async createAssignFormAssignment(preview: AccessWritePreview): Promise<string> {
    if (!preview.mutationPayload) {
      throw new Error('AssignForm preview did not include an assignment mutation payload.');
    }

    return this.createRecord('/_api/mp_formassignments', preview.mutationPayload);
  }

  private async updateContactEmail(contactId: string, email: string): Promise<void> {
    await this.send(`/_api/contacts(${encodeURIComponent(contactId)})`, {
      method: 'PATCH',
      body: {
        emailaddress1: email,
      },
    });
  }

  private async updateFormAssignmentEmail(assignment: FormAssignmentSummary, email: string): Promise<void> {
    await this.send(`/_api/mp_formassignments(${encodeURIComponent(assignment.assignmentId)})`, {
      method: 'PATCH',
      body: {
        mp_useremail: email,
        mp_assignmentkey: this.buildFormAssignmentKey(email, assignment.formVersionId),
      },
    });
  }

  private async reactivateFormAssignment(assignmentId: string, email: string, formVersionId: string): Promise<void> {
    await this.send(`/_api/mp_formassignments(${encodeURIComponent(assignmentId)})`, {
      method: 'PATCH',
      body: {
        mp_useremail: email,
        mp_assignmentkey: this.buildFormAssignmentKey(email, formVersionId),
        mp_lifecyclestatus: FORM_ASSIGNMENT_LIFECYCLE_ACTIVE,
      },
    });
  }

  private async deactivateFormAssignment(assignmentId: string): Promise<void> {
    await this.send(`/_api/mp_formassignments(${encodeURIComponent(assignmentId)})`, {
      method: 'PATCH',
      body: {
        mp_lifecyclestatus: FORM_ASSIGNMENT_LIFECYCLE_INACTIVE,
      },
    });
  }

  private toAccessAuditWebApiPayload(payload: AccessAuditPreviewPayload): Record<string, unknown> {
    return {
      mp_auditkey: payload.AuditKey,
      mp_action: ACCESS_AUDIT_ACTION_CODES[payload.Action],
      mp_resultstatus: ACCESS_AUDIT_RESULT_STATUS_CODES[payload.ResultStatus],
      mp_actoremail: payload.ActorEmail,
      mp_actorrolesjson: payload.ActorRolesJson,
      mp_affectedemail: payload.AffectedEmail,
      mp_targetrole: payload.TargetRole,
      mp_scopetype: ACCESS_AUDIT_SCOPE_TYPE_CODES[payload.ScopeType],
      mp_previousstatejson: payload.PreviousStateJson,
      mp_newstatejson: payload.NewStateJson,
      mp_reason: payload.Reason,
      mp_sourceroute: payload.SourceRoute,
      mp_requestid: payload.RequestId,
      mp_occurredat: payload.OccurredAt,
      mp_resultmessage: payload.ResultMessage,
    };
  }

  private async createSubmission(assignment: FormAssignmentSummary, instanceId: string, now: string): Promise<string> {
    return this.createRecord('/_api/mp_submissions', {
      mp_instanceid: instanceId,
      mp_useremail: assignment.userEmail,
      mp_lifecyclestatus: SUBMISSION_LIFECYCLE_SUBMITTED,
      mp_reviewstate: SUBMISSION_REVIEW_RECEIVED,
      mp_submittedat: now,
      mp_updatedat: now,
    });
  }

  private async createSubmissionVersion(input: {
    assignment: FormAssignmentSummary;
    instanceId: string;
    now: string;
    payload: unknown;
    submissionId: string;
    versionNumber: number;
    xml: string;
  }): Promise<string> {
    const versionKey = `${input.instanceId}:${input.versionNumber}`;
    return this.createRecord('/_api/mp_submissionversions', {
      mp_versionkey: versionKey,
      mp_versionnumber: input.versionNumber,
      mp_instanceid: input.instanceId,
      mp_xformsubmissionxml: input.xml,
      mp_submissionjson: JSON.stringify(this.summarizePayload(input.payload, input.assignment, input.xml)),
      mp_current: true,
      mp_useragent: window.navigator.userAgent.slice(0, 850),
      mp_deviceid: 'tacatdp-powerpages-poc',
      mp_createdat: input.now,
      'mp_Submission@odata.bind': `/mp_submissions(${input.submissionId})`,
    });
  }

  private async createSubmissionAttachments(submissionVersionId: string, attachments: AttachmentPayload[], now: string): Promise<AttachmentPersistResult[]> {
    const results: AttachmentPersistResult[] = [];
    for (const attachment of attachments) {
      const attachmentId = await this.createRecord('/_api/mp_submissionattachments', {
        mp_filename: attachment.fileName,
        mp_mediatype: attachment.mediaType,
        mp_uploadedat: now,
        'mp_SubmissionVersion@odata.bind': `/mp_submissionversions(${submissionVersionId})`,
      });

      const result: AttachmentPersistResult = {
        attachmentId,
        binaryUploaded: false,
      };

      try {
        await this.uploadAttachmentFile(attachmentId, attachment);
        result.binaryUploaded = true;
      } catch (caught) {
        const detail = caught instanceof Error ? caught.message : 'unknown error';
        result.warning = `${attachment.fileName}: metadata saved, binary upload not confirmed (${detail})`;
      }

      results.push(result);
    }

    return results;
  }

  private async findSubmissionByInstanceId(instanceId: string): Promise<SubmissionRow | null> {
    const submissions = await this.get<DataverseCollection<SubmissionRow>>(
      `/_api/mp_submissions?$select=mp_submissionid,mp_instanceid&$filter=mp_instanceid eq '${this.escapeODataString(instanceId)}'&$top=1`,
    );

    return submissions.value[0] ?? null;
  }

  private async requireProjectId(projectCode: string): Promise<string> {
    const result = await this.get<DataverseCollection<{ mp_projectid: string }>>(
      `/_api/mp_projects?$select=mp_projectid,mp_projectcode&$filter=mp_projectcode eq '${this.escapeODataString(projectCode)}'&$top=1`,
    );
    const projectId = result.value[0]?.mp_projectid;
    if (!projectId) {
      throw new Error(`Project ${projectCode} was not found in Dataverse.`);
    }
    return projectId;
  }

  private async requireFormVersionId(version: string): Promise<string> {
    const result = await this.get<DataverseCollection<{ mp_formversionid: string }>>(
      `/_api/mp_formversions?$select=mp_formversionid,mp_version&$filter=mp_version eq '${this.escapeODataString(version)}'&$top=1`,
    );
    const formVersionId = result.value[0]?.mp_formversionid;
    if (!formVersionId) {
      throw new Error(`Form version ${version} was not found in Dataverse. Seed the latest XLSForm version before importing baseline rows.`);
    }
    return formVersionId;
  }

  private async upsertSubmissionForBaseline(row: BaselineBridgeImportAsset['rows'][number], formVersionId: string, now: string): Promise<string> {
    const existing = await this.findSubmissionByInstanceId(row.instanceId);
    const payload: Record<string, unknown> = {
      mp_instanceid: row.instanceId,
      mp_lifecyclestatus: SUBMISSION_LIFECYCLE_SUBMITTED,
      mp_reviewstate: SUBMISSION_REVIEW_RECEIVED,
      mp_startedat: row.startedAt || undefined,
      mp_submittedat: row.submittedAt || now,
      mp_updatedat: now,
      'mp_FormVersion@odata.bind': `/mp_formversions(${formVersionId})`,
    };
    if (existing?.mp_submissionid) {
      await this.send(`/_api/mp_submissions(${encodeURIComponent(existing.mp_submissionid)})`, { method: 'PATCH', body: this.omitUndefined(payload) });
      return existing.mp_submissionid;
    }
    return this.createRecord('/_api/mp_submissions', this.omitUndefined(payload));
  }

  private async upsertSubmissionVersionForBaseline(
    row: BaselineBridgeImportAsset['rows'][number],
    submissionId: string,
    now: string,
    mode: BaselineBridgeImportOptions['mode'],
  ): Promise<{ submissionVersionId: string; versionNumber: number }> {
    const existing = await this.findOne<{ mp_submissionversionid: string }>(
      '/_api/mp_submissionversions',
      'mp_submissionversionid,mp_versionkey',
      `mp_versionkey eq '${this.escapeODataString(row.versionKey)}'`,
    );
    const shouldAppendVersion = mode === 'append' && !!existing?.mp_submissionversionid;
    const versionNumber = shouldAppendVersion ? await this.nextSubmissionVersionNumber(row.instanceId) : 1;
    const payload = {
      mp_versionkey: shouldAppendVersion ? `${row.versionKey}:append:${Date.parse(now)}:${row.rowNumber}` : row.versionKey,
      mp_instanceid: row.instanceId,
      mp_versionnumber: versionNumber,
      mp_current: true,
      mp_createdat: now,
      mp_xformsubmissionxml: row.xformXml,
      mp_submissionjson: row.submissionJson,
      'mp_Submission@odata.bind': `/mp_submissions(${submissionId})`,
    };
    if (existing?.mp_submissionversionid && !shouldAppendVersion) {
      await this.send(`/_api/mp_submissionversions(${encodeURIComponent(existing.mp_submissionversionid)})`, { method: 'PATCH', body: payload });
      return { submissionVersionId: existing.mp_submissionversionid, versionNumber };
    }
    if (existing?.mp_submissionversionid && shouldAppendVersion) {
      await this.send(`/_api/mp_submissionversions(${encodeURIComponent(existing.mp_submissionversionid)})`, { method: 'PATCH', body: { mp_current: false } });
    }
    return { submissionVersionId: await this.createRecord('/_api/mp_submissionversions', payload), versionNumber };
  }

  private async upsertTrackedEntityForBaseline(row: BaselineBridgeImportAsset['rows'][number], _projectId: string): Promise<string> {
    let existing: { mp_trackedentityid: string } | null = null;
    let lookupFailure: string | null = null;
    try {
      existing = await this.findOneByFetchXml<{ mp_trackedentityid: string }>(
        '/_api/mp_trackedentitys',
        'mp_trackedentity',
        ['mp_trackedentityid', 'mp_entitykey'],
        [
          ['mp_entitytype', 'eq', TRACKED_ENTITY_TYPE_BENEFICIARY],
          ['mp_entitykey', 'eq', row.sourceKey],
        ],
      );
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'Unknown lookup error.';
      lookupFailure = this.sanitizeBaselineImportDiagnostic(message);
    }

    const payload = {
      mp_entitytype: TRACKED_ENTITY_TYPE_BENEFICIARY,
      mp_entitykey: row.sourceKey,
      mp_displayname: row.customerName || `Beneficiary ${row.rowNumber}`,
      mp_status: TRACKED_ENTITY_STATUS_ACTIVE,
    };
    try {
      if (existing?.mp_trackedentityid) {
        await this.send(`/_api/mp_trackedentitys(${encodeURIComponent(existing.mp_trackedentityid)})`, { method: 'PATCH', body: payload });
        return existing.mp_trackedentityid;
      }
      return await this.createRecord('/_api/mp_trackedentitys', payload);
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'Unknown write error.';
      if (lookupFailure) {
        throw new Error(`mp_TrackedEntity lookup and create failed. Lookup: ${lookupFailure}. Create: ${this.sanitizeBaselineImportDiagnostic(message)}`);
      }
      throw new Error(`mp_TrackedEntity write failed: ${this.sanitizeBaselineImportDiagnostic(message)}`);
    }
  }

  private async upsertIdentifiersForBaseline(row: BaselineBridgeImportAsset['rows'][number], trackedEntityId: string): Promise<number> {
    const identifiers: Array<[number, string | undefined]> = [
      [IDENTIFIER_SOURCE_RECORD, row.uuid],
      [IDENTIFIER_CUSTOMER_ID, row.customerId],
      [IDENTIFIER_PHONE, row.phone],
    ];
    let count = 0;
    for (const [identifierType, identifierValue] of identifiers) {
      if (!identifierValue) {
        continue;
      }
      const existing = await this.findOne<{ mp_entityidentifierid: string }>(
        '/_api/mp_entityidentifiers',
        'mp_entityidentifierid,mp_identifiertype',
        `_mp_trackedentity_value eq ${trackedEntityId} and mp_identifiertype eq ${identifierType} and mp_identifiervalue eq '${this.escapeODataString(identifierValue)}'`,
      );
      const payload = {
        mp_identifiertype: identifierType,
        mp_identifiervalue: identifierValue,
        mp_status: IDENTIFIER_STATUS_ACTIVE,
        'mp_TrackedEntity@odata.bind': `/mp_trackedentitys(${trackedEntityId})`,
      };
      if (existing?.mp_entityidentifierid) {
        await this.send(`/_api/mp_entityidentifiers(${encodeURIComponent(existing.mp_entityidentifierid)})`, { method: 'PATCH', body: payload });
      } else {
        await this.createRecord('/_api/mp_entityidentifiers', payload);
      }
      count += 1;
    }
    return count;
  }

  private async upsertBeneficiaryProfileForBaseline(row: BaselineBridgeImportAsset['rows'][number], trackedEntityId: string, _projectId: string, now: string): Promise<string> {
    const existing = await this.findOne<{ mp_beneficiaryprofileid: string }>(
      '/_api/mp_beneficiaryprofiles',
      'mp_beneficiaryprofileid',
      `_mp_trackedentity_value eq ${trackedEntityId}`,
    );
    const payload = this.omitUndefined({
      mp_name: row.customerName || `Beneficiary ${row.rowNumber}`,
      mp_beneficiarycategory: BENEFICIARY_CATEGORY_INDIVIDUAL_FARMER,
      mp_region: row.region || undefined,
      mp_district: row.district || undefined,
      mp_verificationstatus: BENEFICIARY_VERIFICATION_UNDER_REVIEW,
      mp_datasource: 'Kobo baseline import',
      mp_lastupdatedat: now,
      'mp_TrackedEntity@odata.bind': `/mp_trackedentitys(${trackedEntityId})`,
    });
    if (existing?.mp_beneficiaryprofileid) {
      await this.send(`/_api/mp_beneficiaryprofiles(${encodeURIComponent(existing.mp_beneficiaryprofileid)})`, { method: 'PATCH', body: payload });
      return existing.mp_beneficiaryprofileid;
    }
    return this.createRecord('/_api/mp_beneficiaryprofiles', payload);
  }

  private async upsertBeneficiarySubmissionLinkForBaseline(row: BaselineBridgeImportAsset['rows'][number], trackedEntityId: string, submissionId: string): Promise<string> {
    const existing = await this.findOne<{ mp_beneficiarysubmissionlinkid: string }>(
      '/_api/mp_beneficiarysubmissionlinks',
      'mp_beneficiarysubmissionlinkid,mp_linkkey',
      `mp_linkkey eq '${this.escapeODataString(row.linkKey)}'`,
    );
    const payload = {
      mp_linkkey: row.linkKey,
      mp_relationshiptype: SUBMISSION_LINK_RELATIONSHIP_BASELINE,
      mp_completeness: 100,
      mp_reviewstatus: SUBMISSION_LINK_REVIEW_UNDER_REVIEW,
      'mp_TrackedEntity@odata.bind': `/mp_trackedentitys(${trackedEntityId})`,
      'mp_Submission@odata.bind': `/mp_submissions(${submissionId})`,
    };
    if (existing?.mp_beneficiarysubmissionlinkid) {
      await this.send(`/_api/mp_beneficiarysubmissionlinks(${encodeURIComponent(existing.mp_beneficiarysubmissionlinkid)})`, { method: 'PATCH', body: payload });
      return existing.mp_beneficiarysubmissionlinkid;
    }
    return this.createRecord('/_api/mp_beneficiarysubmissionlinks', payload);
  }

  private async upsertCanonicalReportRow(submission: SubmissionRow, version: SubmissionVersionRow, formVersionId: string, now: string): Promise<string> {
    const metadata = this.parseBaselineSubmissionJson(version.mp_submissionjson ?? '');
    const instanceId = submission.mp_instanceid || version.mp_instanceid;
    if (!instanceId) {
      throw new Error(`Cannot project submission ${submission.mp_submissionid}: missing instance id.`);
    }
    const reportKey = `${this.sanitizeProjectionKeyPart(formVersionId)}:${this.sanitizeProjectionKeyPart(instanceId)}`;
    const existing = await this.findOne<{ mp_submissionreportrowid: string }>(
      '/_api/mp_submissionreportrows',
      'mp_submissionreportrowid,mp_reportkey',
      `mp_reportkey eq '${this.escapeODataString(reportKey)}'`,
    );
    const payload = this.omitUndefined({
      mp_reportkey: reportKey,
      mp_instanceid: instanceId,
      mp_displayname: metadata.instanceName || instanceId,
      mp_useremail: submission.mp_useremail || this.getSignedInUserEmail() || undefined,
      mp_submittedat: submission.mp_submittedat || now,
      mp_updatedat: submission.mp_updatedat || now,
      mp_versionnumber: version.mp_versionnumber || 1,
      mp_lifecyclestatus: submission.mp_lifecyclestatus ?? SUBMISSION_LIFECYCLE_SUBMITTED,
      mp_reviewstate: submission.mp_reviewstate ?? SUBMISSION_REVIEW_RECEIVED,
      mp_projectionstatus: PROJECTION_READY,
      mp_projectedat: now,
      mp_projectionerror: undefined,
      mp_rootanswersjson: this.buildBaselineRootAnswersJson(version.mp_submissionjson ?? ''),
      'mp_Submission@odata.bind': `/mp_submissions(${submission.mp_submissionid})`,
      'mp_SubmissionVersion@odata.bind': `/mp_submissionversions(${version.mp_submissionversionid})`,
      'mp_FormVersion@odata.bind': `/mp_formversions(${formVersionId})`,
    });
    if (existing?.mp_submissionreportrowid) {
      await this.send(`/_api/mp_submissionreportrows(${encodeURIComponent(existing.mp_submissionreportrowid)})`, { method: 'PATCH', body: payload });
      return existing.mp_submissionreportrowid;
    }
    return this.createRecord('/_api/mp_submissionreportrows', payload);
  }

  private async upsertBaselineReportRow(
    row: BaselineBridgeImportAsset['rows'][number],
    submissionId: string,
    submissionVersionId: string,
    versionNumber: number,
    formVersionId: string,
    now: string,
  ): Promise<string> {
    const reportKey = `${this.sanitizeProjectionKeyPart(formVersionId)}:${this.sanitizeProjectionKeyPart(row.instanceId)}`;
    const existing = await this.findOne<{ mp_submissionreportrowid: string }>(
      '/_api/mp_submissionreportrows',
      'mp_submissionreportrowid,mp_reportkey',
      `mp_reportkey eq '${this.escapeODataString(reportKey)}'`,
    );
    const metadata = this.parseBaselineSubmissionJson(row.submissionJson);
    const payload = this.omitUndefined({
      mp_reportkey: reportKey,
      mp_instanceid: row.instanceId,
      mp_displayname: metadata.instanceName || row.customerName || `Beneficiary ${row.rowNumber}`,
      mp_useremail: this.getSignedInUserEmail() || undefined,
      mp_submittedat: row.submittedAt || now,
      mp_updatedat: now,
      mp_versionnumber: versionNumber,
      mp_lifecyclestatus: SUBMISSION_LIFECYCLE_SUBMITTED,
      mp_reviewstate: SUBMISSION_REVIEW_RECEIVED,
      mp_projectionstatus: PROJECTION_READY,
      mp_projectedat: now,
      mp_projectionerror: undefined,
      mp_rootanswersjson: this.buildBaselineRootAnswersJson(row.submissionJson),
      'mp_Submission@odata.bind': `/mp_submissions(${submissionId})`,
      'mp_SubmissionVersion@odata.bind': `/mp_submissionversions(${submissionVersionId})`,
      'mp_FormVersion@odata.bind': `/mp_formversions(${formVersionId})`,
    });
    if (existing?.mp_submissionreportrowid) {
      await this.send(`/_api/mp_submissionreportrows(${encodeURIComponent(existing.mp_submissionreportrowid)})`, { method: 'PATCH', body: payload });
      return existing.mp_submissionreportrowid;
    }
    return this.createRecord('/_api/mp_submissionreportrows', payload);
  }

  private async findOne<T>(entitySetPath: string, select: string, filter: string): Promise<T | null> {
    const result = await this.get<DataverseCollection<T>>(
      `${entitySetPath}?$select=${encodeURIComponent(select)}&$filter=${encodeURIComponent(filter)}&$top=1`,
    );
    return result.value[0] ?? null;
  }

  private async findOneByFetchXml<T>(
    entitySetPath: string,
    entityLogicalName: string,
    attributes: string[],
    conditions: Array<[string, string, string | number]>,
  ): Promise<T | null> {
    const attributeXml = attributes.map((attribute) => `<attribute name="${this.escapeXmlAttribute(attribute)}" />`).join('');
    const conditionXml = conditions
      .map(([attribute, operator, value]) => (
        `<condition attribute="${this.escapeXmlAttribute(attribute)}" operator="${this.escapeXmlAttribute(operator)}" value="${this.escapeXmlAttribute(String(value))}" />`
      ))
      .join('');
    const fetchXml = `<fetch top="1"><entity name="${this.escapeXmlAttribute(entityLogicalName)}">${attributeXml}<filter>${conditionXml}</filter></entity></fetch>`;
    const result = await this.get<DataverseCollection<T>>(
      `${entitySetPath}?fetchXml=${encodeURIComponent(fetchXml)}`,
    );
    return result.value[0] ?? null;
  }

  private escapeXmlAttribute(value: string): string {
    return value
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  private bumpImportCount(result: BaselineBridgeImportResult, key: string): void {
    result.counts[key] = (result.counts[key] ?? 0) + 1;
  }

  private async runBaselineImportStep<T>(rowNumber: number, step: string, action: () => Promise<T>): Promise<T> {
    try {
      return await action();
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'Unknown Dataverse Web API error.';
      throw new Error(`Baseline import failed at row ${rowNumber} during ${step}: ${this.sanitizeBaselineImportDiagnostic(message)}`);
    }
  }

  private parseBaselineSubmissionJson(value: string): { instanceName?: string; answers?: Record<string, unknown> } {
    try {
      const parsed = JSON.parse(value) as { instanceName?: unknown; answers?: unknown; rootAnswers?: unknown; data?: unknown };
      const answers = typeof parsed.answers === 'object' && parsed.answers !== null && !Array.isArray(parsed.answers)
        ? parsed.answers as Record<string, unknown>
        : typeof parsed.rootAnswers === 'object' && parsed.rootAnswers !== null && !Array.isArray(parsed.rootAnswers)
          ? parsed.rootAnswers as Record<string, unknown>
          : undefined;
      return {
        instanceName: typeof parsed.instanceName === 'string' ? parsed.instanceName : undefined,
        answers,
      };
    } catch {
      return {};
    }
  }

  private buildBaselineRootAnswersJson(value: string): string {
    const parsed = this.parseBaselineSubmissionJson(value);
    if (parsed.answers) {
      return JSON.stringify(parsed.answers);
    }
    return '{}';
  }

  private sanitizeProjectionKeyPart(value: string): string {
    const normalized = value.trim().replace(/\s+/g, '_').replace(/[^0-9A-Za-z_.:-]+/g, '_').replace(/^_+|_+$/g, '');
    return normalized || 'blank';
  }

  private sanitizeBaselineImportDiagnostic(message: string): string {
    return message
      .replace(/mp_identifiervalue eq '[^']*'/g, "mp_identifiervalue eq '<redacted>'")
      .replace(/mp_instanceid eq '[^']*'/g, "mp_instanceid eq '<redacted>'")
      .replace(/mp_entitykey eq '[^']*'/g, "mp_entitykey eq '<redacted>'")
      .replace(/mp_linkkey eq '[^']*'/g, "mp_linkkey eq '<redacted>'")
      .replace(/kobo:[0-9a-f-]{36}/gi, 'kobo:<redacted>')
      .replace(/uuid:[0-9a-f-]{36}/gi, 'uuid:<redacted>')
      .slice(0, 700);
  }

  private omitUndefined(payload: Record<string, unknown>): Record<string, unknown> {
    return Object.fromEntries(Object.entries(payload).filter(([, value]) => value !== undefined));
  }


  private groupRowsByLookup<T, K extends keyof T>(rows: T[], lookupName: K): Map<string, T[]> {
    const grouped = new Map<string, T[]>();
    for (const row of rows) {
      const key = row[lookupName];
      if (typeof key !== 'string' || !key) continue;
      const current = grouped.get(key) ?? [];
      current.push(row);
      grouped.set(key, current);
    }
    return grouped;
  }

  private mapBeneficiaryCategory(value?: number): BeneficiaryListItem['category'] {
    if (value === 100000002) return 'AMCOS';
    if (value === 100000003) return 'SACCOS';
    if (value === 100000001) return 'Farmer group';
    return 'Individual farmer';
  }

  private mapBeneficiaryVerificationStatus(value?: number): BeneficiaryListItem['verificationStatus'] {
    if (value === 100000001) return 'Verified';
    if (value === 100000002) return 'Incomplete';
    return 'Under review';
  }

  private formatDisplayDate(value: string): string {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'short', day: 'numeric' }).format(date);
  }

  private async nextSubmissionVersionNumber(instanceId: string): Promise<number> {
    const versions = await this.get<DataverseCollection<SubmissionVersionRow>>(
      `/_api/mp_submissionversions?$select=mp_submissionversionid,mp_versionnumber&$filter=mp_instanceid eq '${this.escapeODataString(instanceId)}'&$orderby=mp_versionnumber desc&$top=1`,
    );

    return (versions.value[0]?.mp_versionnumber ?? 0) + 1;
  }

  private async getLatestSubmissionVersionByInstanceId(instanceId: string): Promise<SubmissionVersionRow | null> {
    const versions = await this.get<DataverseCollection<SubmissionVersionRow>>(
      `/_api/mp_submissionversions?$select=mp_submissionversionid,mp_versionnumber,mp_instanceid,mp_xformsubmissionxml,mp_submissionjson&$filter=mp_instanceid eq '${this.escapeODataString(instanceId)}'&$orderby=mp_versionnumber desc&$top=1`,
    );

    return versions.value[0] ?? null;
  }

  private async createRecord(url: string, body: unknown): Promise<string> {
    const response = await this.send(url, { method: 'POST', body });
    const entityId = response.headers.get('entityid') ?? response.headers.get('OData-EntityId');
    const id = entityId?.match(/\(([^)]+)\)$/)?.[1] ?? entityId;
    if (!id) {
      throw new Error(`Power Pages Web API create did not return an entity id for ${url}.`);
    }
    return id;
  }

  private async updateSubmission(submissionId: string, updatedAt: string): Promise<void> {
    await this.send(`/_api/mp_submissions(${submissionId})`, {
      method: 'PATCH',
      body: {
        mp_updatedat: updatedAt,
        mp_lifecyclestatus: SUBMISSION_LIFECYCLE_SUBMITTED,
        mp_reviewstate: SUBMISSION_REVIEW_RECEIVED,
      },
    });
  }

  private async request<T>(url: string, options: RequestOptions): Promise<T> {
    const response = await this.send(url, options);
    if (response.status === 204) {
      return undefined as T;
    }
    return response.json() as Promise<T>;
  }

  private async send(url: string, options: RequestOptions): Promise<Response> {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'OData-MaxVersion': '4.0',
      'OData-Version': '4.0',
      ...options.headers,
    };

    const init: RequestInit = {
      method: options.method ?? 'GET',
      credentials: 'same-origin',
      headers,
    };

    if (!this.shouldUseLocalFixture()) {
      headers.__RequestVerificationToken = await this.getRequestVerificationToken();
    }

    if (options.body !== undefined) {
      headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, init);
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${body.slice(0, 500)}`);
    }
    return response;
  }

  private async sendBinary(url: string, file: File): Promise<Response> {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'OData-MaxVersion': '4.0',
      'OData-Version': '4.0',
      'Content-Type': file.type || 'application/octet-stream',
      'x-ms-file-name': file.name,
    };

    if (!this.shouldUseLocalFixture()) {
      headers.__RequestVerificationToken = await this.getRequestVerificationToken();
    }

    const response = await fetch(url, {
      method: 'PATCH',
      credentials: 'same-origin',
      headers,
      body: file,
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${body.slice(0, 500)}`);
    }
    return response;
  }

  private async getRequestVerificationToken(): Promise<string> {
    return new Promise((resolve, reject) => {
      const deferred = window.shell?.getTokenDeferred?.();
      if (!deferred) {
        reject(new Error('Power Pages anti-forgery token provider is not available.'));
        return;
      }
      deferred.done(resolve).fail(() => reject(new Error('Unable to obtain Power Pages anti-forgery token.')));
    });
  }

  private shouldUseLocalFixture(): boolean {
    if (!import.meta.env.DEV) {
      return false;
    }

    return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  }

  private async extractSubmittedXml(payload: unknown): Promise<string> {
    const candidate = payload as OdkInstancePayload;
    if (candidate.status !== 'ready') {
      const violations = Array.isArray(candidate.violations) ? candidate.violations.length : 'unknown';
      throw new Error(`ODK validation is not ready for submission. Violations: ${violations}.`);
    }

    const instanceData = candidate.data?.[0];
    const file = instanceData?.get?.(INSTANCE_FILE_NAME);
    if (file instanceof File) {
      const xml = await file.text();
      if (xml.trim().startsWith('<')) {
        return xml;
      }
    }

    throw new Error('ODK submit payload did not include xml_submission_file instance XML.');
  }

  private extractInstanceId(xml: string): string | null {
    const parsed = new DOMParser().parseFromString(xml, 'text/xml');
    const instanceId = parsed.getElementsByTagName('instanceID')[0]?.textContent?.trim();
    return instanceId || null;
  }

  private async uploadAttachmentFile(attachmentId: string, attachment: AttachmentPayload): Promise<void> {
    await this.sendBinary(`/_api/mp_submissionattachments(${attachmentId})/mp_file`, attachment.file);
  }

  private extractAttachmentPayloads(payload: unknown): AttachmentPayload[] {
    const candidate = payload as OdkInstancePayload;
    const instanceData = candidate.data?.[0];
    const attachments: AttachmentPayload[] = [];
    instanceData?.forEach?.((value, fieldName) => {
      if (fieldName === INSTANCE_FILE_NAME || !(value instanceof File)) {
        return;
      }

      attachments.push({
        fieldName,
        fileName: value.name || fieldName,
        mediaType: value.type || 'application/octet-stream',
        size: value.size,
        file: value,
      });
    });

    return attachments;
  }

  private summarizePayload(payload: unknown, assignment: FormAssignmentSummary, xml: string): InstancePayloadSummary & {
    assignmentKey: string;
    formVersionId: string;
    xmlFormId: string;
  } {
    const candidate = payload as OdkInstancePayload;
    const instanceData = candidate.data?.[0];
    const attachmentNames: string[] = [];
    const attachmentDetails: AttachmentPayloadSummary[] = [];
    instanceData?.forEach?.((_value, key) => {
      if (key !== INSTANCE_FILE_NAME) {
        attachmentNames.push(key);
      }
    });
    for (const attachment of this.extractAttachmentPayloads(payload)) {
      attachmentDetails.push({
        fieldName: attachment.fieldName,
        fileName: attachment.fileName,
        mediaType: attachment.mediaType,
        size: attachment.size,
      });
    }

    return {
      payloadType: candidate.payloadType,
      status: candidate.status,
      violationCount: Array.isArray(candidate.violations) ? candidate.violations.length : 0,
      instanceName: this.resolveInstanceName(xml),
      submissionMeta: candidate.submissionMeta,
      attachmentNames,
      attachmentDetails,
      assignmentKey: assignment.assignmentKey,
      formVersionId: assignment.formVersionId,
      xmlFormId: assignment.xmlFormId,
      repeatPaths: this.extractRepeatPaths(assignment.xformXml ?? ''),
    };
  }

  private extractRepeatPaths(xformXml: string): string[] {
    const parsed = new DOMParser().parseFromString(xformXml, 'text/xml');
    if (parsed.getElementsByTagName('parsererror').length > 0) {
      return [];
    }

    const paths = Array.from(parsed.getElementsByTagNameNS('*', 'repeat'))
      .map((repeat) => repeat.getAttribute('nodeset') || repeat.getAttribute('ref') || '')
      .map((path) => path.trim().replace(/\/{2,}/g, '/'))
      .filter((path) => path.startsWith('/'));
    return Array.from(new Set(paths)).sort();
  }

  private escapeODataString(value: string): string {
    return value.replaceAll("'", "''");
  }

  private getPowerPagesRoles(): string[] {
    return (window.__TACATDP_POWERPAGES__?.roles ?? [])
      .map((role) => role.trim())
      .filter(Boolean);
  }

  private matchPowerPagesRoles(roleNames: string[]): string[] {
    const normalized = new Set(roleNames.map((role) => role.toLowerCase()));
    return this.getPowerPagesRoles()
      .filter((role) => normalized.has(role.toLowerCase()));
  }

  private isCurrentSessionEmail(value?: string): boolean {
    return value?.trim().toLowerCase() === this.getSignedInUserEmail().trim().toLowerCase();
  }

  private parseSubmissionMetadata(value?: string): { assignmentKey?: string; formVersionId?: string; xmlFormId?: string; instanceName?: string; repeatPaths?: string[] } {
    if (!value) {
      return {};
    }

    try {
      const parsed = JSON.parse(value) as { assignmentKey?: unknown; formVersionId?: unknown; xmlFormId?: unknown; instanceName?: unknown; repeatPaths?: unknown };
      return {
        assignmentKey: typeof parsed.assignmentKey === 'string' ? parsed.assignmentKey : undefined,
        formVersionId: typeof parsed.formVersionId === 'string' ? parsed.formVersionId : undefined,
        xmlFormId: typeof parsed.xmlFormId === 'string' ? parsed.xmlFormId : undefined,
        instanceName: typeof parsed.instanceName === 'string' ? parsed.instanceName : undefined,
        repeatPaths: Array.isArray(parsed.repeatPaths)
          ? parsed.repeatPaths.filter((path): path is string => typeof path === 'string' && path.startsWith('/'))
          : undefined,
      };
    } catch {
      return {};
    }
  }

  private normalizeInstanceId(xml: string, instanceId: string): string {
    const parsed = new DOMParser().parseFromString(xml, 'text/xml');
    const instanceIdElement = parsed.getElementsByTagName('instanceID')[0];
    if (!instanceIdElement) {
      return xml;
    }

    instanceIdElement.textContent = instanceId;
    return new XMLSerializer().serializeToString(parsed);
  }

  private resolveInstanceName(xml: string): string | undefined {
    const parsed = new DOMParser().parseFromString(xml, 'text/xml');
    const explicit = this.firstText(parsed, 'instanceName');
    if (explicit) {
      return explicit;
    }

    const customerId = this.firstText(parsed, 'Customer_ID');
    const customerName = this.firstText(parsed, 'Customer_Name');
    if (customerId && customerName) {
      return `${customerId}:${customerName}`;
    }
    if (customerId || customerName) {
      return customerId || customerName;
    }

    return undefined;
  }

  private firstText(document: Document, tagName: string): string | undefined {
    const value = document.getElementsByTagName(tagName)[0]?.textContent?.trim();
    return value || undefined;
  }
}
