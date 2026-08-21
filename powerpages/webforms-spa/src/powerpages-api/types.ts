export interface DataverseCollection<T> {
  value: T[];
  '@odata.count'?: number;
}

export interface BaselineBridgeImportAsset {
  assetType: 'tacatdp-baseline-bridge-import';
  projectCode: string;
  formId: string;
  formVersion: string;
  counts?: {
    rows?: number;
    sourceUuidIdentifiers?: number;
    customerIdIdentifiers?: number;
    phoneIdentifiers?: number;
    duplicateReviewGroups?: number;
    duplicateReviewRows?: number;
  };
  duplicatePolicy?: string;
  rows: BaselineBridgeImportRow[];
}

export interface BaselineBridgeImportRow {
  rowNumber: number;
  uuid?: string;
  customerId?: string;
  customerName?: string;
  phone?: string;
  region?: string;
  district?: string;
  startedAt?: string | null;
  submittedAt?: string | null;
  sourceKey: string;
  instanceId: string;
  versionKey: string;
  linkKey: string;
  submissionJson: string;
  xformXml: string;
}

export type BaselineBridgeImportMode = 'append' | 'replace';

export interface BaselineBridgeImportOptions {
  limit?: number;
  dryRun?: boolean;
  mode?: BaselineBridgeImportMode;
  onProgress?: (progress: BaselineBridgeImportProgress) => void;
}

export interface BaselineBridgeImportProgress {
  processedRows: number;
  totalRows: number;
  currentRowNumber?: number;
  message: string;
}

export interface BaselineBridgeImportResult {
  status: 'validated' | 'executed';
  mode: BaselineBridgeImportMode;
  rowsProcessed: number;
  totalRows: number;
  limit?: number;
  counts: Record<string, number>;
  duplicateReviewGroups: number;
  duplicateReviewRows: number;
  messages: string[];
}

export interface BaselineImportDiagnosticStep {
  name: string;
  operation: string;
  status: 'passed' | 'failed';
  detail: string;
}

export interface IndicatorEvidenceSeedAsset {
  seed_name: 'tacatdp_indicator_evidence_seed';
  target_environment: string;
  target_project_code: string;
  writes_only: string[];
  indicator_definitions: IndicatorEvidenceSeedDefinition[];
}

export interface IndicatorEvidenceSeedDefinition {
  code: string;
  name: string;
  description?: string;
  indicator_type: 'Financial' | 'Output' | 'Outcome' | 'ClimateImpactEstimate' | 'OperationalDataQuality';
  result_level: 'Programme' | 'Component' | 'Outcome' | 'Output' | 'Activity' | 'Operational';
  unit: string;
  formula?: string;
  numerator?: string;
  denominator?: string;
  reporting_frequency: 'OnDemand' | 'Weekly' | 'Monthly' | 'Quarterly' | 'Seasonal' | 'Annual' | 'Baseline' | 'Endline';
  disaggregation?: string[];
  verification_method?: string;
  responsible_unit?: string;
  reporting_framework?: string;
  status: 'Draft' | 'Active' | 'Retired';
  mappings: IndicatorEvidenceSeedMapping[];
}

export interface IndicatorEvidenceSeedMapping {
  mapping_key: string;
  source_type: 'XFormField' | 'ImportedFileColumn' | 'DataverseTable' | 'PowerAutomateFlow' | 'PowerBIModel' | 'ExternalIntegration';
  source_table?: string;
  source_column?: string;
  source_path?: string;
  transform_rule?: string;
  required: boolean;
  active: boolean;
  notes?: string;
}

export interface IndicatorEvidenceSeedResult {
  status: 'validated' | 'executed';
  definitionsProcessed: number;
  mappingsProcessed: number;
  counts: Record<string, number>;
  messages: string[];
}

export interface IndicatorEvidenceReadBackDefinition {
  id: string;
  code: string;
  name: string;
  unit?: string;
  statusLabel: string;
  mappingSummary?: string;
}

