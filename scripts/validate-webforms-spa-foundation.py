#!/usr/bin/env python3
"""Validate the TACATDP Power Pages WebForms SPA foundation slice."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPA = ROOT / "powerpages/webforms-spa"
SITE_SOURCE = ROOT / "powerpages/tacatdp-monitoring-tool/.powerpages-site"
SITE_UPLOAD = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool"
REQUIRED_FILES = [
    "package.json",
    "index.html",
    "vite.config.ts",
    "tsconfig.json",
    "src/main.ts",
    "src/App.vue",
    "src/views/AssignedFormsView.vue",
    "src/powerpages-api/client.ts",
    "src/powerpages-api/types.ts",
    "src/dev/assignedForms.ts",
    "src/dev/reporting.ts",
    "src/vite-env.d.ts",
    "src/types/getodk-web-forms.d.ts",
    "src/offline/drafts.ts",
    "src/styles.css",
]
FORBIDDEN_PATTERNS = [
    r"client_secret",
    r"Authorization\s*:",
    r"Bearer\s+",
    r"login\.microsoftonline\.com",
    r"/api/data/v9\.2",
]
REQUIRED_API_STRINGS = [
    "/_api/mp_formassignments",
    "/_api/mp_formversions",
    "/_api/mp_forms",
    "/_api/mp_formattachments",
    "/_api/mp_submissions",
    "/_api/mp_submissionversions",
    "/_api/mp_submissionattachments",
    "/_api/mp_submissionreportrows",
    "/_api/mp_submissionanswers",
    "/_api/mp_exportsettings",
    "__RequestVerificationToken",
    "getTokenDeferred",
    "mp_xformsubmissionxml",
    "mp_submissionjson",
    "mp_Submission@odata.bind",
    "mp_SubmissionVersion@odata.bind",
    "mp_file",
    "x-ms-file-name",
    "dataverse-file:",
    "/mp_file/$value",
    "formVersionId",
    "repeatPaths",
    "getElementsByTagNameNS('*', 'repeat')",
]
TEXT_SCAN_FILES = [
    "package.json",
    "index.html",
    "vite.config.ts",
    "tsconfig.json",
    "src/main.ts",
    "src/App.vue",
    "src/views/AssignedFormsView.vue",
    "src/powerpages-api/client.ts",
    "src/powerpages-api/types.ts",
    "src/dev/assignedForms.ts",
    "src/dev/reporting.ts",
    "src/vite-env.d.ts",
    "src/types/getodk-web-forms.d.ts",
    "src/offline/drafts.ts",
    "src/styles.css",
]
SEED_SCRIPT = ROOT / "scripts/dataverse-seed-odk-mvp-form.py"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def validate_seed_xform_body_refs() -> None:
    namespace: dict[str, object] = {}
    exec(SEED_SCRIPT.read_text(), namespace)
    xform = str(namespace["RICH_TACATDP_XFORM"])
    root = ET.fromstring(xform)
    body = root.find("{http://www.w3.org/1999/xhtml}body")
    if body is None:
        fail("seeded XForm is missing h:body")

    refs: dict[str, str] = {}
    duplicates: list[str] = []
    for element in body.iter():
        ref = element.attrib.get("ref")
        if not ref:
            continue
        tag = element.tag.rsplit("}", 1)[-1]
        if ref in refs:
            duplicates.append(ref)
        refs[ref] = tag

    if duplicates:
        fail(f"seeded XForm body has duplicate refs rejected by ODK Web Forms: {', '.join(sorted(set(duplicates)))}")


def validate_odk_style_isolation() -> None:
    css = (SPA / "src/styles.css").read_text()
    view = (SPA / "src/views/AssignedFormsView.vue").read_text()
    forbidden_css = [
        r"(?m)^button\s*\{",
        r"(?m)^\*\s*\{",
        r"\.runtime-panel\s+:where",
        r"\.runtime-panel\s+button",
        r"\.runtime-panel\s+input",
        r"\.runtime-panel\s+label",
        r"\.runtime-panel\s+select",
        r"\.runtime-panel\s+textarea",
    ]
    for pattern in forbidden_css:
        if re.search(pattern, css):
            fail(f"host shell CSS must not leak into ODK renderer controls: {pattern}")
    if "odk-runtime-host" not in css or "odk-runtime-host" not in view:
        fail("ODK renderer must be mounted in a dedicated odk-runtime-host boundary")
    if ".icon-action.icon-action--secondary" not in css:
        fail("Secondary icon actions must override the primary icon-action treatment")


def validate_powerpages_hosting() -> None:
    for site in (SITE_SOURCE, SITE_UPLOAD):
        if not site.exists():
            fail(f"missing Power Pages package {site.relative_to(ROOT)}")

        template = site / "page-templates/Monitoring-Tool-SPA.pagetemplate.yml"
        home = site / "web-pages/home/Home.webpage.copy.html"
        home_content_candidates = (
            site / "web-pages/home/content-pages/en-US/Home.webpage.copy.html",
            site / "web-pages/home/content-pages/Home.en-US.webpage.copy.html",
        )
        footer = site / "web-templates/footer/Footer.webtemplate.source.html"
        footer_snippet_candidates = (
            site / "content-snippets/footer/en-US/Footer.contentsnippet.value.html",
            site / "content-snippets/footer/Footer.en-US.contentsnippet.value.html",
        )
        if not template.exists():
            fail(f"missing {template.relative_to(ROOT)}")
        if not home.exists():
            fail(f"missing {home.relative_to(ROOT)}")
        if not footer.exists():
            fail(f"missing {footer.relative_to(ROOT)}")
        home_content = next((path for path in home_content_candidates if path.exists()), None)
        if home_content is None:
            fail(f"missing Home language content page under {site.relative_to(ROOT)}")

        template_text = template.read_text()
        home_texts = {
            home.relative_to(ROOT): home.read_text(),
            home_content.relative_to(ROOT): home_content.read_text(),
        }
        footer_text = footer.read_text()
        footer_snippet = next((path for path in footer_snippet_candidates if path.exists()), None)
        if footer_snippet is None:
            fail(f"missing footer content snippet under {site.relative_to(ROOT)}")
        footer_snippet_text = footer_snippet.read_text()
        if "usewebsiteheaderandfooter: true" not in template_text and "adx_usewebsiteheaderandfooter: true" not in template_text:
            fail("Monitoring Tool SPA page template must use the Power Pages header/footer runtime so shell.getTokenDeferred is available")
        for home_path, home_text in home_texts.items():
            for forbidden in ("<!doctype", "<html", "<head", "<body"):
                if forbidden in home_text.lower():
                    fail(f"Monitoring Tool Home copy must be a Power Pages page fragment, not a full HTML document: {home_path}")
            if "__TACATDP_POWERPAGES__" not in home_text:
                fail(f"Monitoring Tool Home copy missing Power Pages bootstrap: {home_path}")
            if "tacatdp-portal-chrome-reset" not in home_text:
                fail(f"Monitoring Tool Home copy must visually suppress default portal chrome: {home_path}")
            if not re.search(r'<script type="module"[^>]+src="/assets/index-[^"?]+\.mjs\?v=[^"]+"', home_text):
                fail(f"Monitoring Tool Home copy missing versioned module entry asset: {home_path}")
            if not re.search(r'<link rel="stylesheet"[^>]+href="/assets/index-[^"?]+\.css\?v=[^"]+"', home_text):
                fail(f"Monitoring Tool Home copy missing versioned stylesheet asset: {home_path}")
            asset_paths = re.findall(r'(?:href|src)="/assets/([^"?]+)', home_text)
            for asset_path in asset_paths:
                if not (site / "web-files" / asset_path).exists():
                    fail(f"Monitoring Tool Home copy references missing hosted asset {asset_path}: {home_path}")
        for required in (
            "mt-site-footer",
            "mt-site-footer__inner",
            "role=\"contentinfo\"",
            "(c) CRDB",
            "now | date: 'yyyy'",
            "width: min(1180px, 100%)",
            "justify-content: flex-end",
        ):
            if required not in footer_text:
                fail(f"Power Pages Footer shell template missing required Monitoring Tool footer contract: {required}")
        for forbidden in ("Copyright ©", "All rights reserved", "(c) CRDB"):
            if forbidden in footer_snippet_text:
                fail(f"Power Pages default footer content snippet must not render duplicate footer text: {footer_snippet.relative_to(ROOT)}")


def validate_powerpages_session_contract() -> None:
    view = (SPA / "src/views/AssignedFormsView.vue").read_text()
    client = (SPA / "src/powerpages-api/client.ts").read_text()
    drafts = (SPA / "src/offline/drafts.ts").read_text()
    xform_cache = (SPA / "src/offline/xform-cache.ts").read_text()
    performance = (SPA / "src/performance.ts").read_text()
    if '<header class="app-header">' in view:
        fail("SPA must not render a second CRDB/session header; use the Power Pages Header template for visible chrome")
    if 'class="app-footer"' in view:
        fail("SPA must not render the legacy copyright footer; use the managed shell footer")
    if "managed-app-footer" not in view:
        fail("SPA must render the integrated managed shell footer")
    if "managed-top-bar__switcher" not in view or "<Menu " not in view:
        fail("SPA managed shell must use one top-bar hamburger switcher")
    if "import { VueDatePicker } from '@vuepic/vue-datepicker';" in view:
        fail("Date picker must be lazy-loaded, not imported into the initial SPA bundle")
    if "await import('@vuepic/vue-datepicker')" not in view:
        fail("Date picker must remain available through an async component import")
    for required in (
        "type AppView = 'dashboard' | 'projects' | 'records' | 'runner' | 'access' | 'reporting' | 'system-activity' | 'roadmap'",
        "const activeView = ref<AppView>('dashboard')",
        "const activeAccessSection = ref<AccessSection>('users')",
        "const platformName = 'MEL Tool'",
        ':aria-label="platformName"',
        "{{ shellPageEyebrow }}",
        "shellPageEyebrow",
        "managed-top-bar__actions",
        "signedInUserName",
        "Use your Microsoft account to continue to the MEL Tool.",
        "Field Operations",
        "Results &amp; Reporting",
        "MEL Platform",
        "Beneficiaries",
        "openRoadmapModule('Learning')",
        "Microsoft Entra",
        "managed-user-chip",
        "Sustainable Finance Unit",
        "<ChevronDown",
        "Create users, assign forms, and manage access actions.",
        "function openDashboard()",
        "async function openReporting()",
        "activeView.value = 'reporting'",
        "Reporting workspaces",
    ):
        if required not in view:
            fail(f"SPA route model missing required Dashboard/Reporting contract: {required}")
    for forbidden in (
        'aria-label="TACATDP Monitoring Tool"',
        "Use your Microsoft account to continue to TACATDP Impact Evaluation.",
        "<span>TACATDP</span>",
        "Monitoring workspace",
        "Manage TACATDP project and form access through CRDB Microsoft identity",
        "CRDB Sustainable Finance",
        "MEL readiness",
        "Production readiness",
        "Mailbox readiness",
        "projection readiness",
        "CRDB update package",
        "Update gates",
        "crdb-update-readiness",
        "accessCrdbUpdateItems",
        "Future mutation payload",
        "Sign in with Microsoft",
        "managed-nav-item--planned",
        "managed-top-bar__context",
        "top-context-chip",
        "shell-back-action",
        "workspace-brief",
        "shellCanGoBack",
        "shellRefreshLabel",
        "refreshShellRoute",
        'aria-label="Data Collection"',
        "<span>Data Collection</span>",
    ):
        if forbidden in view:
            fail(f"Platform shell must stay generic; TACATDP belongs inside project context only: {forbidden}")
    reporting_function_match = re.search(r"async function openReportingDestination\(\).*?\n}", view, flags=re.S)
    if not reporting_function_match or "await openReporting();" not in reporting_function_match.group(0):
        fail("Global Reporting navigation must open the reporting route, not jump into a project Data tab")
    shell_slots = [
        'class="managed-app-shell"',
        'class="managed-side-nav"',
        'class="managed-app-content"',
        'class="managed-top-bar"',
        'class="managed-workspace-body"',
        'class="managed-app-footer"',
    ]
    slot_positions = []
    for slot in shell_slots:
        position = view.find(slot)
        if position < 0:
            fail(f"SPA managed shell missing required slot: {slot}")
        slot_positions.append(position)
    if slot_positions != sorted(slot_positions):
        fail("SPA managed shell slots must be ordered side nav, app content, top bar, workspace body, footer")
    workspace_position = view.find('class="managed-workspace-body"')
    footer_position = view.find('class="managed-app-footer"')
    workspace_close_position = view.find("</div>", workspace_position)
    if workspace_close_position < 0 or footer_position < workspace_close_position:
        fail("SPA managed shell footer must be outside managed-workspace-body")
    for required in (
        "getSignedInUserEmail",
        "$filter=mp_useremail eq",
        "listSavedSubmissions",
    ):
        if required not in client:
            fail(f"Power Pages assignment API must filter new-form assignments by the signed-in email: missing {required}")
    saved_method = re.search(r"async listSavedSubmissions\(\).*?\n  async getSubmissionFormContext", client, flags=re.S)
    if not saved_method:
        fail("Power Pages API client must keep an explicit listSavedSubmissions method")
    saved_body = saved_method.group(0)
    if "mp_useremail eq" in saved_body:
        fail("Saved submitted records must not be filtered to the signed-in user; authenticated users see all submitted records")
    workspace_match = re.search(r"async function loadWorkspace\(\).*?\n}", view, flags=re.S)
    if not workspace_match:
        fail("SPA must keep an explicit loadWorkspace startup function")
    workspace_body = workspace_match.group(0)
    if "listSavedSubmissions" in workspace_body:
        fail("Workspace startup must not load saved submissions; reporting/data records load on demand")
    if "measureAsync('view:loadWorkspace'" not in workspace_body:
        fail("Workspace startup must emit a bounded performance measurement")
    for required in (
        "workspaceHydrating",
        "workspaceHydrating.value = true",
        "workspaceHydrating.value = false",
        "Dashboard loading preview",
        "project-card--skeleton",
        "operational-metric-strip",
        "dashboardMetricItems",
        "Device connected",
        "Assignments refreshed",
        "Drafts on this device",
        "Assigned forms",
        "Data access",
        "dashboardDataAccessValue",
        "dashboardSubmittedScopeLabel",
        "Open Data to view submitted records",
        "Scope:",
        "attention-panel--clear",
        "Based on this device and the latest assignment refresh.",
    ):
        if required not in view:
            fail(f"Workspace startup must render the shell immediately with background hydration skeletons: missing {required}")
    for forbidden in ("Forms requiring action", "Loaded on demand", "No recent activity loaded", "id: 'submitted-records'"):
        if forbidden in view:
            fail(f"Dashboard state semantics must not expose ambiguous or implementation-oriented copy: {forbidden}")
    if '<section v-if="loading" class="loading-panel" aria-live="polite" aria-label="Loading projects"' in view:
        fail("Dashboard/projects startup must not use a blocking loading panel; render skeleton content instead")
    if "api:listAssignedForms" not in client or "api:listSavedSubmissions" not in client:
        fail("Power Pages API client must keep timing measurements for assignment and saved submission calls")
    for forbidden in (
        r'<template v-else-if="activeView === \'projects\'">\s*<section class="route-header"',
        r'<template v-else-if="activeView === \'records\'">\s*<nav class="top-action-bar"',
        r'v-show="activeView === \'runner\'".*?<nav class="top-action-bar"',
        r'<template v-else-if="activeView === \'access\'">\s*<nav class="top-action-bar"',
        r'<template v-else-if="activeView === \'system-activity\'">\s*<nav class="top-action-bar"',
        r'<h1[^>]*>User\s*&amp;\s*Access</h1>',
        r'<h1[^>]*>System Activity</h1>',
    ):
        if re.search(forbidden, view, flags=re.S):
            fail(f"Managed shell owns route identity; duplicate route chrome found: {forbidden}")
    for required in (
        "ReportingAccessScope",
        "getReportingAccessScope",
        "accessScope.mode === 'own-records'",
        "mp_useremail\" operator=\"eq",
        "this.isCurrentUserAccessAdmin()",
    ):
        if required not in client:
            fail(f"Reporting/export queries must enforce admin-all versus collector-own record scope: missing {required}")
    for required in (
        "reportingScopeLabel",
        "reportingScopeSummary",
        "exportScopeMessage",
        "canReadAllReportingRows ? 'All submitters' : 'Restricted to your email'",
        "export-scope-summary--guarded",
    ):
        if required not in view:
            fail(f"Reporting/export UI must disclose admin-all versus collector-own record scope: missing {required}")
    if "TACATDP_DEBUG_PERF" not in performance or "[TACATDP perf]" not in performance:
        fail("SPA performance helper must support opt-in production timing logs without secrets")
    for required in (
        "buildAssignedFormsFetchXml",
        "FormAssignmentMetadataRow",
        "toLinkedSummary",
        "Linked assignment metadata query failed; falling back to metadata hydration.",
        '<link-entity name="mp_formversion"',
        '<link-entity name="mp_form"',
    ):
        if required not in client:
            fail(f"Assignment startup must use one linked metadata query with guarded fallback: missing {required}")
    summary_match = re.search(r"private async toSummary\(assignment: FormAssignmentRow\).*?\n  private async listAllFormAssignments", client, flags=re.S)
    if not summary_match:
        fail("Power Pages API client must keep an explicit assignment summary mapper")
    summary_body = summary_match.group(0)
    if "resolveFormVersionXForm" in summary_body or "mp_xformxml" in summary_body or "getFormVersion(assignment._mp_formversion_value)" in summary_body:
        fail("Assignment startup summaries must not hydrate XForm XML; Collect/Edit loads XML on demand")
    if "hydrateAssignmentRuntime" not in client or "api:hydrateAssignmentRuntime" not in client:
        fail("Power Pages API client must expose timed runtime XForm hydration for Collect/Edit")
    for required in (
        "XFORM_CACHE_PREFIX",
        "buildXFormCacheKey",
        "api:getCachedXForm",
        "api:getXFormAttachment",
        "api:downloadXFormXml",
        "api:setCachedXForm",
        "setCachedXForm",
    ):
        if required not in client:
            fail(f"Collect runtime hydration must use bounded cached XForm loading with granular timings: missing {required}")
    for required in (
        "tacatdp-xform-cache",
        "maxEntries = 5",
        "indexedDB.open",
        "prune",
    ):
        if required not in xform_cache:
            fail(f"Collect runtime hydration must cache large XForm XML in a bounded IndexedDB store: missing {required}")
    if "formRuntimeMountReady && selectedAssignment.xformXml" not in view:
        fail("ODK runtime must mount only after the selected assignment has hydrated XForm XML")
    for required in (
        "warmedAssignments",
        "getWarmAssignment",
        "rememberWarmAssignment",
        "canReuseWarmRuntime",
    ):
        if required not in view:
            fail(f"Collect runtime must preserve hydrated form state across internal menu navigation: missing {required}")
    for required in (
        "persistent-runner-view",
        "v-show=\"activeView === 'runner'\"",
        ":aria-hidden=\"activeView !== 'runner'\"",
        ":inert=\"activeView !== 'runner' ? true : undefined\"",
    ):
        if required not in view:
            fail(f"Collect runner must stay mounted and be hidden accessibly across internal navigation: missing {required}")
    for required in (
        "Loading form definition...",
        "Loading form definition for edit...",
        "Preparing form runtime...",
    ):
        if required not in view:
            fail(f"Collect runner must show staged loading messages: missing {required}")
    for required in (
        "mp_lifecyclestatus eq",
        "mp_useremail",
        "getLatestSubmissionVersionByInstanceId",
        "mp_xformsubmissionxml",
        "parseSubmissionMetadata",
        "getSubmissionFormContext",
        "getLatestSubmissionXml",
        "updateSubmission",
        "normalizeInstanceId",
        "resolveInstanceName",
        "Customer_ID",
        "Customer_Name",
        "existingSubmission",
        "displayName",
    ):
        if required not in client:
            fail(f"Global saved-record/edit API path missing required guardrail: {required}")
    for required in (
        "ACCESS_ADMIN_POWERPAGES_ROLES",
        "isCurrentUserAccessAdmin",
        "getCurrentUserAccessAuthorization",
        "source: matchedRoles.length > 0 ? 'power-pages-web-role' : 'none'",
        "matchedRoles",
        "detectedRoles",
        "requiredRoles",
    ):
        if required not in client:
            fail(f"Power Pages access-admin authorisation guard missing required contract: {required}")
    for required in (
        "type AppView = 'dashboard' | 'projects' | 'records' | 'runner' | 'access' | 'reporting' | 'system-activity'",
        "User &amp; Access",
        "getCurrentUserAccessAuthorization",
        "accessAuthorizationSourceLabel",
        "routeIntentFromHash",
        "applyRouteIntent",
        "handleHashRouteChange",
        "A direct request for this administration route was blocked",
        "Access authorisation details",
        "System Activity",
        "activeView === 'system-activity'",
        "openSystemActivity",
        "setSystemActivitySection",
        "activeSystemActivitySection === 'health'",
        "activeSystemActivitySection === 'events'",
        "activeSystemActivitySection === 'onboarding'",
        "activeSystemActivitySection === 'submissions'",
        "activeSystemActivitySection === 'integrations'",
        "System Activity denied",
        "System Activity authorisation details",
        "systemHealthItems",
        "systemActivityEvents",
        "Platform logs remain external",
        "formRuntimeFallbackTimer",
        "startRuntimeMountFallback",
        "Form runtime mounted. Continue if the form is visible; refresh only if questions do not appear.",
        "Access route authorisation",
        "Required role",
        "Detected roles",
        "Matched admin role",
        "access-authorization-card",
        "access-authorization-list",
        "access-authorization-panel",
        "listAccessUsers",
        "Portal users",
        "openAccessWorkflow",
        "accessWorkflowOpen",
        "Create, invite and assign",
        "User details",
        "workflow-status-card--compact",
        "Project and form access",
        "Review and send",
        "Create access",
        "No records are created until the onboarding queue is enabled.",
        "access-workflow-panel",
        "access-stepper",
        "accessWorkflowFullName",
        "accessWorkflowCanProceed",
        "setAccessSection",
        "activeAccessSection === 'users'",
        "activeAccessSection === 'add'",
        "activeAccessSection === 'roles'",
        "activeAccessSection === 'activity'",
        "activeAccessSection === 'configuration'",
        "access-tabs",
        "access-tab-panel",
        "accessWriteActionStatus",
        "System status",
        "Production status",
        "userOnboardingReadiness",
        "Business reason",
        "accessWorkflowCanSubmit",
        "submitAccessWorkflow",
        "Access creation results",
        "accessWriteReadiness.statusLabel",
        "Permission model required",
        "access-readiness-panel",
        "access-readiness-row",
        "action-status-badge",
        "accessActivityEvents",
        "selectedAccessUserActivity",
        "Access activity",
        "Read-only audit preview",
        "access-activity-panel",
        "access-activity-row",
        "access-detail-drawer",
        "access-drawer-scrim",
        "Project and form access",
        "selectedAccessProjectName",
        "openAccessChangeAction",
        "selectedAccessAction",
        "Confirm access change",
        "Change role",
        "Correct email",
        "Remove access",
        "Reactivate access",
        "Complete access change details before applying",
        "Audit-first change",
        "submitManageAccessUser",
        "accessChangeCanApply",
        "access-confirm-panel",
        "Collect",
        "Summary",
        "Data",
        "Exports",
        "Power BI",
        "Edit",
        "recordSearch",
        "Search submitted data",
        "openSavedSubmission",
        ":edit-instance",
        "@lucide/vue",
        "ArrowLeft",
        "NotepadText",
        "Pencil",
        "Search",
        "RefreshCw",
        "material-tabs",
        "material-tab--active",
        "project-command-card",
        "summary-grid",
        "Submitted records",
        "submitting",
        "postSubmitMessage",
        "postSubmitTone",
        "Submitting record",
        "Saving to Dataverse",
        "/CRDB_Bank_PLC.svg",
        "visiblePageNumbers",
        "activePageStart",
        "activePageEnd",
        "setActivePage",
        "clampActivePage",
        'class="pagination-bar"',
        "Showing {{ activePageStart }}-{{ activePageEnd }} of {{ activeRecordCount }}",
        "Page {{ activeRecordPage }} of {{ activeTotalPages }}",
        "pagination-button--active",
        "activeView.value = selectedProject.value ? 'records' : 'projects'",
        "activeFormSection.value = 'data'",
        "existingSubmission: selectedEditSubmission.value",
        "reportRow.mp_displayname || reportRow.mp_instanceid",
        "listSubmissionReportRows",
        "listSubmissionAnswers",
        "createCsvExportSetting",
        "reportDateFrom",
        "reportDateTo",
        "reportSubmitter",
        "reportReviewState",
        "Reporting records",
        "openReportDetail",
        "Save and download CSV",
        "listAllSubmissionReportRows",
        "downloadReportCsv",
        "buildExportName",
        "refreshExportName",
        "replace(/\\s+/g, '_')",
        "anchor.download = `${name}.csv`",
        "spreadsheetSafe",
        "powerBiEnvironmentUrl",
        "Microsoft Dataverse",
        "mp_submissionreportrow",
        "mp_submissionrepeatrow",
        "mp_submissionanswer",
        "report-filter-bar",
        "VueDatePicker",
        "date-range-picker",
        "reportDateRange",
        "icon-action--compact",
        "action-tooltip",
        'aria-label="View record"',
        'aria-label="Edit record"',
        'aria-label="Clear all filters"',
        "record-detail-panel",
        "Owner: {{ selectedReportRow.mp_useremail || 'Unknown owner' }}",
        "export-workspace",
        "powerbi-workspace",
    ):
        if required not in view:
            fail(f"Monitoring Tool CRUD workspace shell missing required text or state: {required}")
    reporting_table = re.search(
        r'aria-label="Reporting data table".*?</table>',
        view,
        flags=re.S,
    )
    if not reporting_table:
        fail("Monitoring Tool Data tab must retain its reporting table")
    if '<th scope="col">Owner</th>' in reporting_table.group(0):
        fail("Monitoring Tool Data table must show Owner in record detail, not as a list column")
    for required in (
        "buildReportingFetchXml",
        "fetchXml=",
        'count="${pageSize}" page="${page}"',
        'returntotalrecordcount="true"',
    ):
        if required not in client:
            fail(f"Power Pages reporting API missing required paging/export guardrail: {required}")
    reporting_read = re.search(
        r"async listSubmissionReportRows\(.*?\n  async listAllSubmissionReportRows",
        client,
        flags=re.S,
    )
    if not reporting_read:
        fail("Power Pages reporting API must keep a bounded listSubmissionReportRows method")
    elif "&$count=true" in reporting_read.group(0):
        fail(
            "Power Pages FetchXML reporting must not combine "
            "returntotalrecordcount with the equivalent OData $count option"
        )
    if "'$skip'" in client or "\"$skip\"" in client:
        fail("Power Pages reporting pagination must not use unsupported Dataverse $skip")
    handle_loaded = re.search(r"function handleFormLoaded\(\)\s*\{(?P<body>.*?)\nasync function handleSubmit", view, flags=re.S)
    if not handle_loaded:
        fail("Monitoring Tool runner must keep an explicit handleFormLoaded function")
    if "draftStore.save" in handle_loaded.group("body"):
        fail("handleFormLoaded must not create local drafts; drafts require restorable ODK instance state")
    if "Local runtime marker saved" in view or "Open a form once to create a local draft marker" in view:
        fail("Monitoring Tool must not present runtime-load markers as local drafts")
    for glyph in ('aria-hidden="true">></span>', 'aria-hidden="true"><</span>', 'aria-hidden="true">R</span>', 'aria-hidden="true">S</span>', 'aria-hidden="true">D</span>', 'aria-hidden="true">+</span>'):
        if glyph in view:
            fail(f"Monitoring Tool actions must use icon components, not text glyphs: {glyph}")
    if "RuntimeLoaded" not in drafts or "isRestorableDraft" not in drafts:
        fail("Draft store must filter non-restorable runtime-load markers")


def main() -> int:
    if not SPA.exists():
        fail(f"missing {SPA.relative_to(ROOT)}")
    if not SEED_SCRIPT.exists():
        fail(f"missing {SEED_SCRIPT.relative_to(ROOT)}")

    for relative in REQUIRED_FILES:
        path = SPA / relative
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    package = json.loads((SPA / "package.json").read_text())
    if package.get("private") is not True:
        fail("webforms-spa package must be private")
    for script in ("dev", "build", "typecheck"):
        if script not in package.get("scripts", {}):
            fail(f"package.json missing script {script}")
    dependencies = package.get("dependencies", {})
    for dependency in ("@getodk/web-forms", "@getodk/xforms-engine", "@lucide/vue"):
        if dependency not in dependencies:
            fail(f"package.json missing reviewed ODK dependency {dependency}")

    all_text = "\n".join((SPA / relative).read_text() for relative in TEXT_SCAN_FILES)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, all_text, flags=re.IGNORECASE):
            fail(f"forbidden browser credential/raw Dataverse pattern found: {pattern}")
    for expected in REQUIRED_API_STRINGS:
        if expected not in all_text:
            fail(f"missing required SPA API guardrail string: {expected}")
    if "indexedDB.open" not in all_text:
        fail("draft adapter must use explicit browser-local storage")
    for expected in (
        "OdkWebForm",
        "webFormsPlugin",
        "@getodk/web-forms",
        "@loaded",
        "@submit",
        "Preparing form runtime",
        "Submitting to Dataverse",
        "POST_SUBMIT__NEW_INSTANCE",
        "xml_submission_file",
        "preventPowerPagesFormSubmit",
        "preventRuntimeButtonDefault",
        "document.addEventListener('submit'",
        "document.addEventListener('click'",
        "formRuntimeLoading",
        "formRuntimeMountReady",
        "prepareRuntimeMount",
        "Loading form",
        "Preparing the form runtime",
        "aria-label=\"Loading form\"",
        "loading-panel--runtime",
        "attachmentBinaryUploadCount",
        "attachmentWarnings",
        "relabelOdkSubmitButton",
        "MutationObserver",
        "aria-label', 'Submit'",
        "focusFirstRuntimeError",
        "focusFirstRuntimeErrorAfterRender",
        "ODK validation is not ready",
        "Please fix the highlighted form fields before submitting",
        "aria-invalid=\"true\"",
        ".p-invalid",
        ":focus-visible",
        ".odk-runtime-host .powered-by-wrapper",
        ".odk-runtime-host .footer",
        ".odk-runtime-host .form-wrapper",
        ".submit-overlay",
        ".submit-progress-panel",
        ".loading-dots",
    ):
        if expected not in all_text:
            fail(f"missing required ODK runtime proof string: {expected}")
    for forbidden in ("Technical diagnostics", "debug-panel", "Previous renderer marker"):
        if forbidden in all_text:
            fail(f"diagnostics UI must not be visible in the Monitoring Tool runtime: {forbidden}")
    validate_seed_xform_body_refs()
    validate_odk_style_isolation()
    validate_powerpages_hosting()
    validate_powerpages_session_contract()

    print("WebForms SPA runtime foundation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
