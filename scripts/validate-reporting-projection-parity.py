#!/usr/bin/env python3
"""Compare normalized Python and C# reporting projection output."""

from __future__ import annotations

import importlib.util
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/reporting-projection/root-nested-repeat.json"
CSHARP_DLL = ROOT / "tests/Tacatdp.ReportingProjection.Plugin.Tests/bin/Release/net10.0/Tacatdp.ReportingProjection.Plugin.Tests.dll"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_builder() -> Any:
    path = ROOT / "scripts/build-reporting-projections.py"
    spec = importlib.util.spec_from_file_location("build_reporting_projections_parity", path)
    if spec is None or spec.loader is None:
        fail("could not load Python projection builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def repeat_key(row: dict[str, Any]) -> str | None:
    binding = row.get("mp_SubmissionRepeatRow@odata.bind")
    if not binding:
        return None
    match = re.search(r"mp_repeatrowkey='(.*)'", binding)
    return match.group(1).replace("''", "'") if match else None


def main() -> int:
    if not CSHARP_DLL.is_file():
        fail(f"build the C# validator first: {CSHARP_DLL.relative_to(ROOT)}")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    builder = load_builder()
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
    python_output = {
        "report": {
            "key": projection.report_row["mp_reportkey"],
            "status": projection.report_row["mp_projectionstatus"],
            "rootAnswersJson": projection.report_row["mp_rootanswersjson"],
        },
        "repeats": sorted(
            [
                {
                    "key": row["mp_repeatrowkey"],
                    "path": row["mp_repeatpath"],
                    "parentPath": row["mp_parentpath"],
                    "parentKey": row["mp_parentrepeatrowkey"],
                    "index": row["mp_rowindex"],
                    "answersJson": row["mp_answersjson"],
                }
                for row in projection.repeat_rows
            ],
            key=lambda row: row["key"],
        ),
        "answers": sorted(
            [
                {
                    "key": row["mp_answerkey"],
                    "repeatKey": repeat_key(row),
                    "path": row["mp_fieldpath"],
                    "valueText": row["mp_valuetext"],
                    "valueDecimal": row.get("mp_valuedecimal"),
                    "valueDate": row.get("mp_valuedate"),
                    "valueBoolean": row.get("mp_valueboolean"),
                    "valueJson": row.get("mp_valuejson"),
                }
                for row in projection.answer_rows
            ],
            key=lambda row: row["key"],
        ),
    }
    completed = subprocess.run(
        ["dotnet", str(CSHARP_DLL), str(FIXTURE), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    csharp_output = json.loads(completed.stdout)
    if python_output != csharp_output:
        python_json = json.dumps(python_output, indent=2, sort_keys=True).splitlines()
        csharp_json = json.dumps(csharp_output, indent=2, sort_keys=True).splitlines()
        difference = "\n".join(difflib.unified_diff(python_json, csharp_json, fromfile="python", tofile="csharp"))
        fail(f"normalized Python and C# projection outputs differ\n{difference}")
    print("Reporting projection Python/C# parity validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
