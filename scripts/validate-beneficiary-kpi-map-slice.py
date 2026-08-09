#!/usr/bin/env python3
"""Validate the prototype beneficiary KPI and mapping dashboard slice."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPA = ROOT / "powerpages/webforms-spa"
VIEW = SPA / "src/views/AssignedFormsView.vue"
DOC = ROOT / "docs/powerpages-odk-webforms/beneficiary-kpi-map-slice-20260809.md"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_text(path: Path, expected: str) -> None:
    text = path.read_text()
    if expected not in text:
        fail(f"{path.relative_to(ROOT)} missing required text: {expected}")


def validate_dependencies() -> None:
    package = json.loads((SPA / "package.json").read_text())
    dependencies = package.get("dependencies", {})
    for dependency in ("echarts", "vue-echarts", "leaflet", "@vue-leaflet/vue-leaflet"):
      if dependency not in dependencies:
          fail(f"powerpages/webforms-spa/package.json missing dependency {dependency}")


def validate_view_contract() -> None:
    view = VIEW.read_text()
    required_strings = [
        "const DashboardChart = defineAsyncComponent",
        "import('echarts/core')",
        "import('vue-echarts')",
        "const LeafletMap = defineAsyncComponent",
        "import('leaflet/dist/leaflet.css')",
        "import('@vue-leaflet/vue-leaflet')",
        "interface PrototypeBeneficiaryInsight",
        "const prototypeBeneficiaries = computed<PrototypeBeneficiaryInsight[]>",
        "parseReportRootAnswers(row)",
        "beneficiary_id",
        "customer_id",
        "respondent_id",
        "beneficiaryDistrictCoverage",
        "beneficiaryTypeBreakdown",
        "beneficiaryMapPoints",
        "beneficiaryTypeChartOption",
        "beneficiaryDistrictChartOption",
        "void loadReportingData();",
        "Beneficiary baseline view",
        "DashboardChart class=\"insight-chart\"",
        "LeafletMap",
        "OpenStreetMap contributors",
        "Coordinates are not available in the current projected records",
    ]
    for expected in required_strings:
        if expected not in view:
            fail(f"AssignedFormsView.vue missing required beneficiary visualisation contract: {expected}")

    forbidden_static_imports = [
        "from 'vue-echarts'",
        "from '@vue-leaflet/vue-leaflet'",
        "from 'echarts/core'",
    ]
    for forbidden in forbidden_static_imports:
        if forbidden in view:
            fail(f"visualisation libraries must remain lazy-loaded, found static import: {forbidden}")


def validate_styles() -> None:
    css = (SPA / "src/styles.css").read_text()
    for expected in (
        ".beneficiary-insights-panel",
        ".beneficiary-insights-grid",
        ".insight-chart",
        ".beneficiary-map-shell",
        ".coverage-table",
        "repeat(auto-fit, minmax(180px, 1fr))",
    ):
        if expected not in css:
            fail(f"styles.css missing beneficiary visualisation style: {expected}")


def validate_documentation() -> None:
    for expected in (
        "This slice adds a lightweight beneficiary insight layer",
        "It does not create or deploy new Dataverse tables.",
        "Apache ECharts",
        "Leaflet",
        "MapLibre GL JS remains the future-product option",
        "No deployment is included in this slice.",
    ):
        require_text(DOC, expected)


def main() -> None:
    validate_dependencies()
    validate_view_contract()
    validate_styles()
    validate_documentation()
    print("Beneficiary KPI and mapping slice validation passed.")


if __name__ == "__main__":
    main()
