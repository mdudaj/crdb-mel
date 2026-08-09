#!/usr/bin/env python3
"""Validate the TACATDP onboarding queue architecture artifacts."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "powerpages-odk-webforms"

REQUIRED = {
    "access-onboarding-queue-requirements-20260724.md": [
        "Dataverse-backed onboarding request queue",
        "/_api/cloudflow/v1.0/trigger",
        "Pending",
        "Processing",
        "Completed",
        "Failed",
        "https://learn.microsoft.com/en-us/power-pages/configure/cloud-flow-integration",
    ],
    "adr-0008-onboarding-request-queue.md": [
        "TACATDP will replace direct portal cloud-flow invocation",
        "OnboardingRequest",
        "Dataverse-triggered cloud flow",
        "The portal must not call",
        "Rejected Alternatives",
    ],
    "access-onboarding-queue-data-contract-20260724.md": [
        "mp_onboardingrequest",
        "mp_requestkey",
        "mp_status",
        "mp_formscopejson",
        "Power Pages administrator web role",
    ],
    "access-onboarding-queue-delivery-plan-20260724.md": [
        "Slice 2: Dataverse Schema Package",
        "Slice 3: Portal Queue Submission",
        "Slice 4: Dataverse-Triggered Automation",
        "CRDB Update Package",
    ],
    "access-onboarding-queue-runbook-20260724.md": [
        "Do not call",
        "Administrator Workflow",
        "Expected System Workflow",
        "CRDB Deployment Checklist",
    ],
    "access-onboarding-queue-traceability-20260724.md": [
        "User Story",
        "Requirement Mapping",
        "Acceptance Criteria Mapping",
        "Definition of Done",
        "Verification Summary",
    ],
}


def main() -> int:
    missing: list[str] = []

    for filename, needles in REQUIRED.items():
        path = DOCS / filename
        if not path.exists():
            missing.append(f"{filename}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{filename}: missing {needle!r}")

    if missing:
        for item in missing:
            print(item)
        return 1

    print("Access onboarding queue artifacts validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