export interface IndicatorEvidenceReadBackMapping {
  id: string;
  mappingKey: string;
  sourceTypeLabel: string;
  sourceTable?: string;
  sourceColumn?: string;
  indicatorDefinitionId?: string;
}

export interface IndicatorEvidenceReadBackResult {
  definitions: IndicatorEvidenceReadBackDefinition[];
  mappings: IndicatorEvidenceReadBackMapping[];
  expectedDefinitionCodes: string[];
  missingDefinitionCodes: string[];
  expectedMappingKeys: string[];
  missingMappingKeys: string[];
  readAt: string;
}

export interface FormAssignmentRow {
  mp_formassignmentid: string;
  mp_assignmentkey: string;
  mp_useremail?: string;
  mp_lifecyclestatus?: number;
  _mp_formversion_value: string;
}

export interface FormAssignmentMetadataRow extends FormAssignmentRow {
  'fv.mp_version'?: string;
  'fv.mp_webformsenabled'?: boolean;
  'fv.mp_form'?: string;
  'form.mp_name'?: string;
  'form.mp_xmlformid'?: string;
}

export interface FormVersionRow {
  mp_formversionid?: string;
  mp_version: string;
  mp_webformsenabled: boolean;
  mp_xformxml?: string;
  _mp_form_value: string;
}

export interface FormAttachmentRow {
  mp_formattachmentid: string;
  mp_filename: string;
  mp_mediatype?: string;
  _mp_formversion_value?: string;
}

export interface FormRow {
  mp_formid?: string;
  mp_name: string;
  mp_xmlformid: string;
}

export interface FormAssignmentSummary {
  assignmentId: string;
  assignmentKey: string;
  userEmail?: string;
  lifecycleStatus?: number;
  formVersionId: string;
  formId: string;
  formName: string;
  xmlFormId: string;
  version: string;
  xformXml?: string;
}

export interface ContactRow {
  contactid: string;
  fullname?: string;
  emailaddress1?: string;
  adx_identity_username?: string;
  adx_identity_logonenabled?: boolean;
  adx_identity_emailaddress1confirmed?: boolean;
  statecode?: number;
}

export type ActivationCheckState = 'ready' | 'pending' | 'missing' | 'unavailable' | 'review';

export type ActivationNextAction =
  | 'Send code'
  | 'Await redemption'
  | 'Redeemed'
  | 'Ready'
  | 'Needs admin review';

export interface UserActivationDiagnostic {
  id: string;
  name: string;
  email: string;
  contactId?: string;
  contactStatus: ActivationCheckState;
  emailUniquenessStatus: ActivationCheckState;
  invitationStatus: ActivationCheckState;
  redemptionStatus: ActivationCheckState;
  externalIdentityStatus: ActivationCheckState;
  webRoleStatus: ActivationCheckState;
  assignmentStatus: ActivationCheckState;
  nextAction: ActivationNextAction;
  detail: string;
  contactCount: number | null;
  activeInvitationCount: number | null;
  externalIdentityCount: number | null;
  activeAssignmentCount: number;
  latestInvitationStatus?: string;
  latestInvitationExpiresAt?: string;
  source: 'dataverse' | 'partial' | 'local-fixture';
}

export interface AccessUserSummary {
  id: string;
  name: string;
  email: string;
  contactId?: string;
  contactState: 'active' | 'missing' | 'unavailable';
  role: 'Platform Administrator' | 'Data Collector / Bank Officer';
  accessStatus: 'Active' | 'Needs contact check' | 'Needs admin review';
  assignments: FormAssignmentSummary[];
  projectCount: number;
  formCount: number;
}

export interface AccessAuthorizationDecision {
  allowed: boolean;
  source: 'local-dev-fixture' | 'power-pages-web-role' | 'none';
  matchedRoles: string[];
  detectedRoles: string[];
  requiredRoles: string[];
}

