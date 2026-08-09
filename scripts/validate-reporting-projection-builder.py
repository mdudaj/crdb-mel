#!/usr/bin/env python3
"""Validate reporting projection builder behavior without network access."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/build-reporting-projections.py"
FIXTURE = ROOT / "tests/fixtures/reporting-projection/root-nested-repeat.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_builder():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("build_reporting_projections", BUILDER)
    if spec is None or spec.loader is None:
        fail(f"could not load {BUILDER.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_reporting_projections"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    builder = load_builder()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    submission = {
        "mp_submissionid": fixture["submissionId"],
        "mp_instanceid": fixture["instanceId"],
        "mp_useremail": fixture["userEmail"],
        "mp_submittedat": fixture["submittedAt"],
        "mp_updatedat": fixture["updatedAt"],
        "mp_lifecyclestatus": fixture["lifecycleStatus"],
        "mp_reviewstate": fixture["reviewState"],
    }
    version = {
        "mp_submissionversionid": fixture["submissionVersionId"],
        "mp_versionnumber": fixture["versionNumber"],
        "mp_instanceid": fixture["instanceId"],
        "mp_submissionjson": json.dumps(
            {
                "formVersionId": fixture["formVersionId"],
                "xmlFormId": fixture["xmlFormId"],
                "instanceName": fixture["instanceName"],
                "repeatPaths": fixture["repeatPaths"],
            }
        ),
        "mp_xformsubmissionxml": fixture["submissionXml"],
    }
    projection = builder.build_projection(submission, version, fixture["projectedAt"])
    expected = fixture["expected"]

    if projection.report_row["mp_displayname"] != fixture["instanceName"]:
        fail("report row display name did not come from metadata")
    if projection.report_row["mp_reportkey"] != expected["reportKey"]:
        fail("report key did not match the shared fixture")
    if "customer_name" not in projection.report_row["mp_rootanswersjson"]:
        fail("root answers json missing customer_name")
    if len(projection.repeat_rows) != expected["repeatCount"]:
        fail(f"expected {expected['repeatCount']} repeat rows, got {len(projection.repeat_rows)}")
    if len(projection.answer_rows) != expected["answerCount"]:
        fail(f"expected {expected['answerCount']} answer rows, got {len(projection.answer_rows)}")
    member_repeats = [row for row in projection.repeat_rows if row["mp_repeatpath"] == "/data/household/member"]
    if len(member_repeats) != expected["memberRepeatCount"]:
        fail("known repeat paths did not preserve singleton nested repeats")
    if not any(row["mp_fieldpath"].endswith("/member/name") and row.get("mp_SubmissionRepeatRow@odata.bind") for row in projection.answer_rows):
        fail("repeat answer rows must bind to repeat-row alternate key")
    if not any(row["mp_fieldpath"].endswith("/customer_name") and "mp_SubmissionRepeatRow@odata.bind" not in row for row in projection.answer_rows):
        fail("root answer rows must not bind to a repeat row")
    if not any(row["mp_fieldpath"] == "/data/active" and row.get("mp_valueboolean") is True for row in projection.answer_rows):
        fail("boolean coercion did not match the shared fixture")

    print("Reporting projection builder validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
