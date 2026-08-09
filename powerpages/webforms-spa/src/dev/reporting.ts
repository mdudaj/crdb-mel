import type { ExportSettingRow, SubmissionAnswerRow, SubmissionReportRow } from '../powerpages-api/types';

export const devReportingRows: SubmissionReportRow[] = [
  {
    mp_submissionreportrowid: 'local-report-1',
    mp_reportkey: 'local-form:uuid:crdb-001',
    mp_instanceid: 'uuid:crdb-001',
    mp_displayname: 'C001:Upendo Group',
    mp_useremail: 'operations.user@example.test',
    mp_submittedat: '2026-07-14T08:15:00Z',
    mp_updatedat: '2026-07-14T09:30:00Z',
    mp_versionnumber: 2,
    mp_lifecyclestatus: 100000001,
    mp_reviewstate: 100000000,
    mp_projectionstatus: 100000000,
    mp_projectedat: '2026-07-14T09:31:00Z',
    mp_rootanswersjson: '{"customer_id":"C001","customer_name":"Upendo Group","district":"Moshi"}',
    _mp_formversion_value: 'local-form-version',
  },
  {
    mp_submissionreportrowid: 'local-report-2',
    mp_reportkey: 'local-form:uuid:crdb-002',
    mp_instanceid: 'uuid:crdb-002',
    mp_displayname: 'C002:Amani Enterprise',
    mp_useremail: 'review.user@example.test',
    mp_submittedat: '2026-07-13T12:10:00Z',
    mp_updatedat: '2026-07-13T12:10:00Z',
    mp_versionnumber: 1,
    mp_lifecyclestatus: 100000001,
    mp_reviewstate: 100000004,
    mp_projectionstatus: 100000000,
    mp_projectedat: '2026-07-14T09:31:00Z',
    mp_rootanswersjson: '{"customer_id":"C002","customer_name":"Amani Enterprise","district":"Arusha"}',
    _mp_formversion_value: 'local-form-version',
  },
];

export const devSubmissionAnswers: SubmissionAnswerRow[] = [
  {
    mp_submissionanswerid: 'local-answer-1',
    mp_answerkey: 'local-answer-1',
    mp_instanceid: 'uuid:crdb-001',
    mp_fieldpath: '/data/customer_id',
    mp_fieldname: 'customer_id',
    mp_fieldlabel: 'Customer ID',
    mp_valuetext: 'C001',
    _mp_submissionreportrow_value: 'local-report-1',
  },
  {
    mp_submissionanswerid: 'local-answer-2',
    mp_answerkey: 'local-answer-2',
    mp_instanceid: 'uuid:crdb-001',
    mp_fieldpath: '/data/customer_name',
    mp_fieldname: 'customer_name',
    mp_fieldlabel: 'Customer name',
    mp_valuetext: 'Upendo Group',
    _mp_submissionreportrow_value: 'local-report-1',
  },
];

export const devExportSettings: ExportSettingRow[] = [];