export type AccessWriteAction =
  | 'InviteUser'
  | 'AssignProject'
  | 'AssignForm'
  | 'CorrectEmail'
  | 'ChangeRole'
  | 'SuspendAccess'
  | 'ReactivateAccess'
  | 'RemoveAssignment'
  | 'RollbackAccessChange';

export type AccessWriteScopeType = 'Platform' | 'Project' | 'Form' | 'FormVersion' | 'Assignment';

export interface AccessWriteStateSnapshot {
  userEmail: string;
  contactId?: string;
  role?: string;
  status?: string;
  projectId?: string;
  projectName?: string;
  formId?: string;
  formName?: string;
  formVersionId?: string;
  assignmentId?: string;
}

export interface AccessWriteCommand {
  action: AccessWriteAction;
  affectedEmail: string;
  targetRole?: string;
  scopeType: AccessWriteScopeType;
  reason: string;
  sourceRoute: string;
  projectId?: string;
  formId?: string;
  formVersionId?: string;
  formAssignmentId?: string;
  previousState?: AccessWriteStateSnapshot;
  newState?: AccessWriteStateSnapshot;
  rollbackOfAuditId?: string;
}

export interface AccessWriteReadiness {
  enabled: boolean;
  statusLabel: string;
  disabledReason: string;
  requiredGates: string[];
}

export interface AccessAuditPreviewPayload {
  AuditKey: string;
  Action: AccessWriteAction;
  ResultStatus: 'Requested';
  ActorEmail: string;
  ActorRolesJson: string;
  AffectedEmail: string;
  TargetRole?: string;
  ScopeType: AccessWriteScopeType;
  PreviousStateJson?: string;
  NewStateJson?: string;
  Reason: string;
  SourceRoute: string;
  RequestId: string;
  OccurredAt: string;
  ResultMessage: string;
}

export interface AccessWritePreview {
  requestId: string;
  auditKey: string;
  enabled: boolean;
  statusLabel: string;
  disabledReason: string;
  auditPayload: AccessAuditPreviewPayload;
  mutationPayload: Record<string, unknown> | null;
}

export interface ManageAccessUserInput {
  action: 'CorrectEmail' | 'DeactivateAccess';
  user: AccessUserSummary;
  newEmail?: string;
  reason: string;
  sourceRoute: string;
}

export interface ManageAccessUserResult {
  requestId: string;
  auditKey: string;
  action: ManageAccessUserInput['action'];
  affectedEmail: string;
  newEmail?: string;
  updatedContact: boolean;
  updatedAssignments: number;
  preview: AccessWritePreview;
}

export interface AssignFormAccessInput {
  affectedEmail: string;
  formVersionId: string;
  formId?: string;
  formName?: string;
  projectId?: string;
  projectName?: string;
  targetRole?: string;
  reason: string;
  sourceRoute: string;
  contactId?: string;
}

export interface AssignFormAccessReadiness {
  enabled: boolean;
  statusLabel: string;
  disabledReason: string;
  requiredGates: string[];
}

export interface AssignFormAccessResult {
  status: 'created' | 'already-assigned';
  requestId: string;
  auditKey: string;
  assignmentId?: string;
  existingAssignmentId?: string;
  preview: AccessWritePreview;
}

export interface UserOnboardingAccessInput {
  fullName: string;
  affectedEmail: string;
  targetRole: string;
  requestType: 'NewUser' | 'ExistingUser' | 'Unresolved';
  projectId?: string;
  projectName?: string;
  reason: string;
  sourceRoute: string;
  replacementOfRequestId?: string;
  forms: Array<{
    formId?: string;
    formName?: string;
    formVersionId: string;
  }>;
}

