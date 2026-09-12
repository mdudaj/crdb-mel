# TACATDP Integrated M&E System submission pack

Date: 2026-08-27

## Purpose

This folder contains the end-of-week documentation pack for the TACATDP Integrated M&E System and Monitoring Tool.

The pack is written for mixed technical and non-technical review. It records the current prototype state, the working baseline import path, the dashboard/reporting status, user procedures, draft SOPs, and the annexes used during development.

## Documents

| File | Deliverable supported |
|---|---|
| `01-system-stages-report.md` | Report with all system stages and current configuration details |
| `02-dashboard-interface-screenshot-note.md` | Dashboard interface screenshot deliverable and capture checklist |
| `03-user-manual.md` | User manual for administrators, MEL users, and data-entry users |
| `04-sop-draft.md` | Draft SOPs by role and responsibility |
| `05-annex-index.md` | Annex list of source documents, datasets, forms, environment notes, and technical references |
| `TACATDP-Integrated-ME-System-Submission-Pack.pdf` | Shareable PDF generated from the Markdown pack and screenshot annexes |
| `TACATDP-Integrated-ME-System-Submission-Pack.docx` | Editable Word version generated from the same Markdown pack and embedded screenshot annexes |

## Current prototype state

- The prototype runs on Microsoft Power Pages and Dataverse.
- The cleaned TACATDP baseline data has been successfully imported through the prototype import workflow.
- The CRDB development environment has been updated with the latest tested Power Pages build.
- The latest form version is `2608130924`.
- CRDB users can update the latest form version and import cleaned baseline data through the administrator-only `Baseline Import` route, subject to CRDB table permissions.
- CRDB ICT has proposed a changed deployment strategy using CRDB-hosted infrastructure. This requires architecture and implementation rework for the next system version.

## Packaging instruction

Generate the shareable PDF and Word document with:

```bash
/home/jmduda/KodeX/karakana/.venv/bin/python scripts/render-submission-pack.py docs/submission-pack-20260827
```

Do not attach raw beneficiary data unless CRDB authorizes the recipient and sharing channel.
