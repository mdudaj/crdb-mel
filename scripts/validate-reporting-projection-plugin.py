#!/usr/bin/env python3
"""Validate the reporting projection plug-in source and registration contract."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "dataverse/Tacatdp.ReportingProjection.Plugin"
PROJECT = PLUGIN / "Tacatdp.ReportingProjection.Plugin.csproj"
REGISTRATION = PLUGIN / "registration-contract.json"
REQUIRED_FILES = [
    "PluginBase.cs",
    "ProjectionModels.cs",
    "ProjectionCore.cs",
    "SubmissionMetadataParser.cs",
    "DataverseProjectionRepository.cs",
    "ProjectionRefreshPlugin.cs",
    "packages.lock.json",
    "registration-contract.json",
]
FORBIDDEN_SOURCE = [
    "Task.Run",
    "Parallel.For",
    "Parallel.ForEach",
    "ExecuteMultipleRequest",
    "ExecuteTransactionRequest",
    "client_secret",
    "Authorization:",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> int:
    for relative in REQUIRED_FILES:
        if not (PLUGIN / relative).is_file():
            fail(f"missing plug-in artifact: {relative}")

    project = PROJECT.read_text(encoding="utf-8")
    for required in (
        "<TargetFramework>net462</TargetFramework>",
        'Version="9.0.2.60"',
        'Version="1.52.1"',
        'Version="1.0.3"',
        "<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>",
    ):
        if required not in project:
            fail(f"plug-in project missing pinned contract: {required}")
    if re.search(r'Version="[^"]*\*', project):
        fail("plug-in dependencies must not use wildcard versions")

    source = "\n".join((PLUGIN / relative).read_text(encoding="utf-8") for relative in REQUIRED_FILES if relative.endswith(".cs"))
    for forbidden in FORBIDDEN_SOURCE:
        if forbidden in source:
            fail(f"plug-in source contains forbidden pattern: {forbidden}")
    for required in (
        "ProjectionCore.ShouldProcess",
        "GetLatestVersionIdentity",
        "MaximumConvergencePasses = 3",
        "OperationStatus.Retry",
        "PluginUserService",
        "ProjectionStatuses.Stale",
        "ProjectionStatuses.Ready",
        "ProjectionStatuses.Failed",
        "SubmissionVersionImage",
    ):
        if required not in source:
            fail(f"plug-in source missing behavior marker: {required}")

    repository = (PLUGIN / "DataverseProjectionRepository.cs").read_text(encoding="utf-8")
    answer_delete = repository.find("DeleteObsoleteChildren(AnswerTable")
    repeat_delete = repository.find("DeleteObsoleteChildren(RepeatTable")
    ready_update = repository.find("SetReportAttributes(ready, projection.Report, ProjectionStatuses.Ready)")
    if min(answer_delete, repeat_delete, ready_update) < 0 or not answer_delete < repeat_delete < ready_update:
        fail("repository must delete obsolete answers, then repeats, then mark the root Ready")

    plugin = (PLUGIN / "ProjectionRefreshPlugin.cs").read_text(encoding="utf-8")
    trace_calls = re.findall(r"localPluginContext\.Trace\((.*?);", plugin, flags=re.S)
    if any("SubmissionXml" in trace or "ValueText" in trace for trace in trace_calls):
        fail("plug-in traces must not contain canonical XML or answer values")

    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    step = registration.get("step", {})
    image = registration.get("postImage", {})
    if registration.get("solutionUniqueName") != "tacatdp_prototype":
        fail("registration contract must target tacatdp_prototype")
    if registration.get("environmentWrite") is not False:
        fail("source registration contract must remain non-executing")
    expected_step = {
        "message": "Create",
        "primaryEntity": "mp_submissionversion",
        "stage": "PostOperation",
        "mode": "Asynchronous",
    }
    for key, expected in expected_step.items():
        if step.get(key) != expected:
            fail(f"registration step {key} must be {expected}")
    if step.get("runInUserContext") != "DEDICATED_LEAST_PRIVILEGE_USER_REQUIRED":
        fail("registration contract must not bind a source-environment user id")
    if image.get("alias") != "SubmissionVersionImage" or image.get("columns") != ["mp_instanceid"]:
        fail("registration post image is incomplete")

    client = (ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts").read_text(encoding="utf-8")
    for required in ("repeatPaths", "getElementsByTagNameNS('*', 'repeat')"):
        if required not in client:
            fail(f"submission metadata is missing repeat contract marker: {required}")

    print("Reporting projection plug-in source validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
