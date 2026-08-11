<script setup lang="ts">
import {
  Activity,
  ArrowLeft,
  BarChart3,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Clipboard,
  Database,
  Download,
  Eye,
  FileSpreadsheet,
  FilterX,
  FolderOpen,
  LayoutDashboard,
  LogIn,
  Mail,
  Menu,
  MoreVertical,
  NotepadText,
  Pencil,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  Settings,
  UserCog,
  Users,
} from '@lucide/vue';
import { computed, defineAsyncComponent, defineComponent, h, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import TacatdpDashboardPage from '../components/dashboard/TacatdpDashboardPage.vue';
import { draftStore, type LocalDraft } from '../offline/drafts';
import { PowerPagesApiClient } from '../powerpages-api/client';
import BeneficiariesView from './BeneficiariesView.vue';
import type {
  AssignFormAccessResult,
  AccessUserSummary,
  AccessWriteCommand,
  AccessWritePreview,
  ExportSettingRow,
  FormAssignmentSummary,
  MailboxReadinessStatus,
  NotificationDeliveryMode,
  NotificationDeliverySetting,
  ReportingFilters,
  SubmissionAnswerRow,
  SubmissionReportRow,
  SubmissionSummary,
  UserActivationDiagnostic,
  UserOnboardingAccessResult,
} from '../powerpages-api/types';
import { measureAsync } from '../performance';

type AppView = 'dashboard' | 'workspace' | 'projects' | 'beneficiaries' | 'records' | 'runner' | 'access' | 'reporting' | 'system-activity' | 'roadmap';
type FormSection = 'summary' | 'data' | 'exports' | 'powerbi';
type AccessSection = 'users' | 'add' | 'roles' | 'activity' | 'configuration';
type AccessChangeAction = 'email' | 'role' | 'suspend' | 'reactivate';
type RouteIntent = 'dashboard' | 'projects' | 'beneficiaries' | 'reporting' | 'access' | 'system-activity';
type SystemActivitySection = 'health' | 'events' | 'onboarding' | 'submissions' | 'integrations';

interface AccessActivityEvent {
  id: string;
  userId: string;
  userName: string;
  userEmail: string;
  event: string;
  detail: string;
  status: 'info' | 'warning' | 'success';
  source: string;
}

interface SystemHealthItem {
  id: string;
  component: string;
  status: 'healthy' | 'pending' | 'degraded' | 'blocked' | 'not-configured';
  summary: string;
  nextAction: string;
}

interface SystemActivityEvent {
  id: string;
  component: string;
  severity: 'info' | 'success' | 'warning' | 'error';
  status: string;
  action: string;
  detail: string;
  actor: string;
  target: string;
  occurredAt: string;
  nextAction: string;
}

interface AccessWorkflowOutcome {
  tone: 'success' | 'warning' | 'error';
  title: string;
  message: string;
  details: string[];
  email?: string;
  occurredAt: string;
}

type InvitationCopyField = 'code' | 'url';
type OnboardingTimelineState = 'done' | 'active' | 'waiting' | 'failed';

interface OnboardingTimelineItem {
  id: string;
  label: string;
  state: OnboardingTimelineState;
}

interface ProjectWorkspace {
  id: string;
  name: string;
  description: string;
  assignments: FormAssignmentSummary[];
}

const api = new PowerPagesApiClient();
const ODK_RUNTIME_ENABLED = import.meta.env.VITE_TACATDP_ODK_RUNTIME_ENABLED !== 'false';
const ACCESS_WORKFLOW_OUTCOME_KEY = 'tacatdp.accessWorkflowOutcome.v1';
const OdkWebForm = ODK_RUNTIME_ENABLED
  ? defineAsyncComponent(async () => {
      const module = await import('@getodk/web-forms');
      return module.OdkWebForm;
    })
  : defineComponent({
      name: 'OdkRuntimeDisabled',
      setup() {
        return () => h('p', { class: 'runtime-disabled-message' }, 'Data collection is disabled in this User & Access test build.');
      },
    });
const VueDatePicker = defineAsyncComponent(async () => {
  await import('@vuepic/vue-datepicker/dist/main.css');
  const module = await import('@vuepic/vue-datepicker');
  return module.VueDatePicker;
});
const pageSize = 10;
const loading = ref(false);
const workspaceHydrating = ref(false);
const authRequired = ref(false);
const error = ref('');
const assignments = ref<FormAssignmentSummary[]>([]);
const submissions = ref<SubmissionSummary[]>([]);
const localDrafts = ref<LocalDraft[]>([]);
const selectedProjectId = ref('');
const selectedAssignment = ref<FormAssignmentSummary | null>(null);
const selectedEditSubmission = ref<SubmissionSummary | null>(null);
const activeView = ref<AppView>('dashboard');
const selectedRoadmapModule = ref('Programmes');
const activeFormSection = ref<FormSection>('summary');
const shellNavCollapsed = ref(false);
const mobileNavOpen = ref(false);
const recordSearch = ref('');
const reportDateFrom = ref('');
const reportDateTo = ref('');
const reportSubmitter = ref('');
const reportReviewState = ref<number | ''>('');
const reportRows = ref<SubmissionReportRow[]>([]);
const reportTotal = ref(0);
const reportLoading = ref(false);
const reportError = ref('');
const selectedReportRow = ref<SubmissionReportRow | null>(null);
const reportAnswers = ref<SubmissionAnswerRow[]>([]);
const reportDetailLoading = ref(false);
const reportDetailError = ref('');
const exportSettings = ref<ExportSettingRow[]>([]);
const accessUsers = ref<AccessUserSummary[]>([]);
const activationDiagnostics = ref<UserActivationDiagnostic[]>([]);
const activationDiagnosticsLoading = ref(false);
const activationDiagnosticsError = ref('');
const accessLoading = ref(false);
const accessError = ref('');
const accessSearch = ref('');
const accessRoleFilter = ref('');
const activeAccessSection = ref<AccessSection>('users');
const selectedAccessUser = ref<AccessUserSummary | null>(null);
const selectedAccessAction = ref<AccessChangeAction | null>(null);
const accessChangeRole = ref('');
const accessChangeEmail = ref('');
const accessChangeReason = ref('');
const accessChangeSubmitting = ref(false);
const accessChangeMessage = ref('');
const accessChangeError = ref('');
const accessWorkflowOpen = ref(false);
const accessWorkflowStep = ref(1);
const accessWorkflowFullName = ref('');
const accessWorkflowEmail = ref('');
const accessWorkflowRole = ref('Data Collector / Bank Officer');
const accessWorkflowProjectId = ref('');
const accessWorkflowFormVersionIds = ref<string[]>([]);
const accessWorkflowReason = ref('');
const accessWorkflowSubmitting = ref(false);
const accessWorkflowSubmitMessage = ref('');
const accessWorkflowSubmitError = ref('');
const accessWorkflowSubmitResults = ref<AssignFormAccessResult[]>([]);
const accessWorkflowOnboardingResult = ref<UserOnboardingAccessResult | null>(null);
const invitationCopyStatus = ref('');
const accessWorkflowReplacementOfRequestId = ref('');
const accessWorkflowForceInvitation = ref(false);
const accessWorkflowOutcome = ref<AccessWorkflowOutcome | null>(null);
const accessRouteDenied = ref(false);
const notificationSetting = ref<NotificationDeliverySetting | null>(null);
const notificationDeliveryMode = ref<NotificationDeliveryMode>('manual-code');
const notificationSenderMailbox = ref('');
const notificationMailboxStatus = ref<MailboxReadinessStatus>('not-configured');
const notificationWorkflowId = ref('');
const notificationLastTestResult = ref('');
const notificationInstructions = ref('');
const notificationLoading = ref(false);
const notificationSaving = ref(false);
const notificationMessage = ref('');
const notificationError = ref('');
const activeSystemActivitySection = ref<SystemActivitySection>('health');
const exportName = ref('');
const exportLoading = ref(false);
const exportMessage = ref('');
const exportError = ref('');
const powerBiCopyStatus = ref('');
const savedPage = ref(1);
const draftPage = ref(1);
const online = ref(typeof navigator === 'undefined' ? true : navigator.onLine);
const runtimeStatus = ref('');
const submitStatus = ref('');
const postSubmitMessage = ref('');
const postSubmitTone = ref<'success' | 'warning'>('success');
const submitTone = ref<'neutral' | 'success' | 'warning' | 'error'>('neutral');
const submitting = ref(false);
const formRuntimeLoading = ref(false);
const formRuntimeMountReady = ref(false);
let formRuntimeFallbackTimer: number | null = null;
const lastWorkspaceRefreshAt = ref('');
const warmedAssignments = new Map<string, FormAssignmentSummary>();
const platformName = 'MEL Tool';
const crdbLogoUrl = '/CRDB_Bank_PLC.svg';
const runtimeClickStatus = ref('No ODK runtime button click observed in this page load.');
const odkSubmitEventStatus = ref('No ODK submit event observed in this page load.');
const dataverseWriteStatus = ref('No Dataverse submit write attempted in this page load.');
let odkRuntimeObserver: MutationObserver | null = null;
let reportSearchTimer: number | null = null;

function parseDateFilter(value: string): Date {
  const [year, month, day] = value.split('-').map(Number);
  return new Date(year, month - 1, day);
}

function formatDateFilter(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function dateDaysAgo(days: number): Date {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() - days);
  return date;
}

const reportDateRange = computed<Date[] | null>({
  get() {
    if (!reportDateFrom.value || !reportDateTo.value) {
      return null;
    }
    return [parseDateFilter(reportDateFrom.value), parseDateFilter(reportDateTo.value)];
  },
  set(range) {
    if (!range || range.length !== 2 || !range[0] || !range[1]) {
      if (!range) {
        reportDateFrom.value = '';
        reportDateTo.value = '';
      }
      return;
    }
    reportDateFrom.value = formatDateFilter(range[0]);
    reportDateTo.value = formatDateFilter(range[1]);
  },
});

const reportDatePresets = [
  { label: 'Today', value: [dateDaysAgo(0), dateDaysAgo(0)] },
  { label: 'Last 7 days', value: [dateDaysAgo(6), dateDaysAgo(0)] },
  { label: 'Last 30 days', value: [dateDaysAgo(29), dateDaysAgo(0)] },
  { label: 'This month', value: [new Date(new Date().getFullYear(), new Date().getMonth(), 1), dateDaysAgo(0)] },
];

const powerBiEnvironmentUrl = 'https://orga3cf4b37.crm4.dynamics.com';
const powerBiTables = [
  { logical: 'mp_submissionreportrow', label: 'Submission report rows', purpose: 'One current row per submitted record' },
  { logical: 'mp_submissionrepeatrow', label: 'Submission repeat rows', purpose: 'One row per repeat-group instance' },
  { logical: 'mp_submissionanswer', label: 'Submission answers', purpose: 'Long-format answer facts' },
];

const accessRoleReference = [
  { role: 'Platform Administrator', summary: 'Manages users, projects, forms, reporting, and configuration.' },
  { role: 'Project Manager', summary: 'Manages users and form access for assigned projects.' },
  { role: 'Supervisor / Reviewer', summary: 'Reviews assigned project submissions and flags issues.' },
  { role: 'Data Collector / Bank Officer', summary: 'Collects data and works with assigned forms.' },
  { role: 'Reporting Officer', summary: 'Views project data, exports, and Power BI connection guidance.' },
  { role: 'Read-only Auditor', summary: 'Views assigned project records and access status without edits.' },
];
const accessWriteReadiness = computed(() => api.getAccessWriteReadiness());
const userOnboardingReadiness = computed(() => api.getUserOnboardingReadiness());
const accessWriteActionStatus = computed(() => accessWriteReadiness.value.statusLabel);

const projectWorkspaces = computed<ProjectWorkspace[]>(() => {
  if (assignments.value.length === 0) {
    return [];
  }

  return [{
    id: 'tacatdp-impact-monitoring',
    name: 'TACATDP Impact Evaluation',
    description: 'Secure Microsoft-hosted impact evaluation workspace for assigned project data.',
    assignments: assignments.value,
  }];
});
const accessAuthorization = computed(() => api.getCurrentUserAccessAuthorization());
const canManageAccess = computed(() => accessAuthorization.value.allowed);
const accessAuthorizationSourceLabel = computed(() => {
  if (accessAuthorization.value.source === 'local-dev-fixture') return 'Local development fixture';
  if (accessAuthorization.value.source === 'power-pages-web-role') return 'Power Pages web role';
  return 'No admin role matched';
});
const detectedAccessRoleLabel = computed(() => (
  accessAuthorization.value.detectedRoles.length > 0
    ? accessAuthorization.value.detectedRoles.join(', ')
    : 'No roles detected in the current Power Pages session'
));
const requiredAccessRoleLabel = computed(() => accessAuthorization.value.requiredRoles.join(' or '));
const matchedAccessRoleLabel = computed(() => (
  accessAuthorization.value.matchedRoles.length > 0
    ? accessAuthorization.value.matchedRoles.join(', ')
    : 'None'
));
const filteredAccessUsers = computed(() => {
  const query = accessSearch.value.trim().toLowerCase();
  const role = accessRoleFilter.value;
  return accessUsers.value.filter((user) => {
    const matchesQuery = !query || [user.name, user.email, user.role, user.accessStatus]
      .some((value) => value.toLowerCase().includes(query));
    const matchesRole = !role || user.role === role;
    return matchesQuery && matchesRole;
  });
});
const activeAccessUserCount = computed(() => accessUsers.value.filter((user) => user.accessStatus === 'Active').length);
const contactCheckCount = computed(() => accessUsers.value.filter((user) => user.contactState !== 'active').length);
const accessRoleOptions = computed(() => Array.from(new Set(accessUsers.value.map((user) => user.role))).sort());
const activationReadyCount = computed(() => activationDiagnostics.value.filter((row) => row.nextAction === 'Ready').length);
const activationPendingCount = computed(() => activationDiagnostics.value.filter((row) => row.nextAction === 'Await redemption' || row.nextAction === 'Send code').length);
const activationReviewCount = computed(() => activationDiagnostics.value.filter((row) => row.nextAction === 'Needs admin review').length);
const accessWorkflowRoleOptions = computed(() => accessRoleReference.map((role) => role.role));
const accessWorkflowSteps = [
  { id: 1, label: 'User' },
  { id: 2, label: 'Role' },
  { id: 3, label: 'Access' },
  { id: 4, label: 'Review' },
];
const accessChangeActionLabel = computed(() => {
  if (selectedAccessAction.value === 'email') return 'Correct email';
  if (selectedAccessAction.value === 'role') return 'Change role';
  if (selectedAccessAction.value === 'suspend') return 'Remove access';
  if (selectedAccessAction.value === 'reactivate') return 'Reactivate access';
  return 'Access change';
});
const accessChangeSummary = computed(() => {
  if (!selectedAccessUser.value || !selectedAccessAction.value) {
    return '';
  }
  if (selectedAccessAction.value === 'role') {
    return `${selectedAccessUser.value.role} to ${accessChangeRole.value || 'No role selected'}`;
  }
  if (selectedAccessAction.value === 'email') {
    return `${selectedAccessUser.value.email} to ${accessChangeEmail.value.trim().toLowerCase() || 'No email entered'}`;
  }
  if (selectedAccessAction.value === 'suspend') {
    return `${selectedAccessUser.value.accessStatus} to Inactive`;
  }
  return `${selectedAccessUser.value.accessStatus} to Active`;
});
const accessChangeEmailNormalized = computed(() => accessChangeEmail.value.trim().toLowerCase());
const accessChangeCanApply = computed(() => {
  if (!selectedAccessUser.value || !selectedAccessAction.value || accessChangeSubmitting.value || !accessWriteReadiness.value.enabled) {
    return false;
  }
  if (!accessChangeReason.value.trim()) {
    return false;
  }
  if (selectedAccessAction.value === 'email') {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(accessChangeEmailNormalized.value)
      && accessChangeEmailNormalized.value !== selectedAccessUser.value.email.toLowerCase();
  }
  return selectedAccessAction.value === 'suspend';
});
const selectedAccessWritePreview = computed<AccessWritePreview | null>(() => {
  const command = buildSelectedAccessWriteCommand();
  if (!command) {
    return null;
  }
  return buildSafeAccessWritePreview(command);
});
const selectedAccessProjectName = computed(() => projectWorkspaces.value[0]?.name ?? 'Assigned project');
const accessActivityEvents = computed<AccessActivityEvent[]>(() => accessUsers.value.flatMap((user) => {
  const events: AccessActivityEvent[] = [{
    id: `${user.id}:assignment-scope`,
    userId: user.id,
    userName: user.name,
    userEmail: user.email,
    event: 'Assignment scope reviewed',
    detail: `${user.formCount} assigned forms across ${user.projectCount} projects.`,
    status: user.formCount > 0 ? 'success' : 'warning',
    source: 'Derived from current form assignments',
  }];

  if (user.contactState !== 'active') {
    events.push({
      id: `${user.id}:contact-check`,
      userId: user.id,
      userName: user.name,
      userEmail: user.email,
      event: 'Contact check needed',
      detail: formatContactState(user.contactState),
      status: 'warning',
      source: 'Derived from Power Pages contact lookup',
    });
  }

  if (user.accessStatus !== 'Active') {
    events.push({
      id: `${user.id}:access-status`,
      userId: user.id,
      userName: user.name,
      userEmail: user.email,
      event: 'Access pending review',
      detail: user.accessStatus,
      status: 'warning',
      source: 'Derived from current portal access status',
    });
  }

  return events;
}));
const selectedAccessUserActivity = computed(() => {
  const user = selectedAccessUser.value;
  if (!user) return [];
  return accessActivityEvents.value.filter((event) => event.userId === user.id);
});
const systemHealthItems = computed<SystemHealthItem[]>(() => [
  {
    id: 'auth',
    component: 'Authentication',
    status: canManageAccess.value ? 'healthy' : 'blocked',
    summary: canManageAccess.value ? 'Platform Administrator role detected.' : 'Current session does not have the Platform Administrator role.',
    nextAction: canManageAccess.value ? 'No action required.' : 'Confirm Power Pages web role membership for this contact.',
  },
  {
    id: 'device',
    component: 'Device connection',
    status: online.value ? 'healthy' : 'degraded',
    summary: online.value ? 'Browser reports network connectivity.' : 'Device is offline.',
    nextAction: online.value ? 'Continue normal work.' : 'Reconnect before submitting records or refreshing assignments.',
  },
  {
    id: 'assignments',
    component: 'Assignments',
    status: assignments.value.length > 0 ? 'healthy' : workspaceHydrating.value ? 'pending' : 'degraded',
    summary: `${assignments.value.length} assigned form${assignments.value.length === 1 ? '' : 's'} loaded.`,
    nextAction: assignments.value.length > 0 ? 'No action required.' : 'Refresh assignments or review user/project access.',
  },
  {
    id: 'activation',
    component: 'Activation diagnostics',
    status: activationDiagnosticsError.value ? 'blocked' : activationReviewCount.value > 0 ? 'degraded' : activationPendingCount.value > 0 ? 'pending' : 'healthy',
    summary: activationDiagnosticsError.value || `${activationReadyCount.value} ready, ${activationPendingCount.value} pending, ${activationReviewCount.value} need review.`,
    nextAction: activationDiagnosticsError.value ? 'Check diagnostics Web API/table permissions.' : activationReviewCount.value > 0 ? 'Open System Activity > Onboarding.' : 'Monitor new invitations after redemption.',
  },
  {
    id: 'onboarding',
    component: 'Onboarding queue',
    status: userOnboardingReadiness.value.enabled ? 'healthy' : 'not-configured',
    summary: userOnboardingReadiness.value.statusLabel,
    nextAction: userOnboardingReadiness.value.enabled ? 'Use Add user workflow.' : 'Enable the approved onboarding queue path before creating users.',
  },
  {
    id: 'notification',
    component: 'Invitation delivery',
    status: notificationDeliveryMode.value === 'email'
      ? notificationEmailModeReady.value ? 'healthy' : 'degraded'
      : 'pending',
    summary: `${notificationDeliveryModeLabel.value} · ${notificationMailboxStatusLabel.value}`,
    nextAction: notificationDeliveryMode.value === 'email'
      ? notificationEmailModeReady.value ? 'Email delivery is configured.' : 'Complete mailbox Test & Enable, or use manual invitation code.'
      : 'Share manual redeem link/code through an approved CRDB channel.',
  },
  {
    id: 'submissions',
    component: 'Submissions',
    status: error.value ? 'blocked' : draftCount.value > 0 ? 'pending' : 'healthy',
    summary: error.value || `${draftCount.value} local draft${draftCount.value === 1 ? '' : 's'} on this device.`,
    nextAction: error.value ? 'Review workspace error before collecting data.' : draftCount.value > 0 ? 'Review drafts before duplicate collection.' : 'No action required.',
  },
  {
    id: 'reporting',
    component: 'Reporting projection',
    status: reportError.value ? 'blocked' : reportLoading.value ? 'pending' : 'healthy',
    summary: reportError.value || `${activeRecordCount.value} projected record${activeRecordCount.value === 1 ? '' : 's'} in the current data view.`,
    nextAction: reportError.value ? 'Open Data or Reporting and review the projection/API error.' : 'No action required.',
  },
]);
const systemHealthAttentionCount = computed(() => systemHealthItems.value.filter((item) => item.status === 'blocked' || item.status === 'degraded').length);
const systemHealthPendingCount = computed(() => systemHealthItems.value.filter((item) => item.status === 'pending' || item.status === 'not-configured').length);
const systemActivityEvents = computed<SystemActivityEvent[]>(() => {
  const now = new Date().toISOString();
  const events: SystemActivityEvent[] = [];

  systemHealthItems.value
    .filter((item) => item.status !== 'healthy')
    .forEach((item) => {
      events.push({
        id: `health:${item.id}`,
        component: item.component,
        severity: item.status === 'blocked' || item.status === 'degraded' ? 'warning' : 'info',
        status: formatSystemHealthStatus(item.status),
        action: 'Operational check',
        detail: item.summary,
        actor: 'System check',
        target: item.component,
        occurredAt: now,
        nextAction: item.nextAction,
      });
    });

  accessActivityEvents.value.slice(0, 6).forEach((event) => {
    events.push({
      id: `access:${event.id}`,
      component: 'User & Access',
      severity: event.status,
      status: event.status === 'success' ? 'Succeeded' : 'Needs review',
      action: event.event,
      detail: event.detail,
      actor: 'Derived access check',
      target: event.userEmail,
      occurredAt: now,
      nextAction: event.status === 'warning' ? 'Open User & Access for the affected user.' : 'No action required.',
    });
  });

  if (accessWorkflowOutcome.value) {
    events.unshift({
      id: `onboarding:${accessWorkflowOutcome.value.occurredAt}`,
      component: 'Onboarding',
      severity: accessWorkflowOutcome.value.tone,
      status: accessWorkflowOutcome.value.title,
      action: 'Create, invite and assign',
      detail: accessWorkflowOutcome.value.message,
      actor: api.getSignedInUserEmail() || 'Current administrator',
      target: accessWorkflowOutcome.value.email || 'Requested user',
      occurredAt: accessWorkflowOutcome.value.occurredAt,
      nextAction: accessWorkflowOutcome.value.details[0] || 'Review onboarding result.',
    });
  }

  return events.slice(0, 20);
});
const systemActivityOnboardingEvents = computed(() => systemActivityEvents.value.filter((event) => event.component === 'Onboarding' || event.component === 'Activation diagnostics' || event.component === 'User & Access'));
const systemActivitySubmissionEvents = computed(() => systemActivityEvents.value.filter((event) => event.component === 'Submissions' || event.component === 'Reporting projection'));
const systemActivityIntegrationEvents = computed(() => systemActivityEvents.value.filter((event) => event.component === 'Invitation delivery' || event.component === 'Reporting projection'));
const accessWorkflowEmailNormalized = computed(() => accessWorkflowEmail.value.trim().toLowerCase());
const accessWorkflowExistingUser = computed(() => {
  const email = accessWorkflowEmailNormalized.value;
  if (!email) return null;
  return accessUsers.value.find((user) => user.email.toLowerCase() === email) ?? null;
});
const accessWorkflowIsExistingUser = computed(() => Boolean(accessWorkflowExistingUser.value));
const accessWorkflowOnboardingMode = computed(() => (accessWorkflowForceInvitation.value ? 'new' : accessWorkflowIsExistingUser.value ? 'existing' : 'new'));
const accessWorkflowOnboardingLabel = computed(() => (
  accessWorkflowForceInvitation.value
    ? 'Reissue invitation and assign'
    : accessWorkflowIsExistingUser.value ? 'Assign existing user and notify' : 'Create contact, invite and assign'
));
const accessWorkflowDeliveryLabel = computed(() => (
  accessWorkflowIsExistingUser.value && !accessWorkflowForceInvitation.value
    ? 'Assignment notification'
    : notificationDeliveryMode.value === 'email'
      ? 'Power Pages invitation email'
      : 'Manual invitation code'
));
const notificationDeliveryModeLabel = computed(() => (
  notificationDeliveryMode.value === 'email' ? 'Mailbox email delivery' : 'Manual invitation code'
));
const notificationMailboxStatusLabel = computed(() => {
  const labels: Record<MailboxReadinessStatus, string> = {
    'not-configured': 'Not configured',
    'pending-admin-setup': 'Pending admin setup',
    approved: 'Approved',
    'tested-and-enabled': 'Tested and enabled',
    failed: 'Failed',
  };
  return labels[notificationMailboxStatus.value];
});
const notificationEmailModeReady = computed(() => (
  notificationSenderMailbox.value.trim().length > 0
  && notificationMailboxStatus.value === 'tested-and-enabled'
));
const notificationCanSave = computed(() => (
  !notificationSaving.value
  && (notificationDeliveryMode.value === 'manual-code' || notificationEmailModeReady.value)
));
const notificationSourceLabel = computed(() => (
  notificationSetting.value?.source === 'dataverse' ? 'Dataverse configuration' : 'Default manual-code fallback'
));
const accessWorkflowContactState = computed<AccessUserSummary['contactState']>(() => {
  const existing = accessWorkflowExistingUser.value;
  if (existing) return existing.contactState;
  return accessWorkflowEmailNormalized.value ? 'missing' : 'unavailable';
});
const accessWorkflowSelectedProject = computed(() => projectWorkspaces.value.find((project) => project.id === accessWorkflowProjectId.value) ?? null);
const accessWorkflowSelectedForms = computed(() => {
  const selected = new Set(accessWorkflowFormVersionIds.value);
  return (accessWorkflowSelectedProject.value?.assignments ?? []).filter((assignment) => selected.has(assignment.formVersionId));
});
const accessWorkflowReasonText = computed(() => accessWorkflowReason.value.trim() || 'Pending administrator reason before activation');
const accessWorkflowCanProceed = computed(() => {
  if (accessWorkflowStep.value === 1) return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(accessWorkflowEmailNormalized.value) && accessWorkflowFullName.value.trim().length > 0;
  if (accessWorkflowStep.value === 2) return Boolean(accessWorkflowRole.value);
  if (accessWorkflowStep.value === 3) return Boolean(accessWorkflowProjectId.value) && accessWorkflowFormVersionIds.value.length > 0;
  return false;
});
const accessWorkflowCanSubmit = computed(() => (
  accessWorkflowStep.value === 4
  && userOnboardingReadiness.value.enabled
  && !accessWorkflowSubmitting.value
  && Boolean(accessWorkflowEmailNormalized.value)
  && accessWorkflowFullName.value.trim().length > 0
  && accessWorkflowSelectedForms.value.length > 0
  && accessWorkflowReason.value.trim().length > 0
));
const selectedProject = computed(() => projectWorkspaces.value.find((project) => project.id === selectedProjectId.value) ?? null);
const shellPageTitle = computed(() => {
  if (activeView.value === 'dashboard') return 'Dashboard';
  if (activeView.value === 'workspace') return 'Workspace';
  if (activeView.value === 'beneficiaries') return 'Beneficiaries';
  if (activeView.value === 'access') return 'User & Access';
  if (activeView.value === 'system-activity') return 'System Activity';
  if (activeView.value === 'reporting') return 'Reporting';
  if (activeView.value === 'roadmap') return selectedRoadmapModule.value;
  if (activeView.value === 'runner') return selectedAssignment.value?.formName || 'Form';
  if (activeView.value === 'records') return selectedProject.value?.name || 'Project';
  return 'Projects';
});
const shellPageEyebrow = computed(() => {
  if (activeView.value === 'access' || activeView.value === 'system-activity') return 'Administration';
  if (activeView.value === 'reporting' || activeView.value === 'roadmap' || activeView.value === 'beneficiaries') return 'MEL platform';
  if (activeView.value === 'records') return 'Project';
  if (activeView.value === 'runner') return runnerTitle.value;
  if (activeView.value === 'workspace') return 'Field operations';
  if (activeView.value === 'dashboard') return 'Monitoring sustainability outcomes and loan performance across Tanzania.';
  return 'MEL platform';
});
const selectedProjectAssignments = computed(() => selectedProject.value?.assignments ?? []);
const primaryAssignment = computed(() => selectedProjectAssignments.value[0] ?? assignments.value[0] ?? null);
const draftCount = computed(() => localDrafts.value.length);
const savedCount = computed(() => submissions.value.length);
const dashboardRecentSubmissions = computed(() => submissions.value.slice(0, 5));
const dashboardPrimaryProject = computed(() => selectedProject.value ?? projectWorkspaces.value[0] ?? null);
const dashboardPrimaryAssignment = computed(() => dashboardPrimaryProject.value?.assignments[0] ?? assignments.value[0] ?? null);
const dashboardLastRefreshLabel = computed(() => (
  lastWorkspaceRefreshAt.value ? formatTime(lastWorkspaceRefreshAt.value) : 'Not refreshed'
));
const dashboardSyncSummary = computed(() => (
  lastWorkspaceRefreshAt.value
    ? `Assignments refreshed ${dashboardLastRefreshLabel.value}`
    : 'Assignments not refreshed'
));
const dashboardDataAccessValue = computed(() => (api.getReportingAccessScope().mode === 'all-records' ? 'All records' : 'My records'));
const dashboardDataAccessDetail = computed(() => (api.getReportingAccessScope().mode === 'all-records' ? 'Administrator scope' : 'Collector scope'));
const dashboardSubmittedScopeLabel = computed(() => (api.getReportingAccessScope().mode === 'all-records' ? 'All project records' : 'My records'));
const signedInUserLabel = computed(() => api.getSignedInUserLabel());
const signedInUserName = computed(() => {
  const powerPagesName = window.__TACATDP_POWERPAGES__?.userName?.trim();
  if (powerPagesName) return powerPagesName;
  const label = signedInUserLabel.value.trim();
  if (!label) return 'User';
  if (!label.includes('@')) return label;
  const localPart = label.split('@')[0].replace(/[._-]+/g, ' ').trim();
  return localPart || label;
});
const signedInUserInitials = computed(() => {
  const label = signedInUserName.value.trim();
  if (!label) return 'U';
  const parts = label.split(/\s+/).filter(Boolean);
  return (parts.length > 1 ? `${parts[0][0]}${parts[1][0]}` : label.slice(0, 2)).toUpperCase();
});
const signedInUserRoleLabel = computed(() => (canManageAccess.value ? 'Platform Administrator' : 'MEL User'));

const dashboardMetricItems = computed(() => [
  {
    id: 'active-projects',
    value: workspaceHydrating.value && assignments.value.length === 0 ? '...' : String(projectWorkspaces.value.length),
    label: 'Active projects',
    detail: 'Assigned workspaces',
    tone: 'neutral',
  },
  {
    id: 'forms-action',
    value: workspaceHydrating.value && assignments.value.length === 0 ? '...' : String(assignments.value.length),
    label: 'Assigned forms',
    detail: 'Available to collect',
    tone: 'neutral',
  },
  {
    id: 'local-drafts',
    value: String(draftCount.value),
    label: 'Drafts on this device',
    detail: draftCount.value > 0 ? 'Resume before submitting' : 'No drafts on this device',
    tone: draftCount.value > 0 ? 'warning' : 'success',
  },
  {
    id: 'data-access',
    value: dashboardDataAccessValue.value,
    label: 'Data access',
    detail: dashboardDataAccessDetail.value,
    tone: 'neutral',
  },
]);
const dashboardAttentionItems = computed(() => {
  const items: Array<{ id: string; title: string; detail: string; tone: 'warning' | 'error' | 'info' }> = [];

  if (error.value) {
    items.push({
      id: 'workspace-error',
      title: 'Workspace needs attention',
      detail: error.value,
      tone: 'error',
    });
  }

  if (!online.value) {
    items.push({
      id: 'offline',
      title: 'Device offline',
      detail: 'Continue drafts locally and reconnect before submitting records to Dataverse.',
      tone: 'warning',
    });
  }

  if (draftCount.value > 0) {
    items.push({
      id: 'local-drafts',
      title: `${draftCount.value} draft${draftCount.value === 1 ? '' : 's'} on this device`,
      detail: 'Review device drafts before starting duplicate field records.',
      tone: 'warning',
    });
  }

  if (!workspaceHydrating.value && assignments.value.length === 0 && !error.value) {
    items.push({
      id: 'no-assignment',
      title: 'No project assignment found',
      detail: 'Ask a platform administrator to assign project and form access for this account.',
      tone: 'info',
    });
  }

  return items;
});
const reportingProjectRows = computed(() => projectWorkspaces.value.map((project) => ({
  project,
  forms: project.assignments.length,
  records: submissions.value.length,
  lastUpdated: submissions.value[0]?.updatedAt || submissions.value[0]?.submittedAt || '',
  projectionStatus: reportError.value ? 'Needs attention' : 'Ready',
})));
const selectedFormSubmissions = computed(() => {
  const formVersionId = selectedAssignment.value?.formVersionId;
  if (!formVersionId) {
    return submissions.value;
  }

  return submissions.value.filter((submission) => submission.formVersionId === formVersionId || !submission.formVersionId);
});
const selectedFormDrafts = computed(() => {
  const formVersionId = selectedAssignment.value?.formVersionId;
  if (!formVersionId) {
    return localDrafts.value;
  }

  return localDrafts.value.filter((draft) => draft.formVersionId === formVersionId);
});
const selectedFormSavedCount = computed(() => selectedFormSubmissions.value.length);
const selectedFormDraftCount = computed(() => selectedFormDrafts.value.length);
const activeRecordCount = computed(() => reportTotal.value);
const activeRecordPage = computed(() => savedPage.value);
const activeTotalPages = computed(() => Math.max(1, Math.ceil(activeRecordCount.value / pageSize)));
const activePageStart = computed(() => activeRecordCount.value === 0 ? 0 : ((activeRecordPage.value - 1) * pageSize) + 1);
const activePageEnd = computed(() => Math.min(activeRecordPage.value * pageSize, activeRecordCount.value));
const visiblePageNumbers = computed(() => {
  const total = activeTotalPages.value;
  const current = activeRecordPage.value;
  const start = Math.max(1, current - 1);
  const end = Math.min(total, start + 2);
  const adjustedStart = Math.max(1, end - 2);
  return Array.from({ length: end - adjustedStart + 1 }, (_, index) => adjustedStart + index);
});
const activeReportFilters = computed<ReportingFilters>(() => ({
  search: recordSearch.value.trim() || undefined,
  dateFrom: reportDateFrom.value || undefined,
  dateTo: reportDateTo.value || undefined,
  submitter: canReadAllReportingRows.value ? reportSubmitter.value.trim() || undefined : undefined,
  reviewState: reportReviewState.value === '' ? undefined : reportReviewState.value,
  formVersionId: selectedAssignment.value?.formVersionId,
}));
const reportingAccessScope = computed(() => api.getReportingAccessScope());
const canReadAllReportingRows = computed(() => reportingAccessScope.value.mode === 'all-records');
const reportingScopeLabel = computed(() => canReadAllReportingRows.value ? 'All submitted records' : 'My submitted records');
const reportingScopeSummary = computed(() => canReadAllReportingRows.value
  ? 'Platform administrators can view and export all projected records for this form.'
  : `Collectors can view and export only records submitted by ${reportingAccessScope.value.ownerEmail || 'their signed-in account'}.`);
const exportScopeMessage = computed(() => canReadAllReportingRows.value
  ? 'Download includes all rows matching the current filters.'
  : 'Download is automatically restricted to your submitted rows, even when saved filters are reused.');
const uniqueSubmitters = computed(() => [...new Set(reportRows.value.map((row) => row.mp_useremail).filter((value): value is string => Boolean(value)))].sort());
const selectedVersionLabel = computed(() => {
  if (!selectedAssignment.value) {
    return '';
  }
  return `${selectedAssignment.value.formName} v${selectedAssignment.value.version}`;
});
const runnerTitle = computed(() => selectedEditSubmission.value ? 'Edit record' : 'Form');
const editInstanceOptions = computed(() => {
  const submission = selectedEditSubmission.value;
  if (!submission) {
    return null;
  }

  return {
    resolveInstance: () => api.getLatestSubmissionXml(submission.instanceId),
    attachmentFileNames: [] as string[],
    resolveAttachment: async (fileName: string) => {
      throw new Error(`Attachment edit loading is not enabled for ${fileName}.`);
    },
  };
});

function formatDate(value?: string): string {
  if (!value) {
    return 'Not recorded';
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatTime(value?: string): string {
  if (!value) {
    return 'not recorded';
  }
  return new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function formatStatus(value?: number): string {
  if (value === 100000001) {
    return 'Submitted';
  }
  if (value === 100000000) {
    return 'Draft';
  }
  return value == null ? 'Submitted' : `Status ${value}`;
}

function formatContactState(value: AccessUserSummary['contactState']): string {
  if (value === 'active') {
    return 'Contact active';
  }
  if (value === 'missing') {
    return 'Contact not found';
  }
  return 'Contact check unavailable';
}

function contactStateTone(value: AccessUserSummary['contactState']): string {
  if (value === 'active') {
    return 'success';
  }
  if (value === 'missing') {
    return 'warning';
  }
  return 'neutral';
}

function accessStatusTone(value: AccessUserSummary['accessStatus']): string {
  if (value === 'Active') return 'success';
  if (value === 'Needs contact check') return 'warning';
  return 'neutral';
}

function formatSystemHealthStatus(value: SystemHealthItem['status']): string {
  if (value === 'healthy') return 'Healthy';
  if (value === 'pending') return 'Pending';
  if (value === 'degraded') return 'Degraded';
  if (value === 'blocked') return 'Blocked';
  return 'Not configured';
}

function systemHealthTone(value: SystemHealthItem['status']): string {
  if (value === 'healthy') return 'success';
  if (value === 'pending' || value === 'not-configured') return 'neutral';
  return 'warning';
}

function systemActivityTone(value: SystemActivityEvent['severity']): string {
  if (value === 'success') return 'success';
  if (value === 'warning' || value === 'error') return 'warning';
  return 'neutral';
}

function formatActivationState(value: UserActivationDiagnostic['contactStatus']): string {
  if (value === 'ready') return 'Ready';
  if (value === 'pending') return 'Pending';
  if (value === 'missing') return 'Missing';
  if (value === 'review') return 'Review';
  return 'Unavailable';
}

function activationStateTone(value: UserActivationDiagnostic['contactStatus']): string {
  if (value === 'ready') return 'success';
  if (value === 'pending' || value === 'missing' || value === 'review') return 'warning';
  return 'neutral';
}

function nextActionTone(value: UserActivationDiagnostic['nextAction']): string {
  if (value === 'Ready') return 'success';
  if (value === 'Await redemption' || value === 'Send code') return 'warning';
  return 'neutral';
}

function formatReviewState(value?: number): string {
  if (value === 100000000) return 'Received';
  if (value === 100000001) return 'Edited';
  if (value === 100000002) return 'Has issues';
  if (value === 100000003) return 'Rejected';
  if (value === 100000004) return 'Approved';
  return value == null ? 'Received' : `Review ${value}`;
}

function formatProjectionStatus(value?: number): string {
  if (value === 100000000) return 'Ready';
  if (value === 100000001) return 'Stale';
  if (value === 100000002) return 'Failed';
  return value == null ? 'Unknown' : `Projection ${value}`;
}

function formatAnswerValue(answer: SubmissionAnswerRow): string {
  if (answer.mp_valuetext) return answer.mp_valuetext;
  if (answer.mp_valuedecimal != null) return String(answer.mp_valuedecimal);
  if (answer.mp_valuedate) return formatDate(answer.mp_valuedate);
  if (answer.mp_valueboolean != null) return answer.mp_valueboolean ? 'Yes' : 'No';
  if (answer.mp_valuejson) return answer.mp_valuejson;
  return 'No value';
}

function isInsideOdkRuntime(target: EventTarget | null): boolean {
  return target instanceof Element && Boolean(target.closest('.odk-runtime-host'));
}

function preventPowerPagesFormSubmit(event: Event) {
  if (isInsideOdkRuntime(event.target)) {
    event.preventDefault();
  }
}

function preventRuntimeButtonDefault(event: MouseEvent) {
  const target = event.target;
  if (!(target instanceof Element)) {
    return;
  }

  const button = target.closest('button');
  if (button && button.closest('.odk-runtime-host')) {
    const label = button.textContent?.replace(/\s+/g, ' ').trim() || 'ODK runtime button';
    runtimeClickStatus.value = `${new Date().toLocaleTimeString()} - ${label} click captured by host boundary.`;
    event.preventDefault();
  }
}

function relabelOdkSubmitButton() {
  const submitButtons = document.querySelectorAll<HTMLButtonElement>('.odk-runtime-host .footer button');
  submitButtons.forEach((button) => {
    if (button.textContent?.replace(/\s+/g, ' ').trim() !== 'Send') {
      return;
    }

    const label = button.querySelector<HTMLElement>('.p-button-label') ?? button;
    label.textContent = 'Submit';
    button.setAttribute('aria-label', 'Submit');
  });
}

function focusFirstRuntimeError() {
  const runtime = document.querySelector<HTMLElement>('.odk-runtime-host');
  if (!runtime) {
    return;
  }

  const errorSelectors = [
    '[aria-invalid="true"]',
    '.p-invalid',
    '.invalid',
    '.is-invalid',
    '[data-invalid="true"]',
    '[data-p-invalid="true"]',
    '.error',
    '.error-message',
  ];
  const errorElement = errorSelectors
    .map((selector) => runtime.querySelector<HTMLElement>(selector))
    .find((element) => element && element.offsetParent !== null);
  if (!errorElement) {
    return;
  }

  const fieldContainer = errorElement.closest<HTMLElement>('.question, .field, .form-field, .p-field, .p-component, label, div') ?? errorElement;
  const focusable = fieldContainer.querySelector<HTMLElement>(
    'input:not([type="hidden"]):not([disabled]), textarea:not([disabled]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])',
  ) ?? (errorElement.matches('input, textarea, select, button, [tabindex]:not([tabindex="-1"])') ? errorElement : null);

  fieldContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
  window.setTimeout(() => {
    focusable?.focus({ preventScroll: true });
  }, 180);
}

async function focusFirstRuntimeErrorAfterRender() {
  await nextTick();
  window.setTimeout(focusFirstRuntimeError, 80);
}

function resetRuntimeDiagnostics(assignment: FormAssignmentSummary) {
  clearRuntimeFallbackTimer();
  runtimeStatus.value = selectedEditSubmission.value
    ? 'Loading form definition for edit...'
    : 'Loading form definition...';
  submitStatus.value = '';
  submitTone.value = 'neutral';
  formRuntimeLoading.value = true;
  formRuntimeMountReady.value = false;
  runtimeClickStatus.value = 'No ODK runtime button click observed for this selected form.';
  odkSubmitEventStatus.value = 'No ODK submit event observed for this selected form.';
  dataverseWriteStatus.value = 'No Dataverse submit write attempted for this selected form.';
  selectedAssignment.value = getWarmAssignment(assignment);
}

function getWarmAssignment(assignment: FormAssignmentSummary): FormAssignmentSummary {
  return warmedAssignments.get(assignment.formVersionId) ?? assignment;
}

function rememberWarmAssignment(assignment: FormAssignmentSummary) {
  if (assignment.xformXml) {
    warmedAssignments.set(assignment.formVersionId, assignment);
  }
}

function clearRunnerMountState() {
  clearRuntimeFallbackTimer();
  formRuntimeLoading.value = false;
  formRuntimeMountReady.value = false;
}

function clearRuntimeFallbackTimer() {
  if (formRuntimeFallbackTimer !== null) {
    window.clearTimeout(formRuntimeFallbackTimer);
    formRuntimeFallbackTimer = null;
  }
}

function startRuntimeMountFallback(formVersionId: string) {
  clearRuntimeFallbackTimer();
  formRuntimeFallbackTimer = window.setTimeout(() => {
    formRuntimeFallbackTimer = null;
    if (activeView.value !== 'runner' || selectedAssignment.value?.formVersionId !== formVersionId || !formRuntimeMountReady.value) {
      return;
    }
    if (formRuntimeLoading.value) {
      formRuntimeLoading.value = false;
      runtimeStatus.value = 'Form runtime mounted. Continue if the form is visible; refresh only if questions do not appear.';
    }
  }, 8000);
}

async function prepareRuntimeMount() {
  await nextTick();
  const formVersionId = selectedAssignment.value?.formVersionId;
  window.setTimeout(() => {
    formRuntimeMountReady.value = true;
    if (formVersionId) {
      startRuntimeMountFallback(formVersionId);
    }
  }, 180);
}

function openProject(project: ProjectWorkspace) {
  selectedProjectId.value = project.id;
  selectedAssignment.value = project.assignments[0] ? getWarmAssignment(project.assignments[0]) : null;
  activeFormSection.value = 'summary';
  postSubmitMessage.value = '';
  activeView.value = 'records';
  mobileNavOpen.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openProjectSection(project: ProjectWorkspace, section: FormSection) {
  openProject(project);
  void selectFormSection(section);
}

async function selectFormSection(section: FormSection) {
  activeFormSection.value = section;
  if (section === 'data') {
    await loadReportingData();
  } else if (section === 'exports') {
    refreshExportName();
    await loadExportSettings();
  }
}

function openDashboard() {
  postSubmitMessage.value = '';
  accessRouteDenied.value = false;
  activeView.value = 'dashboard';
  mobileNavOpen.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openWorkspace() {
  postSubmitMessage.value = '';
  accessRouteDenied.value = false;
  activeView.value = 'workspace';
  mobileNavOpen.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function backToProjects() {
  postSubmitMessage.value = '';
  activeView.value = 'projects';
  mobileNavOpen.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openBeneficiaries(options: { preserveHash?: boolean } = {}) {
  postSubmitMessage.value = '';
  accessRouteDenied.value = false;
  activeView.value = 'beneficiaries';
  mobileNavOpen.value = false;
  if (!options.preserveHash) {
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#/beneficiaries`);
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function openReporting() {
  activeView.value = 'reporting';
  mobileNavOpen.value = false;
  if (primaryAssignment.value) {
    selectedAssignment.value = getWarmAssignment(primaryAssignment.value);
    await loadReportingData();
  }
  await loadExportSettings();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function openAccessManagement() {
  accessRouteDenied.value = !canManageAccess.value;
  activeView.value = 'access';
  activeAccessSection.value = canManageAccess.value ? 'users' : 'configuration';
  selectedAccessUser.value = null;
  selectedAccessAction.value = null;
  accessWorkflowOpen.value = false;
  mobileNavOpen.value = false;
  if (!canManageAccess.value) {
    accessUsers.value = [];
    accessError.value = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  await Promise.all([loadAccessUsers(), loadActivationDiagnostics(), loadNotificationDeliverySetting()]);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function openSystemActivity() {
  accessRouteDenied.value = !canManageAccess.value;
  activeView.value = 'system-activity';
  activeSystemActivitySection.value = 'health';
  mobileNavOpen.value = false;
  if (!canManageAccess.value) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  await Promise.all([loadAccessUsers(), loadActivationDiagnostics(), loadNotificationDeliverySetting()]);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openRoadmapModule(moduleName: string) {
  selectedRoadmapModule.value = moduleName;
  activeView.value = 'roadmap';
  mobileNavOpen.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setSystemActivitySection(section: SystemActivitySection) {
  activeSystemActivitySection.value = section;
}

function routeIntentFromHash(): RouteIntent | null {
  const route = window.location.hash.replace(/^#\/?/, '').split('?')[0].split('/')[0].trim().toLowerCase();
  if (route === 'system-activity' || route === 'activity') {
    return 'system-activity';
  }
  if (route === 'beneficiaries') {
    return 'beneficiaries';
  }
  if (route === 'dashboard' || route === 'projects' || route === 'reporting' || route === 'access') {
    return route;
  }
  return null;
}

async function applyRouteIntent(intent: RouteIntent | null) {
  if (intent === 'system-activity') {
    await openSystemActivity();
    return;
  }
  if (intent === 'access') {
    await openAccessManagement();
    return;
  }
  if (intent === 'reporting') {
    await openReporting();
    return;
  }
  if (intent === 'projects') {
    backToProjects();
    return;
  }
  if (intent === 'beneficiaries') {
    openBeneficiaries({ preserveHash: true });
    return;
  }
  if (intent === 'dashboard') {
    openDashboard();
  }
}

function handleHashRouteChange() {
  void applyRouteIntent(routeIntentFromHash());
}

function toggleShellNav() {
  shellNavCollapsed.value = !shellNavCollapsed.value;
}

function toggleShellSwitcher() {
  if (window.matchMedia('(max-width: 760px)').matches) {
    mobileNavOpen.value = !mobileNavOpen.value;
    return;
  }
  toggleShellNav();
}

function closeMobileNav() {
  mobileNavOpen.value = false;
}

async function openReportingDestination() {
  await openReporting();
}

async function loadAccessUsers() {
  if (!canManageAccess.value) {
    accessUsers.value = [];
    accessError.value = 'You do not have access to User & Access.';
    return;
  }

  accessLoading.value = true;
  accessError.value = '';
  try {
    accessUsers.value = await api.listAccessUsers();
  } catch (caught) {
    accessUsers.value = [];
    accessError.value = caught instanceof Error ? caught.message : 'Unable to load users and access.';
  } finally {
    accessLoading.value = false;
  }
}

async function loadActivationDiagnostics() {
  if (!canManageAccess.value) {
    activationDiagnostics.value = [];
    activationDiagnosticsError.value = 'You do not have access to activation diagnostics.';
    return;
  }

  activationDiagnosticsLoading.value = true;
  activationDiagnosticsError.value = '';
  try {
    activationDiagnostics.value = await api.listUserActivationDiagnostics();
  } catch (caught) {
    activationDiagnostics.value = [];
    activationDiagnosticsError.value = caught instanceof Error ? caught.message : 'Unable to load activation diagnostics.';
  } finally {
    activationDiagnosticsLoading.value = false;
  }
}

async function refreshAccessManagement() {
  await Promise.all([loadAccessUsers(), loadActivationDiagnostics()]);
}

function applyNotificationDeliverySetting(setting: NotificationDeliverySetting) {
  notificationSetting.value = setting;
  notificationDeliveryMode.value = setting.deliveryMode;
  notificationSenderMailbox.value = setting.senderMailbox ?? '';
  notificationMailboxStatus.value = setting.mailboxStatus;
  notificationWorkflowId.value = setting.nativeInvitationWorkflowId ?? '';
  notificationLastTestResult.value = setting.lastTestResult ?? '';
  notificationInstructions.value = setting.instructions ?? '';
}

async function loadNotificationDeliverySetting() {
  notificationLoading.value = true;
  notificationError.value = '';
  notificationMessage.value = '';
  try {
    applyNotificationDeliverySetting(await api.getNotificationDeliverySetting());
  } catch (caught) {
    notificationError.value = caught instanceof Error ? caught.message : 'Unable to load notification settings.';
  } finally {
    notificationLoading.value = false;
  }
}

async function saveNotificationDeliverySetting() {
  notificationError.value = '';
  notificationMessage.value = '';
  if (!notificationCanSave.value) {
    notificationError.value = 'Email delivery requires a sender mailbox with Tested and enabled status.';
    return;
  }
  notificationSaving.value = true;
  try {
    const saved = await api.saveNotificationDeliverySetting({
      deliveryMode: notificationDeliveryMode.value,
      senderMailbox: notificationSenderMailbox.value,
      mailboxStatus: notificationMailboxStatus.value,
      nativeInvitationWorkflowId: notificationWorkflowId.value,
      lastTestResult: notificationLastTestResult.value,
      instructions: notificationInstructions.value,
    }, notificationSetting.value?.id);
    applyNotificationDeliverySetting(saved);
    notificationMessage.value = notificationDeliveryMode.value === 'email'
      ? 'Mailbox email delivery configuration saved.'
      : 'Manual invitation code delivery configuration saved.';
  } catch (caught) {
    notificationError.value = caught instanceof Error ? caught.message : 'Unable to save notification settings.';
  } finally {
    notificationSaving.value = false;
  }
}

function openAccessUser(user: AccessUserSummary) {
  selectedAccessUser.value = user;
  selectedAccessAction.value = null;
}

function openResendInvitationWorkflow(user: AccessUserSummary) {
  const firstAssignment = user.assignments[0];
  const project = projectWorkspaces.value.find((candidate) => (
    firstAssignment
      ? candidate.assignments.some((assignment) => assignment.formVersionId === firstAssignment.formVersionId)
      : candidate.assignments.some((assignment) => user.assignments.some((userAssignment) => userAssignment.formVersionId === assignment.formVersionId))
  )) ?? projectWorkspaces.value[0] ?? null;
  const availableFormVersionIds = new Set(project?.assignments.map((assignment) => assignment.formVersionId) ?? []);
  const assignedFormVersionIds = user.assignments
    .map((assignment) => assignment.formVersionId)
    .filter((formVersionId) => availableFormVersionIds.has(formVersionId));

  selectedAccessUser.value = null;
  selectedAccessAction.value = null;
  clearAccessWorkflowOutcome();
  activeAccessSection.value = 'add';
  accessWorkflowOpen.value = true;
  accessWorkflowStep.value = 4;
  accessWorkflowFullName.value = user.name;
  accessWorkflowEmail.value = user.email;
  accessWorkflowRole.value = user.role;
  accessWorkflowProjectId.value = project?.id ?? '';
  accessWorkflowFormVersionIds.value = assignedFormVersionIds.length > 0
    ? assignedFormVersionIds
    : project?.assignments.map((assignment) => assignment.formVersionId) ?? [];
  accessWorkflowReason.value = `Reissue invitation for ${user.email} from User & Access.`;
  accessWorkflowSubmitMessage.value = '';
  accessWorkflowSubmitError.value = '';
  accessWorkflowSubmitResults.value = [];
  accessWorkflowOnboardingResult.value = null;
  invitationCopyStatus.value = '';
  accessWorkflowReplacementOfRequestId.value = '';
  accessWorkflowForceInvitation.value = true;
}

function closeAccessUser() {
  selectedAccessUser.value = null;
  selectedAccessAction.value = null;
  accessChangeEmail.value = '';
  accessChangeReason.value = '';
  accessChangeMessage.value = '';
  accessChangeError.value = '';
}

function openAccessChangeAction(action: AccessChangeAction) {
  if (!selectedAccessUser.value) return;
  selectedAccessAction.value = action;
  accessChangeRole.value = selectedAccessUser.value.role;
  accessChangeEmail.value = selectedAccessUser.value.email;
  accessChangeReason.value = '';
  accessChangeMessage.value = '';
  accessChangeError.value = '';
}

function closeAccessChangeAction() {
  selectedAccessAction.value = null;
  accessChangeEmail.value = '';
  accessChangeReason.value = '';
  accessChangeMessage.value = '';
  accessChangeError.value = '';
}

function persistAccessWorkflowOutcome(outcome: AccessWorkflowOutcome | null) {
  accessWorkflowOutcome.value = outcome;
  try {
    if (outcome) {
      window.sessionStorage.setItem(ACCESS_WORKFLOW_OUTCOME_KEY, JSON.stringify(outcome));
    } else {
      window.sessionStorage.removeItem(ACCESS_WORKFLOW_OUTCOME_KEY);
    }
  } catch {
    // Session storage is best-effort feedback continuity only.
  }
}

function restoreAccessWorkflowOutcome(): boolean {
  try {
    const raw = window.sessionStorage.getItem(ACCESS_WORKFLOW_OUTCOME_KEY);
    if (!raw) return false;
    const parsed = JSON.parse(raw) as Partial<AccessWorkflowOutcome>;
    if (!parsed.title || !parsed.message || !parsed.occurredAt) return false;
    accessWorkflowOutcome.value = {
      tone: parsed.tone === 'success' || parsed.tone === 'error' || parsed.tone === 'warning' ? parsed.tone : 'warning',
      title: String(parsed.title),
      message: String(parsed.message),
      details: Array.isArray(parsed.details) ? parsed.details.map(String) : [],
      email: parsed.email ? String(parsed.email) : undefined,
      occurredAt: String(parsed.occurredAt),
    };
    if (accessWorkflowOutcome.value.tone === 'warning') {
      activeView.value = 'access';
      activeAccessSection.value = 'add';
      accessWorkflowOpen.value = true;
      accessWorkflowStep.value = 4;
    }
    return true;
  } catch {
    return false;
  }
}

function clearAccessWorkflowOutcome() {
  persistAccessWorkflowOutcome(null);
}

function setAccessSection(section: AccessSection) {
  activeAccessSection.value = section;
  if (section !== 'users') {
    selectedAccessUser.value = null;
    selectedAccessAction.value = null;
  }
  if (section === 'add' && !accessWorkflowOpen.value) {
    openAccessWorkflow();
  }
}

function openAccessWorkflow() {
  selectedAccessUser.value = null;
  selectedAccessAction.value = null;
  clearAccessWorkflowOutcome();
  activeAccessSection.value = 'add';
  accessWorkflowOpen.value = true;
  accessWorkflowStep.value = 1;
  accessWorkflowFullName.value = '';
  accessWorkflowEmail.value = '';
  accessWorkflowRole.value = 'Data Collector / Bank Officer';
  accessWorkflowProjectId.value = projectWorkspaces.value[0]?.id ?? '';
  accessWorkflowFormVersionIds.value = projectWorkspaces.value[0]?.assignments.map((assignment) => assignment.formVersionId) ?? [];
  accessWorkflowReason.value = '';
  accessWorkflowSubmitMessage.value = '';
  accessWorkflowSubmitError.value = '';
  accessWorkflowSubmitResults.value = [];
  accessWorkflowOnboardingResult.value = null;
  invitationCopyStatus.value = '';
  accessWorkflowReplacementOfRequestId.value = '';
  accessWorkflowForceInvitation.value = false;
}

function closeAccessWorkflow() {
  accessWorkflowOpen.value = false;
  accessWorkflowSubmitting.value = false;
  accessWorkflowSubmitMessage.value = '';
  accessWorkflowSubmitError.value = '';
  accessWorkflowSubmitResults.value = [];
  accessWorkflowOnboardingResult.value = null;
  invitationCopyStatus.value = '';
  accessWorkflowReplacementOfRequestId.value = '';
  accessWorkflowForceInvitation.value = false;
}

const manualInvitationAvailable = computed(() => Boolean(
  accessWorkflowOnboardingResult.value?.invitationCode
  && accessWorkflowOnboardingResult.value?.invitationRedeemUrl,
));
const manualInvitationExpired = computed(() => {
  const result = accessWorkflowOnboardingResult.value;
  if (!result) return false;
  if (result.invitationStatus === 'Expired') return true;
  if (!result.invitationExpiresAt) return false;
  return new Date(result.invitationExpiresAt).getTime() <= Date.now();
});
const onboardingResultTone = computed(() => {
  const status = accessWorkflowOnboardingResult.value?.queueStatus;
  if (status === 'Failed' || status === 'Cancelled') return 'error';
  if (status === 'Completed') return 'success';
  return 'warning';
});
const onboardingResultTitle = computed(() => {
  const result = accessWorkflowOnboardingResult.value;
  if (!result) return 'Onboarding request';
  if (result.queueStatus === 'Failed') return 'Onboarding failed';
  if (result.queueStatus === 'Completed') return 'Onboarding completed';
  if (manualInvitationAvailable.value && !manualInvitationExpired.value) return 'Invitation ready';
  if (manualInvitationExpired.value) return 'Invitation expired';
  if (result.queueStatus === 'Processing') return 'Processor running';
  return 'Needs administrator review';
});
const onboardingPrimaryInstruction = computed(() => {
  const result = accessWorkflowOnboardingResult.value;
  if (!result) return '';
  if (result.queueStatus === 'Failed') return result.emailMessage || 'Review the processor run history before retrying.';
  if (manualInvitationExpired.value) return 'Create a replacement invitation before contacting the user.';
  if (manualInvitationAvailable.value) return 'Share the redeem link and code only through an approved internal channel.';
  if (result.requestType === 'NewUser') return 'Refresh status until the invitation code and redeem link are available.';
  return result.emailMessage || 'Refresh status to confirm assignment notification state.';
});
const onboardingTimeline = computed<OnboardingTimelineItem[]>(() => {
  const status = accessWorkflowOnboardingResult.value?.queueStatus;
  const failed = status === 'Failed' || status === 'Cancelled';
  const processing = status === 'Processing';
  const review = status === 'NeedsReview' || status === 'Completed';
  return [
    {
      id: 'queued',
      label: 'Queued',
      state: failed || processing || review || status === 'Pending' ? 'done' : 'active',
    },
    {
      id: 'processing',
      label: 'Processing',
      state: failed ? 'failed' : processing ? 'active' : review ? 'done' : 'waiting',
    },
    {
      id: 'review',
      label: status === 'Completed' ? 'Complete' : 'Needs review',
      state: failed ? 'failed' : review ? 'active' : 'waiting',
    },
  ];
});
const onboardingTechnicalSummary = computed(() => {
  const result = accessWorkflowOnboardingResult.value;
  if (!result) return [];
  return [
    ['Request id', result.requestId],
    ['Queue status', result.queueStatus],
    ['Delivery path', result.emailDelivery],
    ['Queue record', result.queueRecordId],
  ].filter((item): item is [string, string] => Boolean(item[1]));
});

async function copyInvitationFallback(field: InvitationCopyField) {
  const result = accessWorkflowOnboardingResult.value;
  const value = field === 'code' ? result?.invitationCode : result?.invitationRedeemUrl;
  if (!value) {
    invitationCopyStatus.value = 'Nothing to copy yet.';
    return;
  }
  try {
    await navigator.clipboard.writeText(value);
    invitationCopyStatus.value = field === 'code' ? 'Invitation code copied.' : 'Redeem URL copied.';
  } catch {
    invitationCopyStatus.value = 'Copy was blocked. Select the value manually.';
  }
}

async function refreshOnboardingRequestResult() {
  const result = accessWorkflowOnboardingResult.value;
  if (!result) return;
  accessWorkflowSubmitError.value = '';
  accessWorkflowSubmitMessage.value = 'Refreshing onboarding request status.';
  try {
    const refreshed = await api.getUserOnboardingRequestResult(result.queueRecordId);
    accessWorkflowOnboardingResult.value = refreshed;
    accessWorkflowSubmitMessage.value = `Request ${refreshed.requestId} is ${refreshed.queueStatus}. ${refreshed.emailMessage}`;
  } catch (caught) {
    accessWorkflowSubmitError.value = caught instanceof Error ? caught.message : 'Unable to refresh onboarding request.';
  }
}

async function recreateExpiredInvitation() {
  const result = accessWorkflowOnboardingResult.value;
  if (!result) return;
  accessWorkflowReplacementOfRequestId.value = result.requestId;
  accessWorkflowReason.value = `${accessWorkflowReason.value.trim() || 'Approved access request'}; replacement for expired invitation ${result.requestId}`;
  accessWorkflowSubmitMessage.value = 'Creating replacement invitation request.';
  accessWorkflowSubmitError.value = '';
  await submitAccessWorkflow();
}

function setAccessWorkflowStep(step: number) {
  accessWorkflowStep.value = Math.min(Math.max(step, 1), accessWorkflowSteps.length);
}

function nextAccessWorkflowStep() {
  if (!accessWorkflowCanProceed.value) return;
  setAccessWorkflowStep(accessWorkflowStep.value + 1);
}

function previousAccessWorkflowStep() {
  setAccessWorkflowStep(accessWorkflowStep.value - 1);
}

async function submitAccessWorkflow() {
  if (!accessWorkflowCanSubmit.value) {
    accessWorkflowSubmitError.value = userOnboardingReadiness.value.enabled
      ? 'Complete the user, project, forms, and business reason before creating access.'
      : userOnboardingReadiness.value.disabledReason;
    persistAccessWorkflowOutcome({
      tone: 'error',
      title: 'Create, invite and assign was not submitted',
      message: accessWorkflowSubmitError.value,
      details: ['No contact, assignment, invitation, or notification write was attempted.'],
      email: accessWorkflowEmailNormalized.value || undefined,
      occurredAt: new Date().toISOString(),
    });
    return;
  }

  accessWorkflowSubmitting.value = true;
  accessWorkflowSubmitError.value = '';
  accessWorkflowSubmitMessage.value = '';
  accessWorkflowSubmitResults.value = [];
  accessWorkflowOnboardingResult.value = null;
  const pendingEmail = accessWorkflowEmailNormalized.value;
  persistAccessWorkflowOutcome({
    tone: 'warning',
    title: 'Create, invite and assign is waiting for confirmation',
    message: 'The request was submitted, but the portal has not received a confirmed result yet.',
    details: [
      'Queue status will appear after the request is created.',
      'Verify Dataverse before retrying if the page reloads.',
    ],
    email: pendingEmail,
    occurredAt: new Date().toISOString(),
  });

  try {
    const result = await api.submitUserOnboardingAccess({
      fullName: accessWorkflowFullName.value.trim(),
      affectedEmail: accessWorkflowEmailNormalized.value,
      targetRole: accessWorkflowRole.value,
      requestType: accessWorkflowOnboardingMode.value === 'existing' ? 'ExistingUser' : 'NewUser',
      projectId: accessWorkflowSelectedProject.value?.id,
      projectName: accessWorkflowSelectedProject.value?.name,
      reason: accessWorkflowReason.value.trim(),
      sourceRoute: 'UserAccess:AddUser',
      replacementOfRequestId: accessWorkflowReplacementOfRequestId.value || undefined,
      forms: accessWorkflowSelectedForms.value.map((assignment) => ({
        formId: assignment.formId,
        formName: assignment.formName,
        formVersionId: assignment.formVersionId,
      })),
    });
    accessWorkflowOnboardingResult.value = result;
    accessWorkflowSubmitResults.value = result.assignmentResults;
    accessWorkflowSubmitMessage.value = `Onboarding request ${result.requestId} was queued for ${accessWorkflowSelectedForms.value.length} form${accessWorkflowSelectedForms.value.length === 1 ? '' : 's'}. ${result.emailMessage}`;
    persistAccessWorkflowOutcome({
      tone: 'warning',
      title: 'Onboarding request queued',
      message: accessWorkflowSubmitMessage.value,
      details: [
        `Request id: ${result.requestId}`,
        `Status: ${result.queueStatus}`,
        `Delivery: ${result.emailDelivery}`,
        'Server processor handles contact, audit, assignment, and invitation records.',
      ],
      email: pendingEmail,
      occurredAt: new Date().toISOString(),
    });
    accessWorkflowOpen.value = true;
    accessWorkflowStep.value = 4;
    activeAccessSection.value = 'add';
    await refreshAccessManagement();
    await nextTick();
    document.getElementById('access-onboarding-outcome')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (caught) {
    accessWorkflowSubmitError.value = caught instanceof Error ? caught.message : 'Unable to create access.';
    persistAccessWorkflowOutcome({
      tone: 'error',
      title: 'Create, invite and assign failed',
      message: accessWorkflowSubmitError.value,
      details: [
        'No confirmed onboarding queue result was returned.',
        'Check Power Automate run history before retrying.',
      ],
      email: pendingEmail,
      occurredAt: new Date().toISOString(),
    });
    accessWorkflowOpen.value = true;
    accessWorkflowStep.value = 4;
    activeAccessSection.value = 'add';
  } finally {
    accessWorkflowSubmitting.value = false;
  }
}

function selectAccessWorkflowProject(projectId: string) {
  accessWorkflowProjectId.value = projectId;
  const project = projectWorkspaces.value.find((candidate) => candidate.id === projectId);
  accessWorkflowFormVersionIds.value = project?.assignments.map((assignment) => assignment.formVersionId) ?? [];
}

function handleAccessWorkflowProjectChange(event: Event) {
  const target = event.target;
  if (target instanceof HTMLSelectElement) {
    selectAccessWorkflowProject(target.value);
  }
}

function toggleAccessWorkflowForm(formVersionId: string) {
  const current = new Set(accessWorkflowFormVersionIds.value);
  if (current.has(formVersionId)) {
    current.delete(formVersionId);
  } else {
    current.add(formVersionId);
  }
  accessWorkflowFormVersionIds.value = [...current];
}

function buildSelectedAccessWriteCommand(): AccessWriteCommand | null {
  if (!selectedAccessUser.value || !selectedAccessAction.value) {
    return null;
  }

  const action = selectedAccessAction.value === 'role'
    ? 'ChangeRole'
    : selectedAccessAction.value === 'email'
      ? 'CorrectEmail'
    : selectedAccessAction.value === 'suspend'
      ? 'RemoveAssignment'
      : 'ReactivateAccess';
  const nextStatus = selectedAccessAction.value === 'suspend' ? 'Inactive' : 'Active';
  const reason = accessChangeReason.value.trim() || 'Pending administrator reason before activation';

  return {
    action,
    affectedEmail: selectedAccessUser.value.email,
    targetRole: selectedAccessAction.value === 'role' ? accessChangeRole.value : selectedAccessUser.value.role,
    scopeType: selectedAccessUser.value.assignments[0]?.assignmentId ? 'Assignment' : 'Project',
    reason,
    sourceRoute: `UserAccess:${accessChangeActionLabel.value.replace(/\s+/g, '')}`,
    projectId: selectedProject.value?.id,
    formId: selectedAccessUser.value.assignments[0]?.formId,
    formVersionId: selectedAccessUser.value.assignments[0]?.formVersionId,
    formAssignmentId: selectedAccessUser.value.assignments[0]?.assignmentId,
    previousState: {
      userEmail: selectedAccessUser.value.email,
      contactId: selectedAccessUser.value.contactId,
      role: selectedAccessUser.value.role,
      status: selectedAccessUser.value.accessStatus,
      projectId: selectedProject.value?.id,
      projectName: selectedProject.value?.name,
      formId: selectedAccessUser.value.assignments[0]?.formId,
      formName: selectedAccessUser.value.assignments[0]?.formName,
      formVersionId: selectedAccessUser.value.assignments[0]?.formVersionId,
      assignmentId: selectedAccessUser.value.assignments[0]?.assignmentId,
    },
    newState: {
      userEmail: selectedAccessAction.value === 'email' ? accessChangeEmailNormalized.value : selectedAccessUser.value.email,
      contactId: selectedAccessUser.value.contactId,
      role: selectedAccessAction.value === 'role' ? accessChangeRole.value : selectedAccessUser.value.role,
      status: selectedAccessAction.value === 'role' || selectedAccessAction.value === 'email' ? selectedAccessUser.value.accessStatus : nextStatus,
      projectId: selectedProject.value?.id,
      projectName: selectedProject.value?.name,
      formId: selectedAccessUser.value.assignments[0]?.formId,
      formName: selectedAccessUser.value.assignments[0]?.formName,
      formVersionId: selectedAccessUser.value.assignments[0]?.formVersionId,
      assignmentId: selectedAccessUser.value.assignments[0]?.assignmentId,
    },
  };
}

async function applySelectedAccessChange() {
  if (!selectedAccessUser.value || !selectedAccessAction.value) return;
  accessChangeError.value = '';
  accessChangeMessage.value = '';
  if (!accessChangeCanApply.value) {
    accessChangeError.value = accessWriteReadiness.value.enabled
      ? 'Enter the required details and business reason before applying this change.'
      : accessWriteReadiness.value.disabledReason;
    return;
  }

  accessChangeSubmitting.value = true;
  try {
    const action = selectedAccessAction.value === 'email' ? 'CorrectEmail' : 'DeactivateAccess';
    const result = await api.submitManageAccessUser({
      action,
      user: selectedAccessUser.value,
      newEmail: selectedAccessAction.value === 'email' ? accessChangeEmailNormalized.value : undefined,
      reason: accessChangeReason.value.trim(),
      sourceRoute: `UserAccess:${accessChangeActionLabel.value.replace(/\s+/g, '')}`,
    });
    accessChangeMessage.value = action === 'CorrectEmail'
      ? `Email updated to ${result.newEmail}; ${result.updatedAssignments} assignment row${result.updatedAssignments === 1 ? '' : 's'} corrected.`
      : `${result.updatedAssignments} assignment row${result.updatedAssignments === 1 ? '' : 's'} deactivated.`;
    await refreshAccessManagement();
    const refreshedEmail = result.newEmail ?? result.affectedEmail;
    selectedAccessUser.value = accessUsers.value.find((user) => user.email.toLowerCase() === refreshedEmail.toLowerCase()) ?? null;
    selectedAccessAction.value = null;
    accessChangeReason.value = '';
  } catch (caught) {
    accessChangeError.value = caught instanceof Error ? caught.message : 'Unable to apply access change.';
  } finally {
    accessChangeSubmitting.value = false;
  }
}

function buildSafeAccessWritePreview(command: AccessWriteCommand): AccessWritePreview | null {
  try {
    return api.buildAccessWritePreview(command);
  } catch {
    return null;
  }
}

function formatAccessPreviewJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

async function openRunner(assignment = primaryAssignment.value) {
  if (!assignment) {
    error.value = 'No assigned form is available for this project.';
    return;
  }
  selectedEditSubmission.value = null;
  postSubmitMessage.value = '';
  const warmAssignment = getWarmAssignment(assignment);
  const canReuseWarmRuntime = Boolean(warmAssignment.xformXml)
    && selectedAssignment.value?.formVersionId === warmAssignment.formVersionId
    && !selectedEditSubmission.value;
  selectedAssignment.value = warmAssignment;
  activeView.value = 'runner';
  mobileNavOpen.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (canReuseWarmRuntime) {
    formRuntimeLoading.value = false;
    formRuntimeMountReady.value = true;
    runtimeStatus.value = '';
    submitStatus.value = '';
    submitTone.value = 'neutral';
    return;
  }

  resetRuntimeDiagnostics(warmAssignment);
  try {
    const hydrated = await api.hydrateAssignmentRuntime(warmAssignment);
    if (selectedAssignment.value?.formVersionId === warmAssignment.formVersionId) {
      runtimeStatus.value = 'Preparing form runtime...';
      rememberWarmAssignment(hydrated);
      selectedAssignment.value = hydrated;
      await prepareRuntimeMount();
    }
  } catch (caught) {
    clearRunnerMountState();
    runtimeStatus.value = '';
    submitStatus.value = caught instanceof Error ? `Unable to load form: ${caught.message}` : 'Unable to load form.';
    submitTone.value = 'error';
  }
}

async function openSavedSubmission(submission: SubmissionSummary) {
  loading.value = true;
  workspaceHydrating.value = true;
  error.value = '';
  postSubmitMessage.value = '';
  try {
    selectedEditSubmission.value = submission;
    const context = await api.getSubmissionFormContext(submission);
    resetRuntimeDiagnostics(context);
    activeView.value = 'runner';
    mobileNavOpen.value = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    void prepareRuntimeMount();
  } catch (caught) {
    selectedEditSubmission.value = null;
    clearRunnerMountState();
    error.value = caught instanceof Error ? caught.message : 'Unable to open saved record for editing.';
  } finally {
    loading.value = false;
    workspaceHydrating.value = false;
  }
}

async function changePage(direction: -1 | 1) {
  await setActivePage(activeRecordPage.value + direction);
}

async function setActivePage(page: number) {
  const nextPage = Math.min(Math.max(1, page), activeTotalPages.value);
  savedPage.value = nextPage;
  await loadReportingData();
}

function clampActivePage() {
  const nextPage = Math.min(Math.max(1, activeRecordPage.value), activeTotalPages.value);
  if (nextPage !== savedPage.value) {
    savedPage.value = nextPage;
    void loadReportingData();
  }
}

async function loadReportingData() {
  if (!selectedAssignment.value) {
    reportRows.value = [];
    reportTotal.value = 0;
    return;
  }

  reportLoading.value = true;
  reportError.value = '';
  try {
    const result = await api.listSubmissionReportRows({
      page: savedPage.value,
      pageSize,
      filters: activeReportFilters.value,
    });
    reportRows.value = result.rows;
    reportTotal.value = result.total;
  } catch (caught) {
    reportRows.value = [];
    reportTotal.value = 0;
    reportError.value = caught instanceof Error ? caught.message : 'Unable to load reporting data.';
  } finally {
    reportLoading.value = false;
  }
}

function clearReportFilters() {
  recordSearch.value = '';
  reportDateFrom.value = '';
  reportDateTo.value = '';
  reportSubmitter.value = '';
  reportReviewState.value = '';
  savedPage.value = 1;
  void loadReportingData();
}

async function openReportDetail(row: SubmissionReportRow) {
  selectedReportRow.value = row;
  reportAnswers.value = [];
  reportDetailError.value = '';
  reportDetailLoading.value = true;
  try {
    reportAnswers.value = await api.listSubmissionAnswers(row.mp_submissionreportrowid);
  } catch (caught) {
    reportDetailError.value = caught instanceof Error ? caught.message : 'Unable to load record answers.';
  } finally {
    reportDetailLoading.value = false;
  }
}

function closeReportDetail() {
  selectedReportRow.value = null;
  reportAnswers.value = [];
  reportDetailError.value = '';
}

async function editReportRow(row: SubmissionReportRow) {
  const submission = submissions.value.find((candidate) => candidate.instanceId === row.mp_instanceid);
  if (!submission) {
    reportError.value = 'The canonical submission for this reporting row is not available in the current workspace.';
    return;
  }
  await openSavedSubmission(submission);
}

async function loadExportSettings() {
  exportError.value = '';
  try {
    exportSettings.value = await api.listExportSettings();
  } catch (caught) {
    exportSettings.value = [];
    exportError.value = caught instanceof Error ? caught.message : 'Unable to load named exports.';
  }
}

function csvCell(value: unknown): string {
  const text = value == null ? '' : String(value);
  const spreadsheetSafe = /^[\t\r\n ]*[=+\-@]/.test(text) ? `'${text}` : text;
  return `"${spreadsheetSafe.replace(/"/g, '""')}"`;
}

function buildExportName(formName: string, now = new Date()): string {
  const safeFormName = formName
    .trim()
    .replace(/\s+/g, '_')
    .replace(/[<>:"/\\|?*\u0000-\u001F]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '') || 'Export';
  const iso = now.toISOString();
  const timestamp = `${iso.slice(0, 10).replaceAll('-', '')}_${iso.slice(11, 19).replaceAll(':', '')}`;
  return `${safeFormName}_${timestamp}`;
}

function refreshExportName() {
  exportName.value = buildExportName(selectedAssignment.value?.formName || 'Export');
}

function parseRootAnswers(raw?: string): Record<string, unknown> {
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed as Record<string, unknown> : {};
  } catch {
    return {};
  }
}

function downloadReportCsv(name: string, rows: SubmissionReportRow[], filters: ReportingFilters) {
  const generatedAt = new Date().toISOString();
  const answerColumns = [...new Set(rows.flatMap((row) => Object.keys(parseRootAnswers(row.mp_rootanswersjson))))].sort();
  const columns = [
    'export_name', 'generated_at', 'form_version_id', 'filters_json', 'record', 'instance_id', 'owner',
    'submitted_at', 'updated_at', 'version', 'lifecycle', 'review', 'projection_status', ...answerColumns,
  ];
  const lines = [columns.map(csvCell).join(',')];
  for (const row of rows) {
    const answers = parseRootAnswers(row.mp_rootanswersjson);
    const values: Record<string, unknown> = {
      export_name: name,
      generated_at: generatedAt,
      form_version_id: row._mp_formversion_value || selectedAssignment.value?.formVersionId,
      filters_json: JSON.stringify(filters),
      record: row.mp_displayname || row.mp_instanceid,
      instance_id: row.mp_instanceid,
      owner: row.mp_useremail,
      submitted_at: row.mp_submittedat,
      updated_at: row.mp_updatedat,
      version: row.mp_versionnumber,
      lifecycle: formatStatus(row.mp_lifecyclestatus),
      review: formatReviewState(row.mp_reviewstate),
      projection_status: formatProjectionStatus(row.mp_projectionstatus),
      ...answers,
    };
    lines.push(columns.map((column) => csvCell(values[column])).join(','));
  }

  const blob = new Blob([`\uFEFF${lines.join('\r\n')}`], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${name}.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

async function saveAndDownloadCsv() {
  exportLoading.value = true;
  exportError.value = '';
  exportMessage.value = '';
  try {
    const name = exportName.value.trim();
    await api.createCsvExportSetting({
      name,
      formVersionId: selectedAssignment.value?.formVersionId,
      filters: activeReportFilters.value,
    });
    const rows = await api.listAllSubmissionReportRows(activeReportFilters.value);
    downloadReportCsv(name, rows, activeReportFilters.value);
    exportMessage.value = `Saved and downloaded ${rows.length} ${reportingScopeLabel.value.toLowerCase()} reporting row${rows.length === 1 ? '' : 's'}.`;
    await loadExportSettings();
    refreshExportName();
  } catch (caught) {
    exportError.value = caught instanceof Error ? caught.message : 'Unable to generate the CSV export.';
  } finally {
    exportLoading.value = false;
  }
}

async function rerunExport(setting: ExportSettingRow) {
  exportLoading.value = true;
  exportError.value = '';
  exportMessage.value = '';
  try {
    const filters = setting.mp_filterjson ? JSON.parse(setting.mp_filterjson) as ReportingFilters : {};
    const rows = await api.listAllSubmissionReportRows(filters);
    downloadReportCsv(setting.mp_name, rows, filters);
    exportMessage.value = `Downloaded ${rows.length} ${reportingScopeLabel.value.toLowerCase()} reporting row${rows.length === 1 ? '' : 's'} using ${setting.mp_name}.`;
  } catch (caught) {
    exportError.value = caught instanceof Error ? caught.message : 'Unable to rerun this export.';
  } finally {
    exportLoading.value = false;
  }
}

async function copyPowerBiEnvironmentUrl() {
  try {
    await navigator.clipboard.writeText(powerBiEnvironmentUrl);
    powerBiCopyStatus.value = 'Environment URL copied.';
  } catch {
    powerBiCopyStatus.value = 'Copy was blocked. Select the environment URL below.';
  }
}

function handleOnline() {
  online.value = true;
}

function handleOffline() {
  online.value = false;
}

async function refreshLocalDrafts() {
  localDrafts.value = await draftStore.list();
}

function handleFormLoaded() {
  if (!selectedAssignment.value) {
    return;
  }

  clearRuntimeFallbackTimer();
  formRuntimeLoading.value = false;
  runtimeStatus.value = selectedEditSubmission.value
    ? 'Form edit session loaded. Submit saves a new version for this record.'
    : '';
  relabelOdkSubmitButton();
}

async function handleSubmit(payload: unknown, callback?: (result: unknown) => void) {
  if (!selectedAssignment.value) {
    submitStatus.value = 'Select an assigned form before submitting.';
    submitTone.value = 'warning';
    return;
  }

  submitting.value = true;
  postSubmitMessage.value = '';
  const candidate = payload as { status?: string; violations?: unknown };
  const violationCount = Array.isArray(candidate.violations) ? candidate.violations.length : 'unknown';
  odkSubmitEventStatus.value = `${new Date().toLocaleTimeString()} - ODK submit event received; payload status ${candidate.status ?? 'unknown'}, violations ${violationCount}.`;
  if (candidate.status !== 'ready') {
    submitting.value = false;
    dataverseWriteStatus.value = `${new Date().toLocaleTimeString()} - Dataverse submit skipped because ODK validation is not ready.`;
    submitStatus.value = `Please fix the highlighted form fields before submitting. Validation issues: ${violationCount}.`;
    submitTone.value = 'warning';
    void focusFirstRuntimeErrorAfterRender();
    return;
  }

  dataverseWriteStatus.value = `${new Date().toLocaleTimeString()} - Starting Dataverse submit write.`;
  submitStatus.value = 'Submitting to Dataverse...';
  submitTone.value = 'neutral';
  try {
    const result = await api.submitOdkSubmission(selectedAssignment.value, payload, {
      existingSubmission: selectedEditSubmission.value,
    });
    dataverseWriteStatus.value = `${new Date().toLocaleTimeString()} - Dataverse submit write completed.`;
    const attachmentSummary = `${result.attachmentCount} attachment record${result.attachmentCount === 1 ? '' : 's'}, ${result.attachmentBinaryUploadCount} binary upload${result.attachmentBinaryUploadCount === 1 ? '' : 's'}`;
    const warningSummary = result.attachmentWarnings.length > 0 ? ` Attachment warning: ${result.attachmentWarnings.join(' ')}` : '';
    submitStatus.value = `Submitted to Dataverse. ${result.displayName || result.instanceId}, version ${result.versionNumber}; ${attachmentSummary}.${warningSummary}`;
    submitTone.value = result.attachmentWarnings.length > 0 ? 'warning' : 'success';
    if (selectedEditSubmission.value || !ODK_RUNTIME_ENABLED) {
      callback?.({});
    } else {
      const module = await import('@getodk/web-forms');
      callback?.({ next: module.POST_SUBMIT__NEW_INSTANCE });
    }
    activeFormSection.value = 'data';
    savedPage.value = 1;
    selectedEditSubmission.value = null;
    if (selectedAssignment.value) {
      rememberWarmAssignment(selectedAssignment.value);
    }
    activeView.value = selectedProject.value ? 'records' : 'projects';
    postSubmitTone.value = result.attachmentWarnings.length > 0 ? 'warning' : 'success';
    postSubmitMessage.value = submitStatus.value;
    submitStatus.value = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    void loadReportingData();
  } catch (caught) {
    dataverseWriteStatus.value = `${new Date().toLocaleTimeString()} - Dataverse submit write failed.`;
    submitStatus.value = caught instanceof Error ? `Submit failed: ${caught.message}` : 'Submit failed.';
    submitTone.value = 'error';
  } finally {
    submitting.value = false;
  }
}

async function loadWorkspace() {
  if (!api.hasPowerPagesSession()) {
    authRequired.value = true;
    error.value = '';
    window.location.assign(api.getSignInUrl());
    return;
  }

  loading.value = true;
  error.value = '';
  authRequired.value = false;
  try {
    const [nextAssignments] = await measureAsync('view:loadWorkspace', () => Promise.all([
      api.listAssignedForms(),
      refreshLocalDrafts(),
    ]));
    assignments.value = nextAssignments;
    submissions.value = [];
    selectedAssignment.value = assignments.value[0] ? getWarmAssignment(assignments.value[0]) : null;
    selectedEditSubmission.value = null;
    if (!selectedProjectId.value && projectWorkspaces.value[0]) {
      selectedProjectId.value = projectWorkspaces.value[0].id;
    }
    if (selectedProject.value && !selectedProjectAssignments.value.some((assignment) => assignment.formVersionId === selectedAssignment.value?.formVersionId)) {
      selectedAssignment.value = selectedProjectAssignments.value[0] ? getWarmAssignment(selectedProjectAssignments.value[0]) : null;
    }
    savedPage.value = 1;
    draftPage.value = 1;
    runtimeStatus.value = selectedAssignment.value ? 'Preparing form runtime...' : '';
    submitStatus.value = '';
    submitTone.value = 'neutral';
    runtimeClickStatus.value = selectedAssignment.value
      ? 'No ODK runtime button click observed for this selected form.'
      : 'No assigned form selected.';
    odkSubmitEventStatus.value = selectedAssignment.value
      ? 'No ODK submit event observed for this selected form.'
      : 'No assigned form selected.';
    dataverseWriteStatus.value = selectedAssignment.value
      ? 'No Dataverse submit write attempted for this selected form.'
      : 'No assigned form selected.';
    lastWorkspaceRefreshAt.value = new Date().toISOString();
    void loadReportingData();
  } catch (caught) {
    const message = caught instanceof Error ? caught.message : 'Unable to load workspace.';
    if ((message.includes('401') || message.includes('403')) && !api.hasPowerPagesSession()) {
      authRequired.value = true;
      window.location.assign(api.getSignInUrl());
      return;
    }
    error.value = message;
  } finally {
    loading.value = false;
  }
}

watch(recordSearch, () => {
  savedPage.value = 1;
  if (reportSearchTimer !== null) window.clearTimeout(reportSearchTimer);
  reportSearchTimer = window.setTimeout(() => void loadReportingData(), 300);
});

watch([reportDateFrom, reportDateTo, reportSubmitter, reportReviewState], () => {
  savedPage.value = 1;
  void loadReportingData();
});

watch([reportTotal], () => {
  clampActivePage();
});

onMounted(() => {
  document.addEventListener('submit', preventPowerPagesFormSubmit, true);
  document.addEventListener('click', preventRuntimeButtonDefault, true);
  window.addEventListener('hashchange', handleHashRouteChange);
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  odkRuntimeObserver = new MutationObserver(relabelOdkSubmitButton);
  odkRuntimeObserver.observe(document.body, { childList: true, subtree: true });
  void loadWorkspace().then(async () => {
    if (restoreAccessWorkflowOutcome()) {
      await refreshAccessManagement();
      await nextTick();
      document.getElementById('access-onboarding-outcome')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    await applyRouteIntent(routeIntentFromHash());
  });
});

onUnmounted(() => {
  clearRuntimeFallbackTimer();
  document.removeEventListener('submit', preventPowerPagesFormSubmit, true);
  document.removeEventListener('click', preventRuntimeButtonDefault, true);
  window.removeEventListener('hashchange', handleHashRouteChange);
  window.removeEventListener('online', handleOnline);
  window.removeEventListener('offline', handleOffline);
  odkRuntimeObserver?.disconnect();
  odkRuntimeObserver = null;
  if (reportSearchTimer !== null) window.clearTimeout(reportSearchTimer);
});
</script>

<template>
  <main class="monitoring-shell" :aria-label="platformName">
    <section v-if="authRequired" class="auth-panel" aria-labelledby="auth-title">
      <h1 id="auth-title">Sign in required</h1>
      <p>Use your Microsoft account to continue to the MEL Tool.</p>
      <a class="primary-action" :href="api.getSignInUrl()">
        <LogIn class="action-icon" aria-hidden="true" />
        Microsoft Entra
      </a>
    </section>

    <div
      v-else
      class="managed-app-shell"
      :class="{ 'managed-app-shell--collapsed': shellNavCollapsed, 'managed-app-shell--mobile-open': mobileNavOpen }"
    >
      <button
        v-if="mobileNavOpen"
        class="nav-scrim"
        type="button"
        aria-label="Close navigation"
        @click="closeMobileNav"
      />
      <aside class="managed-side-nav" aria-label="MEL Tool navigation">
        <div class="managed-side-nav__brand">
          <img class="managed-side-nav__logo" :src="crdbLogoUrl" alt="CRDB Bank">
          <div class="managed-side-nav__brand-text">
            <strong>TACATDP <span aria-hidden="true">🌱</span></strong>
            <small>CRDB · Green Climate Fund</small>
          </div>
        </div>

        <nav class="managed-side-nav__section managed-side-nav__section--primary" aria-label="Overview navigation">
          <h2>Overview</h2>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'dashboard' }"
            type="button"
            aria-label="Overview"
            @click="openDashboard"
          >
            <LayoutDashboard class="managed-nav-item__icon" aria-hidden="true" />
            <span>Overview</span>
            <span class="action-tooltip" role="tooltip">Overview</span>
          </button>
        </nav>

        <nav class="managed-side-nav__section" aria-label="Programme navigation">
          <h2>Programme</h2>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'projects' || activeView === 'records' }"
            type="button"
            aria-label="Programmes"
            @click="openRoadmapModule('Programmes')"
          >
            <Clipboard class="managed-nav-item__icon" aria-hidden="true" />
            <span>Programmes</span>
            <span class="action-tooltip" role="tooltip">Programmes</span>
          </button>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'projects' || activeView === 'records' }"
            type="button"
            aria-label="Projects and loans"
            @click="backToProjects"
          >
            <FolderOpen class="managed-nav-item__icon" aria-hidden="true" />
            <span>Projects / Loans</span>
            <span class="action-tooltip" role="tooltip">Projects / Loans</span>
          </button>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'beneficiaries' }"
            type="button"
            aria-label="Beneficiaries"
            @click="openBeneficiaries()"
          >
            <Users class="managed-nav-item__icon" aria-hidden="true" />
            <span>Beneficiaries</span>
            <span class="action-tooltip" role="tooltip">Beneficiaries</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Disbursements" @click="openRoadmapModule('Disbursements')">
            <Database class="managed-nav-item__icon" aria-hidden="true" />
            <span>Disbursements</span>
            <span class="action-tooltip" role="tooltip">Disbursements</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Repayments" @click="openRoadmapModule('Repayments')">
            <ShieldCheck class="managed-nav-item__icon" aria-hidden="true" />
            <span>Repayments</span>
            <span class="action-tooltip" role="tooltip">Repayments</span>
          </button>
        </nav>

        <nav class="managed-side-nav__section" aria-label="Monitoring and evaluation navigation">
          <h2>Monitoring &amp; Evaluation</h2>
          <button class="managed-nav-item" type="button" aria-label="Indicators" @click="openRoadmapModule('Indicators')">
            <Database class="managed-nav-item__icon" aria-hidden="true" />
            <span>Indicators</span>
            <span class="action-tooltip" role="tooltip">Indicators</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Impact Logframe" @click="openRoadmapModule('Impact Logframe')">
            <ShieldCheck class="managed-nav-item__icon" aria-hidden="true" />
            <span>Impact Logframe</span>
            <span class="action-tooltip" role="tooltip">Impact Logframe</span>
          </button>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'workspace' }"
            type="button"
            aria-label="Data Submissions"
            @click="openWorkspace"
          >
            <FileSpreadsheet class="managed-nav-item__icon" aria-hidden="true" />
            <span>Data Submissions</span>
            <span class="action-tooltip" role="tooltip">Data Submissions</span>
          </button>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'reporting' }"
            type="button"
            aria-label="Reports"
            @click="openReportingDestination"
          >
            <BarChart3 class="managed-nav-item__icon" aria-hidden="true" />
            <span>Reports</span>
            <span class="action-tooltip" role="tooltip">Reports</span>
          </button>
        </nav>

        <nav class="managed-side-nav__section" aria-label="Insights navigation">
          <h2>Insights</h2>
          <button
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'dashboard' }"
            type="button"
            aria-label="Dashboards"
            @click="openDashboard"
          >
            <BarChart3 class="managed-nav-item__icon" aria-hidden="true" />
            <span>Dashboards</span>
            <span class="action-tooltip" role="tooltip">Dashboards</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Maps" @click="openRoadmapModule('Maps')">
            <Activity class="managed-nav-item__icon" aria-hidden="true" />
            <span>Maps</span>
            <span class="action-tooltip" role="tooltip">Maps</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Learning and Insights" @click="openRoadmapModule('Learning & Insights')">
            <Clipboard class="managed-nav-item__icon" aria-hidden="true" />
            <span>Learning &amp; Insights</span>
            <span class="action-tooltip" role="tooltip">Learning &amp; Insights</span>
          </button>
        </nav>


        <nav class="managed-side-nav__section managed-side-nav__section--admin" aria-label="Administration navigation">
          <h2>Admin</h2>
          <button
            v-if="canManageAccess"
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'system-activity' }"
            type="button"
            aria-label="System Activity"
            @click="openSystemActivity"
          >
            <Activity class="managed-nav-item__icon" aria-hidden="true" />
            <span>System Activity</span>
            <span class="action-tooltip" role="tooltip">System Activity</span>
          </button>
          <button
            v-if="canManageAccess"
            class="managed-nav-item"
            :class="{ 'managed-nav-item--active': activeView === 'access' }"
            type="button"
            aria-label="User and Access"
            @click="openAccessManagement"
          >
            <UserCog class="managed-nav-item__icon" aria-hidden="true" />
            <span>Users</span>
            <span class="action-tooltip" role="tooltip">Users</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Organizations" @click="openRoadmapModule('Organizations')">
            <Clipboard class="managed-nav-item__icon" aria-hidden="true" />
            <span>Organizations</span>
            <span class="action-tooltip" role="tooltip">Organizations</span>
          </button>
          <button class="managed-nav-item" type="button" aria-label="Settings" @click="openRoadmapModule('Settings')">
            <Settings class="managed-nav-item__icon" aria-hidden="true" />
            <span>Settings</span>
            <span class="action-tooltip" role="tooltip">Settings</span>
          </button>
        </nav>

        <button class="managed-side-nav__org" type="button" aria-label="Current organization and branch">
          <span>Sustainable Finance Unit</span>
          <strong>CRDB Bank</strong>
          <ChevronDown class="managed-side-nav__org-icon" aria-hidden="true" />
        </button>
      </aside>

      <section class="managed-app-content" aria-label="Monitoring Tool workspace">
        <header class="managed-top-bar">
          <div class="managed-top-bar__identity">
            <button
              class="icon-action icon-action--secondary icon-action--compact managed-top-bar__switcher"
              type="button"
              :aria-label="mobileNavOpen ? 'Close navigation' : (shellNavCollapsed ? 'Expand side navigation' : 'Collapse side navigation')"
              :aria-expanded="!shellNavCollapsed"
              @click="toggleShellSwitcher"
            >
              <Menu class="action-icon" aria-hidden="true" />
              <span class="action-tooltip" role="tooltip">{{ shellNavCollapsed ? 'Expand navigation' : 'Collapse navigation' }}</span>
            </button>
            <div class="managed-top-bar__title">
              <span class="eyebrow">{{ shellPageEyebrow }}</span>
              <strong>{{ shellPageTitle }}</strong>
            </div>
          </div>
          <div class="managed-top-bar__actions" aria-label="User session">
            <div class="managed-user-chip" aria-label="Signed-in user">
              <span class="managed-user-chip__avatar" aria-hidden="true">{{ signedInUserInitials }}</span>
              <span class="managed-user-chip__body">
                <strong>{{ signedInUserName }}</strong>
                <small>{{ signedInUserRoleLabel }}</small>
              </span>
            </div>
          </div>
        </header>

        <div class="managed-workspace-body">
    <template v-if="activeView === 'dashboard'">
      <TacatdpDashboardPage />
    </template>

    <template v-else-if="activeView === 'beneficiaries'">
      <BeneficiariesView />
    </template>

    <template v-else-if="activeView === 'workspace'">
      <section class="sync-status-strip" aria-label="Device and assignment status">
        <span class="state-dot" :class="{ 'state-dot--offline': !online }" aria-hidden="true"></span>
        <strong>{{ online ? 'Device connected' : 'Device offline' }}</strong>
        <span>{{ dashboardSyncSummary }}</span>
        <span>{{ draftCount }} draft{{ draftCount === 1 ? '' : 's' }} on this device</span>
      </section>

      <section v-if="error" class="status-banner status-banner--error" aria-live="polite">
        {{ error }}
      </section>

      <section v-if="workspaceHydrating && assignments.length === 0" class="dashboard-grid" aria-label="Dashboard loading preview">
        <section class="workspace-panel workspace-panel--skeleton" aria-live="polite" aria-label="Loading assigned projects">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Work queue</p>
              <h2>Assigned projects</h2>
            </div>
          </header>
          <div class="project-list project-list--compact">
            <article v-for="index in 2" :key="`dashboard-skeleton:${index}`" class="project-card project-card--entry project-card--skeleton" aria-hidden="true">
              <div>
                <span class="skeleton-line skeleton-line--eyebrow"></span>
                <span class="skeleton-line skeleton-line--title"></span>
                <span class="skeleton-line skeleton-line--body"></span>
              </div>
              <span class="skeleton-action"></span>
            </article>
          </div>
        </section>
      </section>

      <section
        v-if="!workspaceHydrating || assignments.length > 0"
        class="attention-panel"
        :class="{ 'attention-panel--clear': dashboardAttentionItems.length === 0 }"
        aria-labelledby="attention-title"
        aria-live="polite"
      >
        <template v-if="dashboardAttentionItems.length > 0">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Attention required</p>
              <h2 id="attention-title">Operational checks</h2>
            </div>
            <span class="state-chip state-chip--warning">
              {{ `${dashboardAttentionItems.length} item${dashboardAttentionItems.length === 1 ? '' : 's'}` }}
            </span>
          </header>
          <div class="attention-list">
          <article
            v-for="item in dashboardAttentionItems"
            :key="item.id"
            class="attention-item"
            :class="{
              'attention-item--warning': item.tone === 'warning',
              'attention-item--error': item.tone === 'error',
              'attention-item--info': item.tone === 'info',
            }"
          >
            <strong>{{ item.title }}</strong>
            <span>{{ item.detail }}</span>
          </article>
          </div>
        </template>
        <div v-else class="attention-clear-state">
          <Check class="attention-clear-icon" aria-hidden="true" />
          <div>
            <p class="eyebrow">Attention required</p>
            <h2 id="attention-title">No known issues require attention</h2>
            <span>Based on this device and the latest assignment refresh.</span>
          </div>
        </div>
      </section>

      <section v-if="projectWorkspaces.length > 0" class="dashboard-stack" aria-label="Dashboard work queue">
        <section class="active-assignment-panel" aria-labelledby="active-assignment-title">
          <div>
            <p class="eyebrow">Active assignment</p>
            <h2 id="active-assignment-title">{{ dashboardPrimaryProject?.name }}</h2>
            <p>
              {{ dashboardPrimaryAssignment?.formName || 'No form selected' }}
              <span v-if="dashboardPrimaryAssignment"> · Version {{ dashboardPrimaryAssignment.version }}</span>
            </p>
          </div>
          <div class="active-assignment-actions">
            <button
              class="icon-action icon-action--secondary"
              type="button"
              :disabled="!dashboardPrimaryProject"
              :aria-label="`Open ${dashboardPrimaryProject?.name || 'project'}`"
              @click="dashboardPrimaryProject && openProject(dashboardPrimaryProject)"
            >
              <FolderOpen class="action-icon" aria-hidden="true" />
              View project
            </button>
            <button
              class="icon-action"
              type="button"
              :disabled="!dashboardPrimaryAssignment"
              aria-label="Collect data for active assignment"
              @click="dashboardPrimaryAssignment && openRunner(dashboardPrimaryAssignment)"
            >
              <NotepadText class="action-icon" aria-hidden="true" />
              Collect
            </button>
          </div>
        </section>

        <section class="operational-metric-strip" :aria-busy="workspaceHydrating" aria-label="Operational workload">
          <article
            v-for="metric in dashboardMetricItems"
            :key="metric.id"
            class="operational-metric"
            :class="{
              'operational-metric--success': metric.tone === 'success',
              'operational-metric--warning': metric.tone === 'warning',
            }"
          >
            <div class="operational-metric__body">
              <span class="metric-value">{{ metric.value }}</span>
              <span class="metric-label">{{ metric.label }}</span>
              <small>{{ metric.detail }}</small>
            </div>
            <span class="operational-metric__icon" aria-hidden="true">
              <FolderOpen v-if="metric.id === 'active-projects'" />
              <Clipboard v-else-if="metric.id === 'forms-action'" />
              <FileSpreadsheet v-else-if="metric.id === 'local-drafts'" />
              <UserCog v-else />
            </span>
          </article>
        </section>

        <section class="dashboard-grid dashboard-grid--with-rail">
          <div class="dashboard-main-column">
            <section class="workspace-panel" aria-labelledby="dashboard-work-title">
              <header class="section-heading">
                <div>
                  <p class="eyebrow">Work queue</p>
                  <h2 id="dashboard-work-title">Assigned projects</h2>
                </div>
                <button class="icon-action icon-action--secondary" type="button" aria-label="View all projects" @click="backToProjects">
                  <FolderOpen class="action-icon" aria-hidden="true" />
                  Projects
                </button>
              </header>
              <div class="project-list project-list--compact">
                <article
                  v-for="project in projectWorkspaces"
                  :key="`dashboard:${project.id}`"
                  class="project-card project-card--entry"
                >
                  <div>
                    <p class="eyebrow">Project</p>
                    <h3>{{ project.name }}</h3>
                    <p>{{ project.assignments.length }} form{{ project.assignments.length === 1 ? '' : 's' }} assigned · {{ draftCount }} draft{{ draftCount === 1 ? '' : 's' }} on this device</p>
                  </div>
                  <button class="icon-action" type="button" :aria-label="`Open ${project.name}`" @click="openProject(project)">
                    <FolderOpen class="action-icon" aria-hidden="true" />
                    Open
                  </button>
                </article>
              </div>
            </section>

            <section class="workspace-panel workspace-panel--data-entry" aria-labelledby="recent-activity-title">
              <header class="section-heading">
                <div>
                  <p class="eyebrow">Data access</p>
                  <h2 id="recent-activity-title">Submitted records</h2>
                </div>
                <button
                  class="icon-action icon-action--secondary"
                  type="button"
                  :disabled="!dashboardPrimaryProject"
                  aria-label="Open submitted records in Data"
                  @click="dashboardPrimaryProject && openProjectSection(dashboardPrimaryProject, 'data')"
                >
                  <Database class="action-icon" aria-hidden="true" />
                  Open Data
                </button>
              </header>
              <p class="data-entry-summary">Open Data to view submitted records, review status, and export permitted records.</p>
              <p class="data-entry-scope">
                <UserCog class="inline-icon" aria-hidden="true" />
                <strong>Scope:</strong> {{ dashboardSubmittedScopeLabel }}
              </p>
              <div v-if="dashboardRecentSubmissions.length > 0" class="activity-list">
                <article v-for="submission in dashboardRecentSubmissions" :key="submission.submissionId" class="activity-row">
                  <div>
                    <strong>{{ submission.displayName || submission.instanceId }}</strong>
                    <span>{{ submission.userEmail || 'Unknown submitter' }} · {{ formatDate(submission.updatedAt || submission.submittedAt) }}</span>
                  </div>
                  <span class="state-chip">{{ formatReviewState(submission.reviewState) }}</span>
                </article>
              </div>
              <p v-else class="data-entry-empty-note">Open Data to view synchronized records. Record tables stay off the dashboard until needed.</p>
            </section>
          </div>

          <aside class="dashboard-side-rail" aria-label="Operational support">
            <section class="side-rail-card" aria-labelledby="quick-actions-title">
              <p class="eyebrow">Quick actions</p>
              <h2 id="quick-actions-title">Next steps</h2>
              <div class="side-rail-actions">
                <button class="side-rail-action side-rail-action--primary" type="button" :disabled="!dashboardPrimaryAssignment" @click="dashboardPrimaryAssignment && openRunner(dashboardPrimaryAssignment)">
                  <NotepadText class="action-icon" aria-hidden="true" />
                  <span>Collect data</span>
                </button>
                <button class="side-rail-action" type="button" :disabled="!dashboardPrimaryProject" @click="dashboardPrimaryProject && openProjectSection(dashboardPrimaryProject, 'data')">
                  <Database class="action-icon" aria-hidden="true" />
                  <span>Open Data</span>
                </button>
                <button class="side-rail-action" type="button" @click="openReportingDestination">
                  <BarChart3 class="action-icon" aria-hidden="true" />
                  <span>Reporting</span>
                </button>
              </div>
            </section>
          </aside>
        </section>
      </section>

      <section v-else-if="!workspaceHydrating && !error" class="empty-state" aria-label="No projects">
        <h2>No projects</h2>
        <p>No project assignments were returned for this Power Pages session.</p>
      </section>
    </template>

    <template v-else-if="activeView === 'roadmap'">
      <section class="workspace-panel roadmap-panel" aria-labelledby="roadmap-module-title">
        <p class="eyebrow">Module scope</p>
        <h2 id="roadmap-module-title">{{ selectedRoadmapModule }}</h2>
        <p>
          This module is outside the current TACATDP field monitoring delivery. It is reserved for the broader Sustainable Finance MEL platform scope.
        </p>
        <div class="roadmap-panel__actions">
          <button class="icon-action" type="button" @click="backToProjects">
            <FolderOpen class="action-icon" aria-hidden="true" />
            Back to projects
          </button>
          <button class="icon-action icon-action--secondary" type="button" @click="openDashboard">
            <LayoutDashboard class="action-icon" aria-hidden="true" />
            Dashboard
          </button>
        </div>
      </section>
    </template>

    <template v-else-if="activeView === 'projects'">
      <section v-if="error" class="status-banner status-banner--error" aria-live="polite">
        {{ error }}
      </section>

      <section v-if="workspaceHydrating && assignments.length === 0" class="project-list" aria-live="polite" aria-label="Loading available projects">
        <article v-for="index in 3" :key="`project-skeleton:${index}`" class="project-card project-card--entry project-card--skeleton" aria-hidden="true">
          <div>
            <span class="skeleton-line skeleton-line--eyebrow"></span>
            <span class="skeleton-line skeleton-line--title"></span>
            <span class="skeleton-line skeleton-line--body"></span>
            <span class="skeleton-line skeleton-line--body skeleton-line--short"></span>
          </div>
          <span class="skeleton-action"></span>
        </article>
      </section>

      <section v-if="projectWorkspaces.length > 0" class="project-list" aria-label="Available projects">
        <article
          v-for="project in projectWorkspaces"
          :key="project.id"
          class="project-card project-card--entry"
        >
          <div>
            <p class="eyebrow">Project</p>
            <h2>{{ project.name }}</h2>
            <p>{{ project.description }}</p>
            <dl class="compact-facts">
              <div>
                <dt>Forms</dt>
                <dd>{{ project.assignments.length }}</dd>
              </div>
              <div>
                <dt>Local drafts</dt>
                <dd>{{ draftCount }}</dd>
              </div>
            </dl>
          </div>
          <button class="icon-action" type="button" :aria-label="`Open ${project.name}`" @click="openProject(project)">
            <FolderOpen class="action-icon" aria-hidden="true" />
            Open
          </button>
        </article>
      </section>

      <section v-else-if="!workspaceHydrating && !error" class="empty-state" aria-label="No projects">
        <h2>No projects</h2>
        <p>No project assignments were returned for this Power Pages session.</p>
      </section>
    </template>

    <template v-else-if="activeView === 'reporting'">
      <section class="route-status-strip" aria-label="Reporting summary">
        <article class="metric-card metric-card--accent">
          <span class="metric-value">{{ projectWorkspaces.length }}</span>
          <span class="metric-label">Projects</span>
        </article>
        <article class="metric-card">
          <span class="metric-value">{{ activeRecordCount }}</span>
          <span class="metric-label">Projected records</span>
        </article>
        <article class="metric-card">
          <span class="metric-value">{{ exportSettings.length }}</span>
          <span class="metric-label">Named exports</span>
        </article>
        <article class="metric-card">
          <span class="metric-value">{{ reportError ? 'Check' : 'Ready' }}</span>
          <span class="metric-label">Projection health</span>
        </article>
      </section>

      <section v-if="reportError" class="status-banner status-banner--error" aria-live="polite">
        {{ reportError }}
      </section>

      <section class="workspace-panel" aria-labelledby="reporting-projects-title">
        <header class="section-heading">
          <div>
            <p class="eyebrow">Project reporting</p>
            <h2 id="reporting-projects-title">Reporting workspaces</h2>
          </div>
        </header>
        <div v-if="reportingProjectRows.length > 0" class="responsive-table" role="region" aria-label="Reporting workspace table" tabindex="0">
          <table>
            <thead>
              <tr>
                <th scope="col">Project</th>
                <th scope="col">Forms</th>
                <th scope="col">Records</th>
                <th scope="col">Last updated</th>
                <th scope="col">Projection</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in reportingProjectRows" :key="`reporting:${row.project.id}`">
                <td>
                  <strong>{{ row.project.name }}</strong>
                  <span>{{ row.project.description }}</span>
                </td>
                <td>{{ row.forms }}</td>
                <td>{{ row.records }}</td>
                <td>{{ formatDate(row.lastUpdated) }}</td>
                <td><span class="state-chip" :class="reportError ? 'state-chip--warning' : 'state-chip--success'">{{ row.projectionStatus }}</span></td>
                <td>
                  <div class="table-actions">
                    <button class="icon-action icon-action--secondary icon-action--compact" type="button" aria-label="Open project data" @click="openProjectSection(row.project, 'data')">
                      <Database class="action-icon" aria-hidden="true" />
                      <span class="action-tooltip" role="tooltip">Data</span>
                    </button>
                    <button class="icon-action icon-action--secondary icon-action--compact" type="button" aria-label="Open exports" @click="openProjectSection(row.project, 'exports')">
                      <Download class="action-icon" aria-hidden="true" />
                      <span class="action-tooltip" role="tooltip">Exports</span>
                    </button>
                    <button class="icon-action icon-action--secondary icon-action--compact" type="button" aria-label="Open Power BI" @click="openProjectSection(row.project, 'powerbi')">
                      <BarChart3 class="action-icon" aria-hidden="true" />
                      <span class="action-tooltip" role="tooltip">Power BI</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <section v-else class="empty-state empty-state--inline" aria-label="No reporting workspaces">
          <h2>No reporting workspaces</h2>
          <p>Project reporting will appear after assignments are available.</p>
        </section>
      </section>
    </template>

    <template v-else-if="activeView === 'records'">
      <section v-if="error" class="status-banner status-banner--error" aria-live="polite">
        {{ error }}
      </section>

      <section v-if="postSubmitMessage" class="status-banner" :class="`status-banner--${postSubmitTone}`" aria-live="polite">
        {{ postSubmitMessage }}
      </section>

      <section class="project-form-workspace" aria-label="Project data workspace">
        <article class="project-command-card" aria-label="Selected project">
          <button class="collect-action" type="button" :disabled="!primaryAssignment" aria-label="Collect" @click="openRunner(primaryAssignment)">
            <NotepadText class="action-icon" aria-hidden="true" />
            Collect
          </button>
          <div class="project-command-card__copy">
            <h2>{{ selectedProject?.name }}</h2>
            <p>{{ online ? 'Online' : 'Offline' }} · {{ selectedProjectAssignments.length }} form{{ selectedProjectAssignments.length === 1 ? '' : 's' }} · {{ savedCount }} submitted</p>
          </div>
        </article>

        <section v-if="selectedAssignment" class="form-section-shell" :aria-label="`${selectedProject?.name} workspace`">
          <div class="material-tabs" role="tablist" aria-label="Project workspace sections">
            <button
              class="material-tab"
              :class="{ 'material-tab--active': activeFormSection === 'summary' }"
              type="button"
              role="tab"
              :aria-selected="activeFormSection === 'summary'"
              @click="selectFormSection('summary')"
            >
              Summary
            </button>
            <button
              class="material-tab"
              :class="{ 'material-tab--active': activeFormSection === 'data' }"
              type="button"
              role="tab"
              :aria-selected="activeFormSection === 'data'"
              @click="selectFormSection('data')"
            >
              Data
            </button>
            <button
              class="material-tab"
              :class="{ 'material-tab--active': activeFormSection === 'exports' }"
              type="button"
              role="tab"
              :aria-selected="activeFormSection === 'exports'"
              @click="selectFormSection('exports')"
            >
              Exports
            </button>
            <button
              class="material-tab"
              :class="{ 'material-tab--active': activeFormSection === 'powerbi' }"
              type="button"
              role="tab"
              :aria-selected="activeFormSection === 'powerbi'"
              @click="selectFormSection('powerbi')"
            >
              Power BI
            </button>
          </div>

          <section v-if="activeFormSection === 'summary'" class="summary-grid" role="tabpanel" aria-label="Project summary">
            <article class="metric-card metric-card--accent">
              <span class="metric-value">{{ selectedFormSavedCount }}</span>
              <span class="metric-label">Submitted records</span>
            </article>
            <article class="metric-card">
              <span class="metric-value">{{ selectedProjectAssignments.length }}</span>
              <span class="metric-label">Project forms</span>
            </article>
            <article class="metric-card">
              <span class="metric-value">{{ selectedFormDraftCount }}</span>
              <span class="metric-label">Local drafts</span>
            </article>
            <article class="metric-card">
              <span class="metric-value">{{ online ? 'Online' : 'Offline' }}</span>
              <span class="metric-label">Connection</span>
            </article>
            <article class="guidance-card guidance-card--wide">
              <Database class="guidance-icon" aria-hidden="true" />
              <div>
                <p class="eyebrow">Current form</p>
                <h3>{{ selectedAssignment.formName }}</h3>
                <p>Version {{ selectedAssignment.version }} · {{ selectedAssignment.xmlFormId }}</p>
              </div>
            </article>
          </section>

          <section v-else-if="activeFormSection === 'data'" class="data-table-panel" role="tabpanel" aria-label="Submitted data">
            <div class="record-toolbar">
              <div>
                <p class="eyebrow">Data</p>
                <h3>Reporting records</h3>
              </div>
              <label class="record-search">
                <Search class="record-search__icon" aria-hidden="true" />
                <span class="sr-only">Search submitted data</span>
                <input
                  v-model="recordSearch"
                  type="search"
                  autocomplete="off"
                  placeholder="Search submitted data"
                  aria-label="Search submitted data"
                >
              </label>
            </div>

            <section class="export-note export-note--scope" role="note" aria-label="Reporting access scope">
              <ShieldCheck class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>{{ reportingScopeLabel }}</strong>
                <p>{{ reportingScopeSummary }}</p>
              </div>
            </section>

            <div class="report-filter-bar" aria-label="Reporting filters">
              <div class="filter-field filter-field--date-range">
                <label for="report-date-range">Updated date</label>
                <VueDatePicker
                  v-model="reportDateRange"
                  class="date-range-picker"
                  :range="{ partialRange: false }"
                  :time-config="{ enableTimePicker: false }"
                  :text-input="{ format: 'dd/MM/yyyy', rangeSeparator: ' - ', enterSubmit: true, tabSubmit: true, escClose: true, applyOnBlur: true }"
                  :formats="{ input: 'dd MMM yyyy' }"
                  :input-attrs="{ id: 'report-date-range', autocomplete: 'off', clearable: true }"
                  :ui="{ menu: 'tacatdp-date-menu' }"
                  :preset-dates="reportDatePresets"
                  :aria-labels="{
                    input: 'Updated date range',
                    calendarIcon: 'Open updated date calendar',
                    clearInput: 'Clear updated date range',
                    menu: 'Updated date calendar',
                    nextMonth: 'Next month',
                    prevMonth: 'Previous month',
                  }"
                  week-start="1"
                  auto-apply
                  placeholder="Select date range"
                />
              </div>
              <label class="filter-field">
                <span>Submitter</span>
                <input
                  v-model="reportSubmitter"
                  type="email"
                  list="report-submitter-options"
                  :disabled="!canReadAllReportingRows"
                  :placeholder="canReadAllReportingRows ? 'All submitters' : 'Restricted to your email'"
                >
                <datalist id="report-submitter-options">
                  <option v-for="submitter in uniqueSubmitters" :key="submitter" :value="submitter" />
                </datalist>
              </label>
              <label class="filter-field">
                <span>Review state</span>
                <select v-model="reportReviewState">
                  <option value="">All states</option>
                  <option :value="100000000">Received</option>
                  <option :value="100000001">Edited</option>
                  <option :value="100000002">Has issues</option>
                  <option :value="100000003">Rejected</option>
                  <option :value="100000004">Approved</option>
                </select>
              </label>
              <button
                class="icon-action icon-action--secondary icon-action--compact filter-clear"
                type="button"
                aria-label="Clear all filters"
                @click="clearReportFilters"
              >
                <FilterX class="action-icon" aria-hidden="true" />
                <span class="action-tooltip" role="tooltip">Clear filters</span>
              </button>
            </div>

            <section v-if="reportError" class="status-banner status-banner--error" aria-live="polite">
              {{ reportError }}
            </section>
            <section v-if="reportLoading" class="loading-panel loading-panel--inline" aria-live="polite" aria-label="Loading reporting data">
              <h2>Loading reporting data</h2>
              <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
            </section>

            <div v-else class="responsive-table" role="region" aria-label="Reporting data table" tabindex="0">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Record</th>
                    <th scope="col">Version</th>
                    <th scope="col">Updated</th>
                    <th scope="col">Review</th>
                    <th scope="col">Projection</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="reportRow in reportRows" :key="reportRow.mp_submissionreportrowid">
                    <td>
                      <strong>{{ reportRow.mp_displayname || reportRow.mp_instanceid }}</strong>
                      <span>{{ reportRow.mp_instanceid }}</span>
                    </td>
                    <td>{{ reportRow.mp_versionnumber || 1 }}</td>
                    <td>{{ formatDate(reportRow.mp_updatedat || reportRow.mp_submittedat) }}</td>
                    <td>{{ formatReviewState(reportRow.mp_reviewstate) }}</td>
                    <td><span class="state-chip">{{ formatProjectionStatus(reportRow.mp_projectionstatus) }}</span></td>
                    <td>
                      <div class="table-actions">
                        <button
                          class="icon-action icon-action--secondary icon-action--compact"
                          type="button"
                          :disabled="reportLoading"
                          aria-label="View record"
                          @click="openReportDetail(reportRow)"
                        >
                          <Eye class="action-icon" aria-hidden="true" />
                          <span class="action-tooltip" role="tooltip">View record</span>
                        </button>
                        <button
                          class="icon-action icon-action--secondary icon-action--compact"
                          type="button"
                          :disabled="loading"
                          aria-label="Edit record"
                          @click="editReportRow(reportRow)"
                        >
                          <Pencil class="action-icon" aria-hidden="true" />
                          <span class="action-tooltip" role="tooltip">Edit record</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <section v-if="!reportLoading && !reportError && reportTotal === 0" class="empty-state empty-state--inline" aria-label="No reporting data">
              <h2>No reporting data</h2>
              <p>No projected records match the current project and filters.</p>
            </section>

            <nav v-if="!reportLoading && reportTotal > 0" class="pagination-bar" aria-label="Reporting record pagination">
              <p class="pagination-summary">
                Showing {{ activePageStart }}-{{ activePageEnd }} of {{ activeRecordCount }}
              </p>
              <div class="pagination-controls">
                <button
                  class="pagination-button pagination-button--icon"
                  type="button"
                  :disabled="activeRecordPage <= 1"
                  aria-label="Previous page"
                  @click="changePage(-1)"
                >
                  <ChevronLeft class="action-icon" aria-hidden="true" />
                </button>
                <button
                  v-for="pageNumber in visiblePageNumbers"
                  :key="pageNumber"
                  class="pagination-button"
                  :class="{ 'pagination-button--active': pageNumber === activeRecordPage }"
                  type="button"
                  :aria-current="pageNumber === activeRecordPage ? 'page' : undefined"
                  :aria-label="`Page ${pageNumber}`"
                  @click="setActivePage(pageNumber)"
                >
                  {{ pageNumber }}
                </button>
                <button
                  class="pagination-button pagination-button--icon"
                  type="button"
                  :disabled="activeRecordPage >= activeTotalPages"
                  aria-label="Next page"
                  @click="changePage(1)"
                >
                  <ChevronRight class="action-icon" aria-hidden="true" />
                </button>
              </div>
              <p class="pagination-page-count">
                Page {{ activeRecordPage }} of {{ activeTotalPages }}
              </p>
            </nav>

            <section v-if="selectedReportRow" class="record-detail-panel" aria-labelledby="record-detail-title">
              <header class="record-detail-header">
                <div>
                  <p class="eyebrow">Record detail</p>
                  <h3 id="record-detail-title">{{ selectedReportRow.mp_displayname || selectedReportRow.mp_instanceid }}</h3>
                  <p>Owner: {{ selectedReportRow.mp_useremail || 'Unknown owner' }} · Version {{ selectedReportRow.mp_versionnumber }} · {{ formatReviewState(selectedReportRow.mp_reviewstate) }}</p>
                </div>
                <button class="icon-action icon-action--secondary" type="button" @click="closeReportDetail">Close</button>
              </header>
              <section v-if="reportDetailError" class="status-banner status-banner--error" aria-live="polite">{{ reportDetailError }}</section>
              <section v-else-if="reportDetailLoading" class="loading-panel loading-panel--inline" aria-live="polite">
                <h2>Loading answers</h2>
                <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
              </section>
              <dl v-else class="answer-list">
                <div v-for="answer in reportAnswers" :key="answer.mp_submissionanswerid" class="answer-row">
                  <dt>{{ answer.mp_fieldlabel || answer.mp_fieldname || answer.mp_fieldpath }}</dt>
                  <dd>{{ formatAnswerValue(answer) }}</dd>
                  <small>{{ answer.mp_fieldpath }}<template v-if="answer._mp_submissionrepeatrow_value"> · Repeat answer</template></small>
                </div>
              </dl>
              <section v-if="!reportDetailLoading && !reportDetailError && reportAnswers.length === 0" class="empty-state empty-state--inline">
                <h2>No answer rows</h2>
                <p>This reporting record has no normalized answer rows.</p>
              </section>
            </section>
          </section>

          <section v-else-if="activeFormSection === 'exports'" class="export-workspace" role="tabpanel" aria-label="Exports">
            <header class="section-heading">
              <div>
                <p class="eyebrow">Exports</p>
                <h3>Named CSV exports</h3>
                <p>Save the current Data filters and download governed root reporting rows.</p>
              </div>
            </header>
            <section v-if="exportMessage" class="status-banner status-banner--success" aria-live="polite">{{ exportMessage }}</section>
            <section v-if="exportError" class="status-banner status-banner--error" aria-live="polite">{{ exportError }}</section>
            <div class="export-create-panel">
              <label class="filter-field export-name-field">
                <span>Export name</span>
                <input :value="exportName" type="text" readonly aria-readonly="true">
              </label>
              <div class="export-scope-summary">
                <strong>Current filters</strong>
                <span>{{ recordSearch || reportDateFrom || reportDateTo || reportSubmitter || reportReviewState !== '' ? 'Filtered reporting rows' : 'All projected rows for the current form' }}</span>
              </div>
              <div class="export-scope-summary export-scope-summary--guarded">
                <strong>{{ reportingScopeLabel }}</strong>
                <span>{{ exportScopeMessage }}</span>
              </div>
              <button class="icon-action" type="button" :disabled="exportLoading" @click="saveAndDownloadCsv">
                <Save class="action-icon" aria-hidden="true" />
                {{ exportLoading ? 'Preparing CSV' : 'Save and download CSV' }}
              </button>
            </div>
            <div class="export-note" role="note">
              <FileSpreadsheet class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>Root records only</strong>
                <p>CSV does not include repeat rows. XLSX remains unavailable until repeat-group data and a governed workbook generator are verified.</p>
              </div>
            </div>
            <section class="named-export-list" aria-labelledby="saved-exports-title">
              <h3 id="saved-exports-title">Saved exports</h3>
              <article v-for="setting in exportSettings" :key="setting.mp_exportsettingid" class="named-export-row">
                <div>
                  <strong>{{ setting.mp_name }}</strong>
                  <span>CSV · Current filters · Updated {{ formatDate(setting.mp_updatedat || setting.mp_createdat) }}</span>
                </div>
                <button class="icon-action icon-action--secondary" type="button" :disabled="exportLoading" @click="rerunExport(setting)">
                  <Download class="action-icon" aria-hidden="true" />
                  Download
                </button>
              </article>
              <section v-if="exportSettings.length === 0 && !exportError" class="empty-state empty-state--inline">
                <h2>No saved exports</h2>
                <p>Name the current dataset and save the first reusable export.</p>
              </section>
            </section>
          </section>

          <section v-else class="powerbi-workspace" role="tabpanel" aria-label="Power BI">
            <header class="section-heading section-heading--with-icon">
              <BarChart3 class="guidance-icon" aria-hidden="true" />
              <div>
                <p class="eyebrow">Power BI</p>
                <h3>Connect to Dataverse</h3>
                <p>Use the Microsoft Dataverse connector and an organizational account with reporting-table read access.</p>
              </div>
            </header>
            <section class="connection-panel" aria-labelledby="connection-title">
              <div>
                <span class="field-label" id="connection-title">Environment URL</span>
                <code>{{ powerBiEnvironmentUrl }}</code>
              </div>
              <button class="icon-action icon-action--secondary" type="button" @click="copyPowerBiEnvironmentUrl">
                <Check v-if="powerBiCopyStatus === 'Environment URL copied.'" class="action-icon" aria-hidden="true" />
                <Clipboard v-else class="action-icon" aria-hidden="true" />
                Copy URL
              </button>
            </section>
            <p v-if="powerBiCopyStatus" class="copy-status" aria-live="polite">{{ powerBiCopyStatus }}</p>
            <section class="powerbi-steps" aria-labelledby="powerbi-steps-title">
              <h3 id="powerbi-steps-title">Connection steps</h3>
              <ol>
                <li>In Power BI Desktop, select Get data, then Microsoft Dataverse.</li>
                <li>Enter the environment URL above and sign in with your CRDB organizational account.</li>
                <li>Select the reporting tables below. Start with Import mode unless CRDB policy approves DirectQuery.</li>
                <li>Relate repeat and answer tables to the root report table through the submission report row lookup.</li>
              </ol>
            </section>
            <section class="powerbi-table-list" aria-labelledby="powerbi-tables-title">
              <h3 id="powerbi-tables-title">Reporting tables</h3>
              <article v-for="table in powerBiTables" :key="table.logical" class="powerbi-table-row">
                <Database class="action-icon" aria-hidden="true" />
                <div>
                  <strong>{{ table.label }}</strong>
                  <code>{{ table.logical }}</code>
                  <span>{{ table.purpose }}</span>
                </div>
              </article>
            </section>
            <div class="export-note" role="note">
              <Database class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>Access requirement</strong>
                <p>Power Pages table permissions do not grant Power BI access. The signed-in Power BI user also needs Dataverse security-role read permission for these reporting tables.</p>
              </div>
            </div>
          </section>
        </section>

        <section v-else class="empty-state empty-state--inline" aria-label="No selected form">
          <h2>No form selected</h2>
          <p>Select a project form before collecting data or configuring reporting.</p>
        </section>
      </section>
    </template>

    <template v-else-if="activeView === 'system-activity'">
      <section v-if="!canManageAccess" class="empty-state" aria-label="System Activity denied">
        <ShieldCheck class="guidance-icon" aria-hidden="true" />
        <h2>You do not have access to System Activity</h2>
        <p>This administration route is available only to users with an approved Platform Administrator web role.</p>
        <dl class="access-authorization-list" aria-label="System Activity authorisation details">
          <div>
            <dt>Decision source</dt>
            <dd>{{ accessAuthorizationSourceLabel }}</dd>
          </div>
          <div>
            <dt>Required role</dt>
            <dd>{{ requiredAccessRoleLabel }}</dd>
          </div>
          <div>
            <dt>Detected roles</dt>
            <dd>{{ detectedAccessRoleLabel }}</dd>
          </div>
        </dl>
      </section>

      <section v-else class="system-activity-workspace" aria-label="System Activity workspace">
        <section class="access-metric-strip" aria-label="System Activity summary">
          <article class="metric-card metric-card--accent">
            <span class="metric-value">{{ systemHealthAttentionCount }}</span>
            <span class="metric-label">Needs attention</span>
          </article>
          <article class="metric-card">
            <span class="metric-value">{{ systemHealthPendingCount }}</span>
            <span class="metric-label">Pending / not configured</span>
          </article>
          <article class="metric-card">
            <span class="metric-value">{{ systemActivityEvents.length }}</span>
            <span class="metric-label">Recent events</span>
          </article>
        </section>

        <nav class="material-tabs access-tabs" aria-label="System Activity sections">
          <button class="material-tab" :class="{ 'material-tab--active': activeSystemActivitySection === 'health' }" type="button" :aria-current="activeSystemActivitySection === 'health' ? 'page' : undefined" @click="setSystemActivitySection('health')">
            Health
          </button>
          <button class="material-tab" :class="{ 'material-tab--active': activeSystemActivitySection === 'events' }" type="button" :aria-current="activeSystemActivitySection === 'events' ? 'page' : undefined" @click="setSystemActivitySection('events')">
            Events
          </button>
          <button class="material-tab" :class="{ 'material-tab--active': activeSystemActivitySection === 'onboarding' }" type="button" :aria-current="activeSystemActivitySection === 'onboarding' ? 'page' : undefined" @click="setSystemActivitySection('onboarding')">
            Onboarding
          </button>
          <button class="material-tab" :class="{ 'material-tab--active': activeSystemActivitySection === 'submissions' }" type="button" :aria-current="activeSystemActivitySection === 'submissions' ? 'page' : undefined" @click="setSystemActivitySection('submissions')">
            Submissions
          </button>
          <button class="material-tab" :class="{ 'material-tab--active': activeSystemActivitySection === 'integrations' }" type="button" :aria-current="activeSystemActivitySection === 'integrations' ? 'page' : undefined" @click="setSystemActivitySection('integrations')">
            Integrations
          </button>
        </nav>

        <section v-if="activeSystemActivitySection === 'health'" class="access-readiness-panel" role="tabpanel" aria-label="System health">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Health</p>
              <h2>Operational checks</h2>
              <p>Read-only checks from current portal state and existing TACATDP diagnostics.</p>
            </div>
          </header>
          <section class="system-health-grid" aria-label="Operational health checks">
            <article v-for="item in systemHealthItems" :key="item.id" class="system-health-card">
              <div>
                <p class="eyebrow">{{ item.component }}</p>
                <h3>{{ item.summary }}</h3>
                <p>{{ item.nextAction }}</p>
              </div>
              <span class="state-chip" :class="`state-chip--${systemHealthTone(item.status)}`">{{ formatSystemHealthStatus(item.status) }}</span>
            </article>
          </section>
        </section>

        <section v-else-if="activeSystemActivitySection === 'events'" class="access-activity-panel" role="tabpanel" aria-label="Recent system events">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Events</p>
              <h2>Recent activity</h2>
              <p>Sanitized operational events and checks. Platform trace logs remain in Microsoft admin tools.</p>
            </div>
          </header>
          <section class="access-activity-list" aria-label="Recent system activity list">
            <article v-for="event in systemActivityEvents" :key="event.id" class="system-activity-row">
              <span class="state-chip" :class="`state-chip--${systemActivityTone(event.severity)}`">{{ event.status }}</span>
              <div>
                <strong>{{ event.action }}</strong>
                <small>{{ event.component }} · {{ formatDate(event.occurredAt) }}</small>
              </div>
              <div>
                <p>{{ event.detail }}</p>
                <small>{{ event.target }}</small>
              </div>
              <div>
                <strong>Next action</strong>
                <small>{{ event.nextAction }}</small>
              </div>
            </article>
          </section>
        </section>

        <section v-else-if="activeSystemActivitySection === 'onboarding'" class="access-activity-panel" role="tabpanel" aria-label="Onboarding activity">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Onboarding</p>
              <h2>User activation timeline</h2>
              <p>Review activation proof before issuing or reissuing invitations.</p>
            </div>
          </header>
          <section class="access-activity-list" aria-label="Onboarding activity list">
            <article v-for="event in systemActivityOnboardingEvents" :key="event.id" class="system-activity-row">
              <span class="state-chip" :class="`state-chip--${systemActivityTone(event.severity)}`">{{ event.status }}</span>
              <div>
                <strong>{{ event.action }}</strong>
                <small>{{ event.actor }}</small>
              </div>
              <div>
                <p>{{ event.detail }}</p>
                <small>{{ event.target }}</small>
              </div>
              <div>
                <strong>Next action</strong>
                <small>{{ event.nextAction }}</small>
              </div>
            </article>
          </section>
          <section v-if="systemActivityOnboardingEvents.length === 0" class="empty-state empty-state--inline" aria-label="No onboarding events">
            <h2>No onboarding events</h2>
            <p>Open User &amp; Access or create an onboarding request to populate this view.</p>
          </section>
          <section class="access-toolbar" aria-label="Activation diagnostics summary">
            <div>
              <p class="eyebrow">Activation</p>
              <h3>User activation diagnostics</h3>
              <p>Confirm invitation redemption and Microsoft identity binding before treating a user as ready.</p>
            </div>
            <button class="icon-action icon-action--secondary" type="button" :disabled="activationDiagnosticsLoading" aria-label="Refresh activation diagnostics" @click="loadActivationDiagnostics">
              <RefreshCw class="action-icon" aria-hidden="true" />
              Refresh
            </button>
          </section>

          <section class="access-metric-strip" aria-label="Activation summary">
            <article class="metric-card metric-card--accent">
              <span class="metric-value">{{ activationReadyCount }}</span>
              <span class="metric-label">Ready</span>
            </article>
            <article class="metric-card">
              <span class="metric-value">{{ activationPendingCount }}</span>
              <span class="metric-label">Pending</span>
            </article>
            <article class="metric-card">
              <span class="metric-value">{{ activationReviewCount }}</span>
              <span class="metric-label">Needs review</span>
            </article>
          </section>

          <div class="access-readiness-note" role="note">
            <ShieldCheck class="guidance-icon" aria-hidden="true" />
            <div>
              <strong>Activation proof</strong>
              <p>Contact and assignment are provisioning records. A user is ready only after invitation redemption creates a Power Pages external identity.</p>
            </div>
          </div>

          <section v-if="activationDiagnosticsError" class="status-banner status-banner--error" aria-live="polite">
            {{ activationDiagnosticsError }}
          </section>

          <section v-if="activationDiagnosticsLoading" class="loading-panel loading-panel--inline" aria-live="polite" aria-label="Loading activation diagnostics">
            <h2>Loading activation diagnostics</h2>
            <p>Checking contacts, invitations, identity binding, and assignments</p>
            <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
          </section>

          <div v-else class="responsive-table access-table activation-diagnostics-table" role="region" aria-label="Activation diagnostics table" tabindex="0">
            <table>
              <thead>
                <tr>
                  <th scope="col">User</th>
                  <th scope="col">Contact</th>
                  <th scope="col">Email</th>
                  <th scope="col">Invitation</th>
                  <th scope="col">Redemption</th>
                  <th scope="col">Identity</th>
                  <th scope="col">Web role</th>
                  <th scope="col">Assignment</th>
                  <th scope="col">Next action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in activationDiagnostics" :key="row.id">
                  <td>
                    <strong>{{ row.name }}</strong>
                    <span>{{ row.email }}</span>
                  </td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.contactStatus)}`">{{ formatActivationState(row.contactStatus) }}</span></td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.emailUniquenessStatus)}`">{{ formatActivationState(row.emailUniquenessStatus) }}</span></td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.invitationStatus)}`">{{ formatActivationState(row.invitationStatus) }}</span></td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.redemptionStatus)}`">{{ formatActivationState(row.redemptionStatus) }}</span></td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.externalIdentityStatus)}`">{{ formatActivationState(row.externalIdentityStatus) }}</span></td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.webRoleStatus)}`">{{ formatActivationState(row.webRoleStatus) }}</span></td>
                  <td><span class="state-chip" :class="`state-chip--${activationStateTone(row.assignmentStatus)}`">{{ row.activeAssignmentCount }} active</span></td>
                  <td>
                    <span class="state-chip" :class="`state-chip--${nextActionTone(row.nextAction)}`">{{ row.nextAction }}</span>
                    <small class="activation-detail">{{ row.detail }}</small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <section v-if="!activationDiagnosticsLoading && !activationDiagnosticsError && activationDiagnostics.length === 0" class="empty-state empty-state--inline" aria-label="No activation diagnostics">
            <ShieldCheck class="guidance-icon" aria-hidden="true" />
            <h2>No activation records to review</h2>
            <p>Create or assign users before checking activation status.</p>
          </section>
        </section>

        <section v-else-if="activeSystemActivitySection === 'submissions'" class="access-activity-panel" role="tabpanel" aria-label="Submission activity">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Submissions</p>
              <h2>Collection and projection signals</h2>
              <p>Submission events are summarized from current workspace, local drafts, and reporting error state.</p>
            </div>
          </header>
          <section class="access-activity-list" aria-label="Submission activity list">
            <article v-for="event in systemActivitySubmissionEvents" :key="event.id" class="system-activity-row">
              <span class="state-chip" :class="`state-chip--${systemActivityTone(event.severity)}`">{{ event.status }}</span>
              <div>
                <strong>{{ event.action }}</strong>
                <small>{{ event.component }}</small>
              </div>
              <div>
                <p>{{ event.detail }}</p>
                <small>{{ event.target }}</small>
              </div>
              <div>
                <strong>Next action</strong>
                <small>{{ event.nextAction }}</small>
              </div>
            </article>
          </section>
          <section v-if="systemActivitySubmissionEvents.length === 0" class="empty-state empty-state--inline" aria-label="No submission events">
            <h2>No submission events</h2>
            <p>No submission or projection issues are visible in the current browser state.</p>
          </section>
        </section>

        <section v-else class="access-activity-panel" role="tabpanel" aria-label="Integration activity">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Integrations</p>
              <h2>Mailbox, exports, and Power BI status</h2>
              <p>Operational status for Microsoft services that sit outside the portal runtime.</p>
            </div>
          </header>
          <section class="access-readiness-note" role="note">
            <Database class="guidance-icon" aria-hidden="true" />
            <div>
              <strong>Platform logs remain external</strong>
              <p>Use CRDB-controlled Power Pages diagnostics, Dataverse auditing, Power Automate run history, Purview, or Application Insights for low-level traces.</p>
            </div>
          </section>
          <section class="access-activity-list" aria-label="Integration activity list">
            <article v-for="event in systemActivityIntegrationEvents" :key="event.id" class="system-activity-row">
              <span class="state-chip" :class="`state-chip--${systemActivityTone(event.severity)}`">{{ event.status }}</span>
              <div>
                <strong>{{ event.action }}</strong>
                <small>{{ event.component }}</small>
              </div>
              <div>
                <p>{{ event.detail }}</p>
                <small>{{ event.target }}</small>
              </div>
              <div>
                <strong>Next action</strong>
                <small>{{ event.nextAction }}</small>
              </div>
            </article>
          </section>
        </section>
      </section>
    </template>

    <template v-else-if="activeView === 'access'">
      <section v-if="!canManageAccess" class="empty-state" aria-label="User and Access denied">
        <ShieldCheck class="guidance-icon" aria-hidden="true" />
        <h2>You do not have access to User &amp; Access</h2>
        <p>This administration route is available only to users with an approved Power Pages administrator role.</p>
        <p v-if="accessRouteDenied" class="workflow-helper">A direct request for this administration route was blocked for the current session.</p>
        <dl class="access-authorization-list" aria-label="Access authorisation details">
          <div>
            <dt>Decision source</dt>
            <dd>{{ accessAuthorizationSourceLabel }}</dd>
          </div>
          <div>
            <dt>Required role</dt>
            <dd>{{ requiredAccessRoleLabel }}</dd>
          </div>
          <div>
            <dt>Detected roles</dt>
            <dd>{{ detectedAccessRoleLabel }}</dd>
          </div>
        </dl>
        <button class="icon-action icon-action--secondary" type="button" aria-label="Return to projects" @click="backToProjects">
          <ArrowLeft class="action-icon" aria-hidden="true" />
          Return to projects
        </button>
      </section>

      <section v-else class="access-workspace" aria-label="User and Access workspace">
        <header class="admin-section-header admin-section-header--compact">
          <div>
            <p class="eyebrow">Access workspace</p>
            <p>Create users, assign forms, and manage access actions.</p>
          </div>
          <div class="access-authorization-card" role="status" aria-label="Access authorisation source">
            <span>Signed in as</span>
            <strong>{{ matchedAccessRoleLabel }}</strong>
            <small>{{ accessAuthorizationSourceLabel }}</small>
          </div>
        </header>

        <section class="access-metric-strip" aria-label="Access summary">
          <article class="metric-card metric-card--accent">
            <span class="metric-value">{{ accessUsers.length }}</span>
            <span class="metric-label">Users in scope</span>
          </article>
          <article class="metric-card">
            <span class="metric-value">{{ activeAccessUserCount }}</span>
            <span class="metric-label">Active access</span>
          </article>
          <article class="metric-card">
            <span class="metric-value">{{ contactCheckCount }}</span>
            <span class="metric-label">Needs review</span>
          </article>
        </section>

        <section v-if="accessError" class="status-banner status-banner--error" aria-live="polite">
          {{ accessError }}
        </section>

        <section
          v-if="accessWorkflowOutcome"
          id="access-onboarding-outcome"
          class="access-outcome-panel"
          :class="`access-outcome-panel--${accessWorkflowOutcome.tone}`"
          role="status"
          aria-live="polite"
          aria-label="Create invite and assign outcome"
        >
          <div>
            <p class="eyebrow">Onboarding result</p>
            <h2>{{ accessWorkflowOutcome.title }}</h2>
            <p>{{ accessWorkflowOutcome.message }}</p>
            <dl class="access-preview-list access-preview-list--compact">
              <div v-if="accessWorkflowOutcome.email">
                <dt>User</dt>
                <dd>{{ accessWorkflowOutcome.email }}</dd>
              </div>
              <div>
                <dt>Time</dt>
                <dd>{{ formatDate(accessWorkflowOutcome.occurredAt) }}</dd>
              </div>
            </dl>
            <ul v-if="accessWorkflowOutcome.details.length > 0" class="access-outcome-details">
              <li v-for="detail in accessWorkflowOutcome.details" :key="detail">{{ detail }}</li>
            </ul>
          </div>
          <button class="icon-action icon-action--secondary" type="button" aria-label="Dismiss onboarding result" @click="clearAccessWorkflowOutcome">
            Close
          </button>
        </section>

        <nav class="material-tabs access-tabs" aria-label="User and Access sections">
          <button
            class="material-tab"
            :class="{ 'material-tab--active': activeAccessSection === 'users' }"
            type="button"
            :aria-current="activeAccessSection === 'users' ? 'page' : undefined"
            @click="setAccessSection('users')"
          >
            Users
          </button>
          <button
            class="material-tab"
            :class="{ 'material-tab--active': activeAccessSection === 'add' }"
            type="button"
            :aria-current="activeAccessSection === 'add' ? 'page' : undefined"
            @click="setAccessSection('add')"
          >
            Add user
          </button>
        </nav>

        <section v-if="activeAccessSection === 'users'" class="access-tab-panel" role="tabpanel" aria-label="Users">
          <section class="access-list-surface" aria-labelledby="access-users-title">
            <header class="access-list-header">
              <div>
                <p class="eyebrow">Users</p>
                <h3 id="access-users-title">Portal users</h3>
                <p>Review contacts, role scope, project assignments, form access, and activation state.</p>
              </div>
              <span class="access-list-count">{{ filteredAccessUsers.length }} shown</span>
            </header>

            <section class="access-toolbar" aria-label="User access filters">
              <label class="filter-field">
                <span>Role</span>
                <select v-model="accessRoleFilter">
                  <option value="">All roles</option>
                  <option v-for="role in accessRoleOptions" :key="role" :value="role">{{ role }}</option>
                </select>
              </label>
              <label class="record-search">
                <Search class="record-search__icon" aria-hidden="true" />
                <span class="sr-only">Search users</span>
                <input v-model="accessSearch" type="search" autocomplete="off" placeholder="Search users" aria-label="Search users">
              </label>
            </section>

            <section v-if="accessLoading" class="loading-panel loading-panel--inline access-loading-state" aria-live="polite" aria-label="Loading users">
              <h2>Loading users</h2>
              <p>Checking assignments and contacts.</p>
              <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
            </section>

            <div v-else-if="filteredAccessUsers.length > 0" class="responsive-table access-table" role="region" aria-label="User access table" tabindex="0">
              <table>
                <caption class="sr-only">Portal users with contact state, role, project count, form count, access state, and row actions.</caption>
                <thead>
                  <tr>
                    <th scope="col">User</th>
                    <th scope="col">Contact</th>
                    <th scope="col">Role</th>
                    <th scope="col">Projects</th>
                    <th scope="col">Forms</th>
                    <th scope="col">Access</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in filteredAccessUsers" :key="user.id" tabindex="0">
                    <td>
                      <strong>{{ user.name }}</strong>
                      <span>{{ user.email }}</span>
                    </td>
                    <td>
                      <span class="state-chip" :class="`state-chip--${contactStateTone(user.contactState)}`">{{ formatContactState(user.contactState) }}</span>
                    </td>
                    <td>{{ user.role }}</td>
                    <td class="access-table__number">{{ user.projectCount }}</td>
                    <td class="access-table__number">{{ user.formCount }}</td>
                    <td>
                      <span class="state-chip" :class="`state-chip--${accessStatusTone(user.accessStatus)}`">{{ user.accessStatus }}</span>
                    </td>
                    <td>
                      <div class="table-actions">
                        <details class="access-row-menu">
                          <summary aria-label="More actions">
                            <MoreVertical class="action-icon" aria-hidden="true" />
                            <span class="action-tooltip" role="tooltip">More actions</span>
                          </summary>
                          <div class="access-row-menu__items" role="menu">
                            <button type="button" role="menuitem" @click="openAccessUser(user)">
                              <Eye class="action-icon" aria-hidden="true" />
                              Manage access
                            </button>
                            <button type="button" role="menuitem" @click="openResendInvitationWorkflow(user)">
                              <Mail class="action-icon" aria-hidden="true" />
                              Resend invitation
                            </button>
                          </div>
                        </details>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <section v-if="!accessLoading && filteredAccessUsers.length > 0" class="access-card-list" aria-label="User access cards">
              <article v-for="user in filteredAccessUsers" :key="`card:${user.id}`" class="access-user-card">
                <header class="access-user-card__header">
                  <div>
                    <p class="eyebrow">User</p>
                    <h3>{{ user.name }}</h3>
                    <p>{{ user.email }}</p>
                  </div>
                  <span class="state-chip" :class="`state-chip--${accessStatusTone(user.accessStatus)}`">{{ user.accessStatus }}</span>
                </header>
                <dl class="access-card-facts">
                  <div>
                    <dt>Contact</dt>
                    <dd>
                      <span class="state-chip" :class="`state-chip--${contactStateTone(user.contactState)}`">{{ formatContactState(user.contactState) }}</span>
                    </dd>
                  </div>
                  <div>
                    <dt>Role</dt>
                    <dd>{{ user.role }}</dd>
                  </div>
                  <div>
                    <dt>Projects</dt>
                    <dd>{{ user.projectCount }}</dd>
                  </div>
                  <div>
                    <dt>Forms</dt>
                    <dd>{{ user.formCount }}</dd>
                  </div>
                </dl>
                <div class="access-card-actions">
                  <button type="button" class="icon-action icon-action--secondary" @click="openAccessUser(user)">
                    <Eye class="action-icon" aria-hidden="true" />
                    Manage access
                  </button>
                  <button type="button" class="icon-action icon-action--secondary" @click="openResendInvitationWorkflow(user)">
                    <Mail class="action-icon" aria-hidden="true" />
                    Resend invitation
                  </button>
                </div>
              </article>
            </section>

            <section v-if="!accessLoading && !accessError && filteredAccessUsers.length === 0" class="empty-state empty-state--inline access-empty-state" aria-label="No users">
              <Users class="guidance-icon" aria-hidden="true" />
              <h2>No users match the current filters</h2>
              <p>Clear search or role filters to review all assigned users.</p>
            </section>
          </section>
        </section>

        <button
          v-if="activeAccessSection === 'users' && selectedAccessUser"
          class="access-drawer-scrim"
          type="button"
          aria-label="Close user detail"
          @click="closeAccessUser"
        />

        <aside
          v-if="activeAccessSection === 'users' && selectedAccessUser"
          class="access-detail-drawer"
          role="dialog"
          aria-modal="true"
          aria-labelledby="access-detail-title"
        >
          <header class="access-drawer-header">
            <div>
              <p class="eyebrow">User detail</p>
              <h3 id="access-detail-title">{{ selectedAccessUser.name }}</h3>
              <p>{{ selectedAccessUser.email }}</p>
            </div>
            <button class="icon-action icon-action--secondary" type="button" @click="closeAccessUser">Close</button>
          </header>
          <dl class="access-detail-list">
            <div>
              <dt>Contact state</dt>
              <dd>{{ formatContactState(selectedAccessUser.contactState) }}</dd>
            </div>
            <div>
              <dt>Role</dt>
              <dd>{{ selectedAccessUser.role }}</dd>
            </div>
            <div>
              <dt>Access status</dt>
              <dd>{{ selectedAccessUser.accessStatus }}</dd>
            </div>
            <div>
              <dt>Assigned forms</dt>
              <dd>{{ selectedAccessUser.formCount }}</dd>
            </div>
          </dl>
          <section class="access-detail-actions" aria-label="Access change actions">
            <button class="icon-action icon-action--secondary" type="button" @click="openAccessChangeAction('email')">
              <Pencil class="action-icon" aria-hidden="true" />
              Correct email
              <span class="action-status-badge">{{ accessWriteActionStatus }}</span>
            </button>
            <button class="icon-action icon-action--secondary" type="button" @click="openAccessChangeAction('role')">
              <UserCog class="action-icon" aria-hidden="true" />
              Change role
              <span class="action-status-badge">{{ accessWriteActionStatus }}</span>
            </button>
            <button class="icon-action icon-action--secondary" type="button" @click="openAccessChangeAction('suspend')">
              <ShieldCheck class="action-icon" aria-hidden="true" />
              Remove access
              <span class="action-status-badge">{{ accessWriteActionStatus }}</span>
            </button>
            <button class="icon-action icon-action--secondary" type="button" @click="openAccessChangeAction('reactivate')">
              <Check class="action-icon" aria-hidden="true" />
              Reactivate access
              <span class="action-status-badge">{{ accessWriteActionStatus }}</span>
            </button>
          </section>
          <section
            v-if="selectedAccessAction"
            class="access-confirm-panel"
            aria-labelledby="access-confirm-title"
            aria-describedby="access-confirm-description"
          >
            <header>
              <p class="eyebrow">Confirmation</p>
              <h4 id="access-confirm-title">Confirm access change</h4>
              <p id="access-confirm-description">Review the target change before it is submitted through the approved access and audit path.</p>
            </header>

            <label v-if="selectedAccessAction === 'role'" class="filter-field">
              <span>Target role</span>
              <select v-model="accessChangeRole">
                <option v-for="role in accessWorkflowRoleOptions" :key="role" :value="role">{{ role }}</option>
              </select>
            </label>

            <label v-if="selectedAccessAction === 'email'" class="filter-field">
              <span>Corrected email</span>
              <input v-model="accessChangeEmail" type="email" autocomplete="email" placeholder="name@crdbbank.co.tz">
            </label>

            <dl class="access-confirm-grid">
              <div>
                <dt>User</dt>
                <dd>{{ selectedAccessUser.email }}</dd>
              </div>
              <div>
                <dt>Action</dt>
                <dd>{{ accessChangeActionLabel }}</dd>
              </div>
              <div>
                <dt>Current state</dt>
                <dd>{{ selectedAccessUser.role }} · {{ selectedAccessUser.accessStatus }}</dd>
              </div>
              <div>
                <dt>Requested change</dt>
                <dd>{{ accessChangeSummary }}</dd>
              </div>
            </dl>

            <label class="filter-field access-change-reason">
              <span>Reason for change</span>
              <textarea v-model="accessChangeReason" rows="3" placeholder="Capture the business reason before this action is enabled."></textarea>
            </label>

            <div class="export-note" role="note">
              <ShieldCheck class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>Audit-first change</strong>
                <p>Email correction updates the contact email and active assignment keys. Remove access marks active assignment rows inactive without deleting contacts.</p>
              </div>
            </div>
            <div class="access-readiness-note" role="note">
              <Settings class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>Permission model required</strong>
                <p>Apply requires the Platform Administrator web role, Web API write settings for contacts and form assignments, and audit-table create permission.</p>
              </div>
            </div>

            <p v-if="accessChangeError" class="status-banner status-banner--error" role="alert">
              {{ accessChangeError }}
            </p>
            <p v-if="accessChangeMessage" class="status-banner status-banner--success" role="status">
              {{ accessChangeMessage }}
            </p>

            <section v-if="selectedAccessWritePreview" class="access-preview-payload" aria-label="Generated access write preview">
              <header>
                <p class="eyebrow">Generated preview</p>
                <h5>Audit and mutation payload</h5>
                <p>{{ selectedAccessWritePreview.disabledReason }}</p>
              </header>
              <dl class="access-preview-list access-preview-list--compact">
                <div>
                  <dt>Request id</dt>
                  <dd>{{ selectedAccessWritePreview.requestId }}</dd>
                </div>
                <div>
                  <dt>Audit key</dt>
                  <dd>{{ selectedAccessWritePreview.auditKey }}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{{ selectedAccessWritePreview.statusLabel }}</dd>
                </div>
                <div>
                  <dt>Actor</dt>
                  <dd>{{ selectedAccessWritePreview.auditPayload.ActorEmail }}</dd>
                </div>
              </dl>
              <details>
                <summary>Audit payload</summary>
                <pre>{{ formatAccessPreviewJson(selectedAccessWritePreview.auditPayload) }}</pre>
              </details>
              <details>
                <summary>Later mutation payload</summary>
                <pre>{{ formatAccessPreviewJson(selectedAccessWritePreview.mutationPayload) }}</pre>
              </details>
            </section>

            <footer class="access-workflow-actions">
              <button class="icon-action icon-action--secondary" type="button" @click="closeAccessChangeAction">
                <ArrowLeft class="action-icon" aria-hidden="true" />
                Cancel
              </button>
              <button
                class="icon-action"
                type="button"
                :disabled="!accessChangeCanApply"
                :aria-label="accessChangeCanApply ? 'Apply access change' : 'Complete access change details before applying'"
                @click="applySelectedAccessChange"
              >
                <ShieldCheck class="action-icon" aria-hidden="true" />
                {{ accessChangeSubmitting ? 'Applying' : accessChangeCanApply ? 'Apply change' : 'Complete review' }}
              </button>
            </footer>
          </section>
          <section class="access-assignment-list" aria-label="Assigned forms">
            <header class="access-assignment-header">
              <div>
                <p class="eyebrow">Assignments</p>
                <h4>Project and form access</h4>
              </div>
              <span class="state-chip state-chip--neutral">{{ selectedAccessUser.formCount }} forms</span>
            </header>
            <article v-for="assignment in selectedAccessUser.assignments" :key="assignment.assignmentId" class="access-assignment-row">
              <div>
                <strong>{{ assignment.formName }}</strong>
                <span>{{ selectedAccessProjectName }}</span>
              </div>
              <dl>
                <div>
                  <dt>Version</dt>
                  <dd>{{ assignment.version }}</dd>
                </div>
                <div>
                  <dt>XML form</dt>
                  <dd>{{ assignment.xmlFormId }}</dd>
                </div>
              </dl>
            </article>
          </section>
          <section class="access-drawer-activity" aria-label="Selected user activity">
            <header class="access-assignment-header">
              <div>
                <p class="eyebrow">Audit preview</p>
                <h4>User activity</h4>
              </div>
              <span class="state-chip state-chip--neutral">{{ selectedAccessUserActivity.length }} events</span>
            </header>
            <article v-for="event in selectedAccessUserActivity" :key="event.id" class="access-activity-row access-activity-row--compact">
              <span class="state-chip" :class="`state-chip--${event.status}`">{{ event.event }}</span>
              <p>{{ event.detail }}</p>
              <small>{{ event.source }}</small>
            </article>
          </section>
          <div class="export-note" role="note">
            <ShieldCheck class="guidance-icon" aria-hidden="true" />
            <div>
              <strong>Read-only slice</strong>
              <p>Role changes, invitations, suspension, and assignment writes are intentionally disabled until the permission model and audit path are packaged.</p>
            </div>
          </div>
        </aside>

        <section v-if="activeAccessSection === 'roles'" class="role-reference-panel" aria-labelledby="role-reference-title" role="tabpanel" aria-label="Roles">
          <header>
            <p class="eyebrow">Roles</p>
            <h3 id="role-reference-title">Role reference</h3>
          </header>
          <article v-for="role in accessRoleReference" :key="role.role" class="role-reference-row">
            <strong>{{ role.role }}</strong>
            <span>{{ role.summary }}</span>
          </article>
        </section>

        <section v-if="activeAccessSection === 'activity'" class="access-activity-panel" role="tabpanel" aria-label="Activity">
          <header class="section-heading">
            <div>
              <p class="eyebrow">Audit preview</p>
              <h3>Access activity</h3>
              <p>Preview how access changes and contact checks will be reviewed before write actions are enabled.</p>
            </div>
          </header>
          <div class="export-note" role="note">
            <ShieldCheck class="guidance-icon" aria-hidden="true" />
            <div>
              <strong>Read-only audit preview</strong>
              <p>These rows are derived from current assignments and contact state. They are not persisted audit records yet.</p>
            </div>
          </div>
          <section class="access-activity-list" aria-label="Access activity events">
            <article v-for="event in accessActivityEvents" :key="event.id" class="access-activity-row">
              <span class="state-chip" :class="`state-chip--${event.status}`">{{ event.event }}</span>
              <div>
                <strong>{{ event.userName }}</strong>
                <span>{{ event.userEmail }}</span>
              </div>
              <p>{{ event.detail }}</p>
              <small>{{ event.source }}</small>
            </article>
          </section>
          <section v-if="accessActivityEvents.length === 0" class="empty-state empty-state--inline" aria-label="No access activity">
            <ShieldCheck class="guidance-icon" aria-hidden="true" />
            <h2>No activity to preview</h2>
            <p>Load user assignments to review derived access activity.</p>
          </section>
        </section>

        <section v-if="activeAccessSection === 'configuration'" class="access-readiness-panel" role="tabpanel" aria-label="Configuration">
          <header class="section-heading">
            <div>
              <p class="eyebrow">System status</p>
              <h3>Production status</h3>
              <p>Check the few gates that affect user creation and assignment.</p>
            </div>
          </header>
          <div class="access-readiness-note" role="note">
            <ShieldCheck class="guidance-icon" aria-hidden="true" />
            <div>
              <strong>{{ accessWriteReadiness.statusLabel }}</strong>
              <p>{{ accessWriteReadiness.disabledReason || 'Access writes use the approved queue, audit, and permission path.' }}</p>
            </div>
          </div>
          <section class="notification-settings-card" aria-labelledby="notification-settings-title">
            <header class="notification-settings-header">
              <div>
                <p class="eyebrow">Notifications</p>
                <h4 id="notification-settings-title">Onboarding delivery</h4>
                <p>Choose how new-user invitations are delivered after the processor creates contact and access records.</p>
              </div>
              <span class="state-chip state-chip--neutral">{{ notificationSourceLabel }}</span>
            </header>

            <div class="notification-current-state">
              <div>
                <span>Active mode</span>
                <strong>{{ notificationDeliveryModeLabel }}</strong>
              </div>
              <div>
                <span>Mailbox status</span>
                <strong>{{ notificationMailboxStatusLabel }}</strong>
              </div>
            </div>

            <fieldset class="notification-mode-options">
              <legend>Delivery mode</legend>
              <label class="notification-mode-option">
                <input v-model="notificationDeliveryMode" type="radio" value="manual-code" />
                <span>
                  <strong>Manual invitation code</strong>
                  <small>Admin copies the redeem link and code from the portal and shares through an approved internal channel.</small>
                </span>
              </label>
              <label class="notification-mode-option" :class="{ 'notification-mode-option--disabled': !notificationEmailModeReady }">
                <input v-model="notificationDeliveryMode" type="radio" value="email" :disabled="!notificationEmailModeReady" />
                <span>
                  <strong>Mailbox email delivery</strong>
                  <small>Available after a CRDB-approved sender mailbox is approved, tested, and enabled.</small>
                </span>
              </label>
            </fieldset>

            <div class="notification-settings-form">
              <label class="filter-field">
                <span>Sender mailbox</span>
                <input v-model="notificationSenderMailbox" type="email" autocomplete="email" placeholder="noreply@example.com" />
              </label>
              <label class="filter-field">
                <span>Mailbox status</span>
                <select v-model="notificationMailboxStatus">
                  <option value="not-configured">Not configured</option>
                  <option value="pending-admin-setup">Pending admin setup</option>
                  <option value="approved">Approved</option>
                  <option value="tested-and-enabled">Tested and enabled</option>
                  <option value="failed">Failed</option>
                </select>
              </label>
              <label class="filter-field">
                <span>Send Invitation workflow id</span>
                <input v-model="notificationWorkflowId" type="text" placeholder="Workflow id" />
              </label>
              <label class="filter-field notification-settings-form__wide">
                <span>Last test result</span>
                <textarea v-model="notificationLastTestResult" rows="3" placeholder="Mailbox approval or delivery smoke-test note"></textarea>
              </label>
              <label class="filter-field notification-settings-form__wide">
                <span>Admin instruction</span>
                <textarea v-model="notificationInstructions" rows="3" placeholder="Operational instruction shown to administrators"></textarea>
              </label>
            </div>

            <div class="notification-setup-checklist" aria-label="Mailbox setup checklist">
              <article>
                <span class="state-chip state-chip--warning">admin</span>
                <p>Create or identify the shared/service mailbox in Microsoft 365.</p>
              </article>
              <article>
                <span class="state-chip state-chip--warning">admin</span>
                <p>Approve the Dataverse mailbox and run Test & Enable in Power Platform admin center.</p>
              </article>
              <article>
                <span class="state-chip state-chip--warning">processor</span>
                <p>Processor uses email mode only after delivery status is recorded as Tested and enabled.</p>
              </article>
            </div>

            <p v-if="notificationError" class="status-banner status-banner--error" role="alert">{{ notificationError }}</p>
            <p v-if="notificationMessage" class="status-banner status-banner--success" role="status">{{ notificationMessage }}</p>
            <div class="access-workflow-actions access-workflow-actions--inline access-workflow-actions--result">
              <button class="icon-action" type="button" :disabled="!notificationCanSave" @click="saveNotificationDeliverySetting">
                <Save class="action-icon" aria-hidden="true" />
                {{ notificationSaving ? 'Saving' : 'Save delivery settings' }}
              </button>
              <button class="icon-action icon-action--secondary" type="button" :disabled="notificationLoading || notificationSaving" @click="loadNotificationDeliverySetting">
                <RefreshCw class="action-icon" aria-hidden="true" />
                Refresh
              </button>
            </div>
          </section>
          <section class="access-authorization-panel" aria-label="Access route authorisation">
            <header>
              <p class="eyebrow">Route guard</p>
              <h4>Authorisation</h4>
            </header>
            <dl class="access-authorization-list">
              <div>
                <dt>Decision source</dt>
                <dd>{{ accessAuthorizationSourceLabel }}</dd>
              </div>
              <div>
                <dt>Required role</dt>
                <dd>{{ requiredAccessRoleLabel }}</dd>
              </div>
              <div>
                <dt>Detected roles</dt>
                <dd>{{ detectedAccessRoleLabel }}</dd>
              </div>
              <div>
                <dt>Matched admin role</dt>
                <dd>{{ matchedAccessRoleLabel }}</dd>
              </div>
            </dl>
          </section>
          <section class="access-readiness-list" aria-label="Write-path status checklist">
            <article v-for="gate in accessWriteReadiness.requiredGates" :key="gate" class="access-readiness-row">
              <span class="state-chip state-chip--warning">required</span>
              <div>
                <strong>Required</strong>
                <p>{{ gate }}</p>
              </div>
            </article>
          </section>
        </section>

        <aside
          v-if="activeAccessSection === 'add' && accessWorkflowOpen"
          class="access-workflow-panel"
          aria-labelledby="access-workflow-title"
          aria-describedby="access-workflow-description"
          role="tabpanel"
          aria-label="Add user"
        >
          <header class="record-detail-header">
            <div>
              <p class="eyebrow">Access workflow</p>
              <h3 id="access-workflow-title">Create, invite and assign</h3>
              <p id="access-workflow-description">Add a user to a project form through the governed onboarding queue.</p>
            </div>
            <button class="icon-action icon-action--secondary" type="button" @click="closeAccessWorkflow">Close</button>
          </header>

          <nav class="access-stepper" aria-label="Add user steps">
            <button
              v-for="step in accessWorkflowSteps"
              :key="step.id"
              class="access-step"
              :class="{ 'access-step--active': accessWorkflowStep === step.id, 'access-step--complete': accessWorkflowStep > step.id }"
              type="button"
              :aria-current="accessWorkflowStep === step.id ? 'step' : undefined"
              @click="setAccessWorkflowStep(step.id)"
            >
              <span>{{ step.id }}</span>
              <small>{{ step.label }}</small>
            </button>
          </nav>

          <section v-if="accessWorkflowStep === 1" class="access-workflow-step" aria-label="User email">
            <h4>User details</h4>
            <label class="filter-field">
              <span>Full name</span>
              <input v-model="accessWorkflowFullName" type="text" autocomplete="name" placeholder="Full name">
            </label>
            <label class="filter-field">
              <span>Microsoft account email</span>
              <input v-model="accessWorkflowEmail" type="email" autocomplete="email" placeholder="name@example.com">
            </label>
            <div v-if="accessWorkflowEmailNormalized" class="workflow-status-card workflow-status-card--compact">
              <span class="state-chip" :class="`state-chip--${contactStateTone(accessWorkflowContactState)}`">
                {{ accessWorkflowIsExistingUser ? 'Existing user' : 'New user' }}
              </span>
              <strong>{{ accessWorkflowOnboardingLabel }}</strong>
              <p>{{ accessWorkflowExistingUser ? 'Assign access and notify.' : 'Create contact, invitation, and assignment.' }}</p>
            </div>
          </section>

          <section v-else-if="accessWorkflowStep === 2" class="access-workflow-step" aria-label="Role selection">
            <h4>Role</h4>
            <label class="filter-field">
              <span>Role</span>
              <select v-model="accessWorkflowRole">
                <option v-for="role in accessWorkflowRoleOptions" :key="role" :value="role">{{ role }}</option>
              </select>
            </label>
          </section>

          <section v-else-if="accessWorkflowStep === 3" class="access-workflow-step" aria-label="Project and form access">
            <h4>Project and form access</h4>
            <label class="filter-field">
              <span>Project</span>
              <select :value="accessWorkflowProjectId" @change="handleAccessWorkflowProjectChange">
                <option v-for="project in projectWorkspaces" :key="project.id" :value="project.id">{{ project.name }}</option>
              </select>
            </label>
            <fieldset class="form-check-list">
              <legend>Forms</legend>
              <label v-for="assignment in accessWorkflowSelectedProject?.assignments ?? []" :key="assignment.formVersionId" class="form-check-row">
                <input
                  type="checkbox"
                  :checked="accessWorkflowFormVersionIds.includes(assignment.formVersionId)"
                  @change="toggleAccessWorkflowForm(assignment.formVersionId)"
                >
                <span>
                  <strong>{{ assignment.formName }}</strong>
                  <small>Version {{ assignment.version }} · {{ assignment.xmlFormId }}</small>
                </span>
              </label>
            </fieldset>
          </section>

          <section v-else class="access-workflow-step" aria-label="Confirmation preview">
            <h4>Review and send</h4>
            <label class="filter-field access-change-reason">
              <span>Business reason</span>
              <textarea v-model="accessWorkflowReason" rows="3" placeholder="Capture the approved business reason before activation."></textarea>
            </label>
            <dl class="access-preview-list">
              <div>
                <dt>Workflow</dt>
                <dd>{{ accessWorkflowOnboardingLabel }}</dd>
              </div>
              <div>
                <dt>Name</dt>
                <dd>{{ accessWorkflowFullName }}</dd>
              </div>
              <div>
                <dt>User</dt>
                <dd>{{ accessWorkflowEmailNormalized }}</dd>
              </div>
              <div>
                <dt>Contact</dt>
                <dd>{{ formatContactState(accessWorkflowContactState) }}</dd>
              </div>
              <div>
                <dt>Role</dt>
                <dd>{{ accessWorkflowRole }}</dd>
              </div>
              <div>
                <dt>Project</dt>
                <dd>{{ accessWorkflowSelectedProject?.name || 'No project selected' }}</dd>
              </div>
              <div>
                <dt>Forms</dt>
                <dd>{{ accessWorkflowSelectedForms.length }}</dd>
              </div>
              <div>
                <dt>Reason</dt>
                <dd>{{ accessWorkflowReasonText }}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>{{ accessWorkflowDeliveryLabel }}</dd>
              </div>
            </dl>
            <section class="assignform-readiness-panel" aria-labelledby="onboarding-readiness-title">
              <header>
                <p class="eyebrow">System check</p>
                <h5 id="onboarding-readiness-title">{{ userOnboardingReadiness.statusLabel }}</h5>
                <p>{{ userOnboardingReadiness.enabled ? 'Onboarding queue is enabled.' : userOnboardingReadiness.disabledReason }}</p>
              </header>
            </section>
            <div v-if="!userOnboardingReadiness.enabled" class="export-note" role="note">
              <ShieldCheck class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>Preview only</strong>
                <p>No records are created until the onboarding queue is enabled.</p>
              </div>
            </div>
            <div v-else class="export-note" role="note">
              <ShieldCheck class="guidance-icon" aria-hidden="true" />
              <div>
                <strong>Ready to queue</strong>
                <p>Dataverse will process contact, audit, assignment, and invitation records.</p>
              </div>
            </div>
            <p v-if="accessWorkflowSubmitError" class="status-banner status-banner--error" role="alert">
              {{ accessWorkflowSubmitError }}
            </p>
            <p v-if="accessWorkflowSubmitMessage" class="status-banner status-banner--success" role="status">
              {{ accessWorkflowSubmitMessage }}
            </p>
            <section v-if="accessWorkflowSubmitResults.length > 0" class="access-preview-payload" aria-label="Access creation results">
              <header>
                <p class="eyebrow">Result</p>
                <h5>Assignment write outcome</h5>
                <p v-if="accessWorkflowOnboardingResult">
                  Queue request {{ accessWorkflowOnboardingResult.requestId }}:
                  {{ accessWorkflowOnboardingResult.emailMessage }}
                </p>
                <dl v-if="accessWorkflowOnboardingResult" class="access-preview-list access-preview-list--compact">
                  <div>
                    <dt>Email delivery</dt>
                    <dd>{{ accessWorkflowOnboardingResult.emailDelivery }}</dd>
                  </div>
                </dl>
              </header>
              <article v-for="result in accessWorkflowSubmitResults" :key="result.requestId" class="access-preview-record">
                <dl class="access-preview-list access-preview-list--compact">
                  <div>
                    <dt>Request id</dt>
                    <dd>{{ result.requestId }}</dd>
                  </div>
                  <div>
                    <dt>Status</dt>
                    <dd>{{ result.status }}</dd>
                  </div>
                  <div>
                    <dt>Audit key</dt>
                    <dd>{{ result.auditKey }}</dd>
                  </div>
                </dl>
              </article>
            </section>
            <section
              v-if="accessWorkflowOnboardingResult && accessWorkflowSubmitResults.length === 0"
              :class="['onboarding-result-panel', `onboarding-result-panel--${onboardingResultTone}`]"
              aria-label="Onboarding queue result"
            >
              <header class="onboarding-result-header">
                <div>
                  <p class="eyebrow">Result</p>
                  <h5>{{ onboardingResultTitle }}</h5>
                  <p>{{ onboardingPrimaryInstruction }}</p>
                </div>
                <span :class="['state-chip', `state-chip--${onboardingResultTone}`]">
                  {{ accessWorkflowOnboardingResult.queueStatus }}
                </span>
              </header>

              <ol class="onboarding-timeline" aria-label="Onboarding progress">
                <li
                  v-for="item in onboardingTimeline"
                  :key="item.id"
                  :class="['onboarding-timeline-item', `onboarding-timeline-item--${item.state}`]"
                >
                  <span>
                    <Check v-if="item.state === 'done'" class="action-icon" aria-hidden="true" />
                    <span v-else aria-hidden="true"></span>
                  </span>
                  <strong>{{ item.label }}</strong>
                </li>
              </ol>

              <div class="access-workflow-actions access-workflow-actions--inline access-workflow-actions--result">
                <button class="icon-action" type="button" :disabled="accessWorkflowSubmitting" @click="refreshOnboardingRequestResult">
                  <RefreshCw class="action-icon" aria-hidden="true" />
                  Refresh status
                </button>
                <button v-if="manualInvitationExpired" class="icon-action icon-action--secondary" type="button" :disabled="accessWorkflowSubmitting" @click="recreateExpiredInvitation">
                  <RefreshCw class="action-icon" aria-hidden="true" />
                  Create new invitation
                </button>
              </div>

              <section v-if="manualInvitationAvailable" class="manual-invitation-card" aria-label="Manual invitation fallback">
                <header>
                  <p class="eyebrow">Manual invitation</p>
                  <h5>{{ manualInvitationExpired ? 'Code expired' : 'Code ready' }}</h5>
                </header>
                <dl class="manual-invitation-grid">
                  <div>
                    <dt>Redeem link</dt>
                    <dd>{{ accessWorkflowOnboardingResult.invitationRedeemUrl }}</dd>
                  </div>
                  <div>
                    <dt>Invitation code</dt>
                    <dd>{{ accessWorkflowOnboardingResult.invitationCode }}</dd>
                  </div>
                  <div>
                    <dt>Expires</dt>
                    <dd>{{ accessWorkflowOnboardingResult.invitationExpiresAt ? formatDate(accessWorkflowOnboardingResult.invitationExpiresAt) : 'Not set' }}</dd>
                  </div>
                </dl>
                <div class="access-workflow-actions access-workflow-actions--inline">
                  <button class="icon-action icon-action--secondary" type="button" :disabled="manualInvitationExpired" @click="copyInvitationFallback('url')">
                    <Clipboard class="action-icon" aria-hidden="true" />
                    Copy redeem link
                  </button>
                  <button class="icon-action icon-action--secondary" type="button" :disabled="manualInvitationExpired" @click="copyInvitationFallback('code')">
                    <Clipboard class="action-icon" aria-hidden="true" />
                    Copy code
                  </button>
                </div>
                <p class="manual-invitation-warning">
                  Share only through an approved internal channel. The portal does not set passwords.
                </p>
                <p v-if="invitationCopyStatus" class="copy-status" aria-live="polite">{{ invitationCopyStatus }}</p>
              </section>

              <div v-else-if="accessWorkflowOnboardingResult.requestType === 'NewUser'" class="onboarding-pending-note" role="note">
                <ShieldCheck class="guidance-icon" aria-hidden="true" />
                <div>
                  <strong>Invitation details pending</strong>
                  <p>The processor will write the code and redeem link back to this request after creating the native invitation.</p>
                </div>
              </div>

              <details class="onboarding-technical-details">
                <summary>Technical details</summary>
                <dl class="access-preview-list access-preview-list--compact">
                  <div v-for="[label, value] in onboardingTechnicalSummary" :key="label">
                    <dt>{{ label }}</dt>
                    <dd>{{ value }}</dd>
                  </div>
                </dl>
              </details>
            </section>
          </section>

          <footer class="access-workflow-actions">
            <button class="icon-action icon-action--secondary" type="button" :disabled="accessWorkflowStep === 1" @click="previousAccessWorkflowStep">
              <ArrowLeft class="action-icon" aria-hidden="true" />
              Back
            </button>
            <button v-if="accessWorkflowStep < 4" class="icon-action" type="button" :disabled="!accessWorkflowCanProceed" @click="nextAccessWorkflowStep">
              Next
              <ChevronRight class="action-icon" aria-hidden="true" />
            </button>
            <button
              v-else
              class="icon-action"
              type="button"
              :disabled="!accessWorkflowCanSubmit"
              :aria-label="accessWorkflowCanSubmit ? 'Create user access' : 'Complete review before creating access'"
              @click="submitAccessWorkflow"
            >
              <ShieldCheck class="action-icon" aria-hidden="true" />
              {{ accessWorkflowSubmitting ? 'Creating access' : accessWorkflowCanSubmit ? 'Create access' : 'Complete review' }}
            </button>
          </footer>
        </aside>
      </section>
    </template>

    <section
      v-show="activeView === 'runner'"
      class="persistent-runner-view"
      :aria-hidden="activeView !== 'runner'"
      :inert="activeView !== 'runner' ? true : undefined"
      aria-label="Collect form workspace"
    >
      <section v-if="submitting" class="submit-overlay" aria-live="assertive" aria-label="Submitting record">
        <div class="submit-progress-panel" role="status">
          <img class="loading-logo" :src="crdbLogoUrl" alt="CRDB Bank">
          <h2>Submitting record</h2>
          <p>Saving to Dataverse</p>
          <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
        </div>
      </section>

      <section v-if="formRuntimeLoading" class="submit-overlay" aria-live="assertive" aria-label="Loading form">
        <div class="submit-progress-panel" role="status">
          <img class="loading-logo" :src="crdbLogoUrl" alt="CRDB Bank">
          <h2>Loading form</h2>
          <p>Preparing the form runtime</p>
          <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
        </div>
      </section>

      <section v-if="runtimeStatus || submitStatus" class="runner-status-stack" aria-live="polite">
        <p v-if="runtimeStatus" class="status-banner status-banner--success">{{ runtimeStatus }}</p>
        <p v-if="submitStatus" class="status-banner" :class="`status-banner--${submitTone}`">{{ submitStatus }}</p>
      </section>

      <section v-if="selectedAssignment" class="runner-shell" :aria-label="selectedVersionLabel">
        <section v-if="formRuntimeLoading" class="loading-panel loading-panel--runtime" aria-live="polite" aria-label="Loading form">
          <img class="loading-logo" :src="crdbLogoUrl" alt="CRDB Bank">
          <h2>Loading form</h2>
          <p>Preparing the form runtime</p>
          <span class="loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
        </section>
        <section v-if="formRuntimeMountReady && selectedAssignment.xformXml" class="odk-runtime-host" aria-label="ODK Web Forms runtime">
          <OdkWebForm
            :key="`${selectedAssignment.formVersionId}:${selectedEditSubmission?.submissionId || 'new'}`"
            :form-xml="selectedAssignment.xformXml"
            :edit-instance="editInstanceOptions"
            device-id="tacatdp-powerpages-poc"
            missing-resource-behavior="placeholder"
            @loaded="handleFormLoaded"
            @submit="handleSubmit"
            @submit-chunked="handleSubmit"
          />
        </section>

      </section>
    </section>
        </div>
        <footer class="managed-app-footer" aria-label="Application footer">
          <span class="managed-app-footer__status">
            <span>Last updated: May 31, 2025 10:45 AM</span>
            <span class="managed-app-footer__dot" aria-hidden="true"></span>
            <span>Data synced</span>
          </span>
          <span>© 2025 CRDB Bank — Sustainable Finance Unit. All rights reserved.</span>
        </footer>
      </section>
    </div>
  </main>
</template>
