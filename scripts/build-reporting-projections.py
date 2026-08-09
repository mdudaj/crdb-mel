#!/usr/bin/env python3
"""Build TACATDP reporting projection rows from canonical submission versions.

Dry-run is the default. Use --execute only after the additive reporting tables
exist in the target Dataverse environment.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SUBMITTED_STATUS = 100000001
PROJECTION_READY = 100000000
PROJECTION_STALE = 100000001
PROJECTION_FAILED = 100000002
REVIEW_RECEIVED = 100000000
LIFECYCLE_SUBMITTED = 100000001


@dataclass(frozen=True)
class ProjectionRows:
    report_row: dict[str, Any]
    repeat_rows: list[dict[str, Any]]
    answer_rows: list[dict[str, Any]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env", help="Environment file with Dataverse app settings.")
    parser.add_argument("--top", type=int, default=500, help="Maximum submitted records to inspect.")
    parser.add_argument("--instance-id", help="Limit rebuild to one ODK instance id.")
    parser.add_argument("--include-all-statuses", action="store_true", help="Include non-submitted canonical submissions.")
    parser.add_argument("--execute", action="store_true", help="Write/upsert reporting projection rows.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable summary.")
    return parser.parse_args()


def load_deploy_module() -> Any:
    module_path = ROOT / "scripts/dataverse-schema-deploy.py"
    spec = importlib.util.spec_from_file_location("dataverse_schema_deploy", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dataverse_schema_deploy"] = module
    spec.loader.exec_module(module)
    return module


def escape_odata_string(value: str) -> str:
    return value.replace("'", "''")


def parse_metadata(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"metadata_parse_error": True}
    return parsed if isinstance(parsed, dict) else {}


def strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sanitize_key_part(value: Any) -> str:
    text = str("" if value is None else value).strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^0-9A-Za-z_.:-]+", "_", text)
    return text.strip("_") or "blank"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_leaf(node: ElementTree.Element) -> bool:
    return not list(node)


def node_text(node: ElementTree.Element) -> str:
    return (node.text or "").strip()


def sibling_name_counts(parent: ElementTree.Element) -> dict[str, int]:
    counts: dict[str, int] = {}
    for child in list(parent):
        name = strip_namespace(child.tag)
        counts[name] = counts.get(name, 0) + 1
    return counts


def coerce_value(text: str) -> dict[str, Any]:
    value: dict[str, Any] = {"mp_valuetext": text}
    lower = text.lower()
    if lower in {"true", "false"}:
        value["mp_valueboolean"] = lower == "true"
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        try:
            value["mp_valuedecimal"] = float(text)
        except ValueError:
            pass
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}(t.*)?", lower):
        value["mp_valuedate"] = text
    if text.startswith("{") or text.startswith("["):
        value["mp_valuejson"] = text
    return value


def leaf_answers(node: ElementTree.Element, path: list[str]) -> dict[str, str]:
    answers: dict[str, str] = {}

    def visit(current: ElementTree.Element, current_path: list[str]) -> None:
        if is_leaf(current):
            text = node_text(current)
            if text:
                answers["/".join(current_path)] = text
            return
        for child in list(current):
            visit(child, [*current_path, strip_namespace(child.tag)])

    visit(node, path)
    return answers


def build_projection(
    submission: dict[str, Any],
    version: dict[str, Any],
    projected_at: str,
    *,
    form_version_exists: bool = True,
) -> ProjectionRows:
    metadata = parse_metadata(version.get("mp_submissionjson"))
    instance_id = submission.get("mp_instanceid") or version.get("mp_instanceid") or metadata.get("instanceId") or ""
    form_version_id = metadata.get("formVersionId") or version.get("_mp_formversion_value")
    xml_form_id = metadata.get("xmlFormId") or "unknown_form"
    report_key = f"{sanitize_key_part(form_version_id or xml_form_id)}:{sanitize_key_part(instance_id)}"
    report_row = {
        "mp_reportkey": report_key,
        "mp_instanceid": instance_id,
        "mp_displayname": metadata.get("instanceName") or instance_id,
        "mp_useremail": submission.get("mp_useremail"),
        "mp_submittedat": submission.get("mp_submittedat"),
        "mp_updatedat": submission.get("mp_updatedat"),
        "mp_versionnumber": version.get("mp_versionnumber") or 1,
        "mp_lifecyclestatus": submission.get("mp_lifecyclestatus") or LIFECYCLE_SUBMITTED,
        "mp_reviewstate": submission.get("mp_reviewstate") or REVIEW_RECEIVED,
        "mp_projectionstatus": PROJECTION_READY,
        "mp_projectedat": projected_at,
        "mp_rootanswersjson": "{}",
        "mp_Submission@odata.bind": f"/mp_submissions({submission['mp_submissionid']})",
        "mp_SubmissionVersion@odata.bind": f"/mp_submissionversions({version['mp_submissionversionid']})",
    }
    if form_version_id and form_version_exists:
        report_row["mp_FormVersion@odata.bind"] = f"/mp_formversions({form_version_id})"

    xml = version.get("mp_xformsubmissionxml") or ""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        failed = dict(report_row)
        failed["mp_projectionstatus"] = PROJECTION_FAILED
        failed["mp_projectionerror"] = str(exc)
        return ProjectionRows(failed, [], [])

    repeat_rows: list[dict[str, Any]] = []
    answer_rows: list[dict[str, Any]] = []
    root_answers: dict[str, str] = {}
    repeat_answers: dict[str, dict[str, str]] = {}
    known_repeat_paths = {
        str(path).strip()
        for path in metadata.get("repeatPaths", [])
        if isinstance(path, str) and str(path).strip().startswith("/")
    }

    def add_answer(field_path: str, text: str, repeat_row_key: str | None = None) -> None:
        key_parts = [report_key, repeat_row_key or "root", field_path]
        answer_key = ":".join(sanitize_key_part(part) for part in key_parts)
        row = {
            "mp_answerkey": answer_key,
            "mp_instanceid": instance_id,
            "mp_fieldpath": field_path,
            "mp_fieldname": field_path.rsplit("/", 1)[-1],
            "mp_projectedat": projected_at,
            "mp_SubmissionReportRow@odata.bind": f"/mp_submissionreportrows(mp_reportkey='{escape_odata_string(report_key)}')",
            "mp_SubmissionVersion@odata.bind": f"/mp_submissionversions({version['mp_submissionversionid']})",
            **coerce_value(text),
        }
        if repeat_row_key:
            repeat_answers[repeat_row_key][field_path.lstrip("/")] = text
            row["mp_SubmissionRepeatRow@odata.bind"] = (
                f"/mp_submissionrepeatrows(mp_repeatrowkey='{escape_odata_string(repeat_row_key)}')"
            )
        answer_rows.append(row)

    def visit(parent: ElementTree.Element, path: list[str], parent_repeat_key: str | None = None) -> None:
        counts = sibling_name_counts(parent)
        seen: dict[str, int] = {}
        for child in list(parent):
            name = strip_namespace(child.tag)
            child_path = [*path, name]
            text = node_text(child)
            if is_leaf(child):
                if text:
                    field_path = "/" + "/".join(child_path)
                    if parent_repeat_key:
                        add_answer(field_path, text, parent_repeat_key)
                    else:
                        root_answers[field_path] = text
                        add_answer(field_path, text)
                continue

            seen[name] = seen.get(name, 0) + 1
            repeat_path = "/" + "/".join(child_path)
            is_repeat = counts[name] > 1 or repeat_path in known_repeat_paths
            if is_repeat:
                row_index = seen[name] - 1
                repeat_key = ":".join(
                    sanitize_key_part(part)
                    for part in [report_key, repeat_path, parent_repeat_key or "root", row_index]
                )
                repeat_answers[repeat_key] = {}
                repeat_row = {
                        "mp_repeatrowkey": repeat_key,
                        "mp_instanceid": instance_id,
                        "mp_repeatpath": repeat_path,
                        "mp_parentpath": "/" + "/".join(path) if path else "/",
                        "mp_parentrepeatrowkey": parent_repeat_key,
                        "mp_rowindex": row_index,
                        "mp_answersjson": "{}",
                        "mp_projectedat": projected_at,
                        "mp_SubmissionReportRow@odata.bind": (
                            f"/mp_submissionreportrows(mp_reportkey='{escape_odata_string(report_key)}')"
                        ),
                        "mp_SubmissionVersion@odata.bind": f"/mp_submissionversions({version['mp_submissionversionid']})",
                    }
                repeat_rows.append(repeat_row)
                visit(child, child_path, repeat_key)
                repeat_row["mp_answersjson"] = json.dumps(
                    repeat_answers[repeat_key], sort_keys=True, ensure_ascii=True
                )
            else:
                visit(child, child_path, parent_repeat_key)

    visit(root, [strip_namespace(root.tag)])
    report_row["mp_rootanswersjson"] = json.dumps(root_answers, sort_keys=True, ensure_ascii=True)
    return ProjectionRows(report_row, repeat_rows, answer_rows)


class ProjectionClient:
    def __init__(self, deploy: Any, settings: Any, token: str) -> None:
        self.deploy = deploy
        self.dv = deploy.Dataverse(settings, token)

    def collect(self, path: str, limit: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        data = self.dv.get_json(path) or {}
        while True:
            rows.extend(data.get("value") or [])
            if len(rows) >= limit:
                return rows[:limit]
            next_link = data.get("@odata.nextLink")
            if not next_link:
                return rows
            data = self.dv.get_json(next_link) or {}

    def submissions(self, top: int, submitted_only: bool, instance_id: str | None) -> list[dict[str, Any]]:
        select = ",".join(
            [
                "mp_submissionid",
                "mp_instanceid",
                "mp_useremail",
                "mp_submittedat",
                "mp_updatedat",
                "mp_lifecyclestatus",
                "mp_reviewstate",
            ]
        )
        filters: list[str] = []
        if submitted_only:
            filters.append(f"mp_lifecyclestatus eq {SUBMITTED_STATUS}")
        if instance_id:
            filters.append(f"mp_instanceid eq '{escape_odata_string(instance_id)}'")
        path = f"mp_submissions?$select={select}&$orderby=mp_updatedat desc&$top={min(top, 5000)}"
        if filters:
            path += "&$filter=" + " and ".join(filters)
        return self.collect(path, top)

    def latest_version(self, instance_id: str) -> dict[str, Any] | None:
        select = ",".join(
            [
                "mp_submissionversionid",
                "mp_versionnumber",
                "mp_instanceid",
                "mp_xformsubmissionxml",
                "mp_submissionjson",
            ]
        )
        data = self.dv.get_json(
            "mp_submissionversions?"
            f"$select={select}&$filter=mp_instanceid eq '{escape_odata_string(instance_id)}'"
            "&$orderby=mp_versionnumber desc&$top=1"
        ) or {}
        rows = data.get("value") or []
        return rows[0] if rows else None

    def table_exists(self, logical_name: str) -> bool:
        return self.deploy.entity_exists(self.dv, logical_name)

    def row_exists(self, entity_set: str, row_id: str) -> bool:
        response = self.dv.request("GET", f"{entity_set}({row_id})?$select={entity_set[:-1]}id")
        if response.status_code == 404:
            return False
        if response.status_code >= 400:
            raise RuntimeError(f"GET {entity_set}({row_id}) failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")
        return True

    def upsert(self, entity_set: str, key_column: str, key_value: str, payload: dict[str, Any]) -> None:
        path = f"{entity_set}({key_column}='{escape_odata_string(key_value)}')"
        response = self.dv.request("PATCH", path, payload=payload)
        if response.status_code >= 400:
            raise RuntimeError(f"PATCH {path} failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")

    def row_id_by_key(self, entity_set: str, key_column: str, key_value: str) -> str:
        row_id_column = f"{entity_set[:-1]}id"
        data = self.dv.get_json(
            f"{entity_set}?$select={row_id_column}&$filter={key_column} eq '{escape_odata_string(key_value)}'&$top=1"
        ) or {}
        rows = data.get("value") or []
        if not rows:
            raise RuntimeError(f"Upserted {entity_set} row was not found by alternate key")
        return rows[0][row_id_column]

    def child_rows(self, entity_set: str, key_column: str, report_row_id: str) -> list[dict[str, Any]]:
        row_id_column = f"{entity_set[:-1]}id"
        return self.collect(
            f"{entity_set}?$select={row_id_column},{key_column}"
            f"&$filter=_mp_submissionreportrow_value eq {report_row_id}&$top=5000",
            5000,
        )

    def delete(self, entity_set: str, row_id: str) -> None:
        response = self.dv.request("DELETE", f"{entity_set}({row_id})")
        if response.status_code not in {200, 204}:
            raise RuntimeError(
                f"DELETE {entity_set}({row_id}) failed: HTTP {response.status_code} {self.deploy.safe_error(response)}"
            )


def summarize(rows: list[ProjectionRows]) -> dict[str, Any]:
    failed = sum(1 for row in rows if row.report_row.get("mp_projectionstatus") == PROJECTION_FAILED)
    return {
        "submissions_projected": len(rows),
        "failed_projections": failed,
        "report_rows": len(rows),
        "repeat_rows": sum(len(row.repeat_rows) for row in rows),
        "answer_rows": sum(len(row.answer_rows) for row in rows),
        "writes_performed": False,
    }


def main() -> int:
    args = parse_args()
    deploy = load_deploy_module()
    settings = deploy.build_settings(
        argparse.Namespace(env_file=args.env_file, schema_dir=None, schema_file=None, execute=False, no_publish=False)
    )
    if settings.deploy_target.lower() != "dev":
        raise SystemExit(f"Refusing non-dev target: {settings.deploy_target}")
    client = ProjectionClient(deploy, settings, deploy.get_token(settings))

    submissions = client.submissions(args.top, submitted_only=not args.include_all_statuses, instance_id=args.instance_id)
    projected_at = utc_now_iso()
    projections: list[ProjectionRows] = []
    for submission in submissions:
        version = client.latest_version(submission["mp_instanceid"])
        if not version:
            continue
        metadata = parse_metadata(version.get("mp_submissionjson"))
        form_version_id = metadata.get("formVersionId") or version.get("_mp_formversion_value")
        form_version_exists = bool(form_version_id and client.row_exists("mp_formversions", form_version_id))
        projections.append(build_projection(submission, version, projected_at, form_version_exists=form_version_exists))

    summary = summarize(projections)

    if args.execute:
        prefix = settings.publisher_prefix
        required_tables = {
            "mp_submissionreportrow": "mp_submissionreportrows",
            "mp_submissionrepeatrow": "mp_submissionrepeatrows",
            "mp_submissionanswer": "mp_submissionanswers",
        }
        missing = [logical for logical in required_tables if not client.table_exists(logical)]
        if missing:
            raise SystemExit(f"Reporting tables are missing; deploy schema before --execute: {', '.join(missing)}")
        for projection in projections:
            report = projection.report_row
            stale_report = dict(report)
            stale_report["mp_projectionstatus"] = PROJECTION_STALE
            stale_report["mp_projectedat"] = None
            stale_report["mp_projectionerror"] = None
            stale_report["mp_rootanswersjson"] = "{}"
            if report.get("mp_projectionstatus") == PROJECTION_FAILED:
                stale_report = report
            client.upsert("mp_submissionreportrows", "mp_reportkey", report["mp_reportkey"], stale_report)
            report_row_id = client.row_id_by_key("mp_submissionreportrows", "mp_reportkey", report["mp_reportkey"])
            for repeat in projection.repeat_rows:
                client.upsert("mp_submissionrepeatrows", "mp_repeatrowkey", repeat["mp_repeatrowkey"], repeat)
            for answer in projection.answer_rows:
                client.upsert("mp_submissionanswers", "mp_answerkey", answer["mp_answerkey"], answer)
            expected_answer_keys = {row["mp_answerkey"] for row in projection.answer_rows}
            for existing in client.child_rows("mp_submissionanswers", "mp_answerkey", report_row_id):
                if existing.get("mp_answerkey") not in expected_answer_keys:
                    client.delete("mp_submissionanswers", existing["mp_submissionanswerid"])
            expected_repeat_keys = {row["mp_repeatrowkey"] for row in projection.repeat_rows}
            for existing in client.child_rows("mp_submissionrepeatrows", "mp_repeatrowkey", report_row_id):
                if existing.get("mp_repeatrowkey") not in expected_repeat_keys:
                    client.delete("mp_submissionrepeatrows", existing["mp_submissionrepeatrowid"])
            if report.get("mp_projectionstatus") != PROJECTION_FAILED:
                client.upsert("mp_submissionreportrows", "mp_reportkey", report["mp_reportkey"], report)
        summary["writes_performed"] = True
        summary["publisher_prefix"] = prefix

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("# TACATDP Reporting Projection Builder")
        print(f"Target: {settings.deploy_target}")
        print(f"Environment: {settings.environment_url}")
        print(f"Mode: {'execute' if args.execute else 'dry-run'}")
        print(f"Canonical submissions read: {len(submissions)}")
        print(f"Report rows: {summary['report_rows']}")
        print(f"Repeat rows: {summary['repeat_rows']}")
        print(f"Answer rows: {summary['answer_rows']}")
        print(f"Failed projections: {summary['failed_projections']}")
        print(f"Writes performed: {str(summary['writes_performed']).lower()}")
        if projections:
            sample = projections[0]
            sample_payload = {
                "report_key": sample.report_row.get("mp_reportkey"),
                "instance_id": sample.report_row.get("mp_instanceid"),
                "display_name": sample.report_row.get("mp_displayname"),
                "answer_rows": len(sample.answer_rows),
                "repeat_rows": len(sample.repeat_rows),
            }
            print(json.dumps(sample_payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
