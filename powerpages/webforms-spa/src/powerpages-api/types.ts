export interface DataverseCollection<T> {
  value: T[];
  '@odata.count'?: number;
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
}

export interface SubmissionVersionRow {
  mp_submissionversionid: string;
  mp_versionnumber: number;
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