export interface UserOnboardingAccessResult {
  status: 'queued';
  requestId: string;
  requestKey: string;
  queueRecordId: string;
  queueStatus: 'Pending' | 'Processing' | 'Completed' | 'Failed' | 'Cancelled' | 'NeedsReview';
  requestType: 'NewUser' | 'ExistingUser' | 'Unresolved';
  contactId?: string;
  contactCreated: false;
  emailDelivery: 'queued-for-invitation' | 'queued-for-assignment-notification' | 'manual-code-required' | 'email-sent';
  emailMessage: string;
  invitationId?: string;
  invitationCode?: string;
  invitationRedeemUrl?: string;
  invitationExpiresAt?: string;
  invitationStatus?: 'Pending' | 'ManualDeliveryRequired' | 'EmailSent' | 'Redeemed' | 'Expired' | 'Replaced';
  invitationDeliveryMode?: 'Email' | 'ManualCode' | 'AssignmentNotification';
  replacementOfRequestId?: string;
  assignmentResults: AssignFormAccessResult[];
}

export interface SubmissionRow {
  mp_submissionid: string;
  mp_instanceid: string;
  mp_useremail?: string;
  mp_submittedat?: string;
  mp_updatedat?: string;
  mp_lifecyclestatus?: number;
  mp_reviewstate?: number;
  _mp_formversion_value?: string;
}

export interface SubmissionVersionRow {
  mp_submissionversionid: string;
  mp_versionnumber: number;
  mp_instanceid?: string;
  mp_xformsubmissionxml?: string;
  mp_submissionjson?: string;
}

export interface OdkSubmitResult {
  instanceId: string;
  displayName?: string;
  submissionId: string;
  submissionVersionId: string;
  versionNumber: number;
  attachmentCount: number;
  attachmentBinaryUploadCount: number;
  attachmentWarnings: string[];
}


export interface BeneficiaryProfileRow {
  mp_beneficiaryprofileid: string;
  mp_name?: string;
  mp_beneficiarycategory?: number;
  mp_region?: string;
  mp_district?: string;
  mp_verificationstatus?: number;
  mp_datasource?: string;
  mp_lastupdatedat?: string;
  _mp_trackedentity_value?: string;
}

export interface EntityIdentifierRow {
  mp_entityidentifierid: string;
  mp_identifiertype?: number;
  mp_identifiervalue?: string;
  mp_status?: number;
  _mp_trackedentity_value?: string;
}

export interface BeneficiarySubmissionLinkRow {
  mp_beneficiarysubmissionlinkid: string;
  mp_linkkey?: string;
  mp_relationshiptype?: number;
  mp_completeness?: number;
  mp_reviewstatus?: number;
  _mp_trackedentity_value?: string;
  _mp_submission_value?: string;
}

export interface BeneficiaryListItem {
  id: string;
  name: string;
  category: 'Individual farmer' | 'Farmer group' | 'AMCOS' | 'SACCOS';
  region: string;
  district: string;
  borrowerStatus: 'Active borrower' | 'Training only' | 'Pending verification';
  loanType: 'Short-term' | 'Medium-term' | 'Long-term' | 'Not financed';
  technology: string;
  projectParticipation: {
    programme: string;
    project: string;
    implementationPartner: string;
    enrolmentDate: string;
    participationRole: string;
  };
  finance: {
    loanAccountRef: string;
    disbursedAmount: string;
    outstandingBalance: string;
    repaymentRate: string;
  };
  technologiesFinanced: Array<{
    name: string;
    category: string;
    adoptionStage: 'Planned' | 'In use' | 'Scaling';
  }>;
  trainingSummary: {
    sessionsAttended: number;
    lastTopic: string;
    completionRate: string;
    lastTrainingDate: string;
  };
  latestSubmission: {
    form: string;
    reportingPeriod: string;
    status: 'Submitted' | 'Under review' | 'Returned' | 'Awaiting submission';
    completeness: string;
    dataSource: string;
  };
  identityGovernance?: {
    matchState: 'Linked to tracked entity' | 'Candidate match review' | 'Create new tracked entity' | 'Needs investigation';
    matchSignals: string;
    reviewerDecision: string;
  };
  groupMembership?: {
    membershipType: 'Individual beneficiary' | 'Group beneficiary' | 'AMCOS beneficiary' | 'SACCOS beneficiary';
    membersLinked: string;
    membershipStatus: 'Active' | 'Pending verification' | 'Not modelled';
  };
  locationHistory?: {
    currentLocation: string;
    source: string;
    effectiveFrom: string;
    historyState: 'Current profile location' | 'Correction pending' | 'Awaiting submission';
  };
  outcomeSnapshot: {
    areaUnderImprovedPractices: string;
    yieldIncrease: string;
    climateEstimate: string;
  };
  futureDataverseMapping: {
    table: string;
    recordId: string;
    relationshipNotes: string;
  };
  trained: boolean;
  verificationStatus: 'Verified' | 'Under review' | 'Incomplete';
  lastUpdated: string;
  source: 'dataverse' | 'prototype';
}

