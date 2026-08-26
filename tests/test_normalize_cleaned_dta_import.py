from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "normalize-cleaned-dta-import.py"


def load_module():
    spec = importlib.util.spec_from_file_location("normalize_cleaned_dta_import", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_asset_rows_preserves_root_and_loan_repeats() -> None:
    module = load_module()
    root = pd.DataFrame(
        [
            {
                "_uuid": "uuid-1",
                "_submission_time": "2026-08-11",
                "starttime": "2026-08-11",
                "endtime": "2026-08-11",
                "Customer_ID": "customer-1",
                "Customer_Name": "Farmer One",
                "Farmer_Phone": "0712000000",
                "region": "Arusha",
                "district": "Arusha DC",
                "land_after": 2,
            }
        ]
    )
    loans = pd.DataFrame(
        [
            {
                "_submission__uuid": "uuid-1",
                "loan_amount": 1000,
                "loan_year": "2026",
            }
        ]
    )

    rows = module.build_asset_rows(
        root,
        loans,
        project_code="TACATDP",
        form_id="tacatdp_impact_evaluation",
        form_version="2608130924",
        limit=None,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["uuid"] == "uuid-1"
    assert row["sourceKey"] == "TACATDP:kobo:uuid-1"
    assert row["instanceId"] == "kobo:uuid-1"
    assert "loan_value_chain" in row["submissionJson"]
    assert "<land_after>2</land_after>" in row["xformXml"]


def test_child_linkage_marks_cost_rows_deferred() -> None:
    module = load_module()
    root = pd.DataFrame([{"_uuid": "uuid-1"}, {"_uuid": "uuid-2"}])
    loans = pd.DataFrame([{"_submission__uuid": "uuid-1"}, {"_submission__uuid": "uuid-2"}])
    costs = pd.DataFrame([{"PID": "1"}, {"PID": "2"}])

    linkage = module.child_linkage(root, loans, costs)

    assert linkage["loan_rows_matching_root_uuid"] == 2
    assert linkage["loan_link_status"] == "ready"
    assert linkage["cost_rows_matching_root_uuid"] == 0
    assert linkage["cost_link_status"] == "deferred_pid_mapping_required"