export interface SubmissionSummary {
  submissionId: string;
  instanceId: string;
  displayName?: string;
  userEmail?: string;
  submittedAt?: string;
  updatedAt?: string;
  lifecycleStatus?: number;
  reviewState?: number;
  assignmentKey?: string;
  formVersionId?: string;
  xmlFormId?: string;
  versionNumber?: number;
}

export interface SubmissionReportRow {
  mp_submissionreportrowid: string;
  mp_reportkey: string;
  mp_instanceid: string;
  mp_displayname?: string;
  mp_useremail?: string;
  mp_submittedat?: string;
  mp_updatedat?: string;
  mp_versionnumber: number;
  mp_lifecyclestatus?: number;
  mp_reviewstate?: number;
  mp_projectionstatus: number;
  mp_projectedat?: string;
  mp_projectionerror?: string;
  mp_rootanswersjson?: string;
  _mp_formversion_value?: string;
}

export interface SubmissionAnswerRow {
  mp_submissionanswerid: string;
  mp_answerkey: string;
  mp_instanceid: string;
  mp_fieldpath: string;
  mp_fieldname?: string;
  mp_fieldlabel?: string;
  mp_valuetext?: string;
  mp_valuedecimal?: number;
  mp_valuedate?: string;
  mp_valueboolean?: boolean;
  mp_valuejson?: string;
  _mp_submissionreportrow_value: string;
  _mp_submissionrepeatrow_value?: string;
}

export interface ReportingFilters {
  search?: string;
  dateFrom?: string;
  dateTo?: string;
  submitter?: string;
  reviewState?: number;
  formVersionId?: string;
}

export interface ReportingAccessScope {
  mode: 'all-records' | 'own-records';
  ownerEmail?: string;
}

export interface SubmissionReportPage {
  rows: SubmissionReportRow[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ExportSettingRow {
  mp_exportsettingid: string;
  mp_exportkey: string;
  mp_name: string;
  mp_format: number;
  mp_scope: number;
  mp_filterjson?: string;
  mp_createdbyemail?: string;
  mp_createdat?: string;
  mp_updatedat?: string;
}

export interface CreateCsvExportSettingInput {
  name: string;
  formVersionId?: string;
  filters: ReportingFilters;
}

export type NotificationDeliveryMode = 'manual-code' | 'email';
export type MailboxReadinessStatus = 'not-configured' | 'pending-admin-setup' | 'approved' | 'tested-and-enabled' | 'failed';

export interface NotificationDeliverySetting {
  id?: string;
  settingKey: string;
  deliveryMode: NotificationDeliveryMode;
  senderMailbox?: string;
  mailboxStatus: MailboxReadinessStatus;
  nativeInvitationWorkflowId?: string;
  lastTestedAt?: string;
  lastTestResult?: string;
  instructions?: string;
  updatedByEmail?: string;
  updatedAt?: string;
  source: 'dataverse' | 'default';
}

export interface NotificationDeliverySettingInput {
  deliveryMode: NotificationDeliveryMode;
  senderMailbox?: string;
  mailboxStatus: MailboxReadinessStatus;
  nativeInvitationWorkflowId?: string;
  lastTestedAt?: string;
  lastTestResult?: string;
  instructions?: string;
}
