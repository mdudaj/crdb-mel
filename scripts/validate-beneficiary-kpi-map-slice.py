#!/usr/bin/env python3
"""Validate the dedicated TACATDP dashboard prototype route.

The earlier beneficiary KPI/map experiment has been retired from the operational
workspace. Visualisations now belong on the dedicated TACATDP Dashboard route.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPA = ROOT / "powerpages/webforms-spa"
VIEW = SPA / "src/views/AssignedFormsView.vue"
DASHBOARD = SPA / "src/components/dashboard/TacatdpDashboardPage.vue"
DASHBOARD_CARD = SPA / "src/components/dashboard/DashboardCard.vue"
DATA = SPA / "src/prototype/tacatdpDashboardData.ts"
MAP = SPA / "src/assets/maps/tanzania-adm1.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_text(path: Path, expected: str) -> None:
    text = path.read_text()
    if expected not in text:
        fail(f"{path.relative_to(ROOT)} missing required text: {expected}")


def validate_route_split() -> None:
    view = VIEW.read_text()
    for expected in (
        "type AppView = 'dashboard' | 'workspace'",
        "<TacatdpDashboardPage />",
        "activeView === 'workspace'",
        "function openWorkspace()",
        "Data Submissions",
        "Organizations",
    ):
        require_text(VIEW, expected)
    for forbidden in (
        "LeafletMap",
        "beneficiary-insights-panel",
        "prototypeBeneficiaries",
    ):
        if forbidden in view:
            fail(f"operational shell must not keep retired mixed visualisation block: {forbidden}")


def validate_dashboard_component() -> None:
    for expected in (
        "import DashboardCard from './DashboardCard.vue';",
        "import DashboardPage from './DashboardPage.vue';",
        "import KpiCard from './KpiCard.vue';",
        "<DashboardPage>",
        "<KpiCard",
        "<template #footer>",
        "zanzibarRegionNames",
        "core.registerMap('tanzania-mainland-adm1'",
        "map: 'tanzania-mainland-adm1'",
        "<DashboardCard :span=\"8\" title=\"Climate Resilience Outcomes\">",
        "<DashboardCard :span=\"4\" title=\"Training &amp; Capacity Building\">",
        "<DashboardCard :span=\"6\" title=\"Recent Data Submissions\">",
        "<DashboardCard :span=\"6\" variant=\"goal\" title=\"Program Impact Goal\">",
        "insights-grid",
        "charts.MapChart",
        "Loan Portfolio by Type",
        "Disbursement Trend (TZS)",
        "Loans by Region",
        "Technologies Financed",
        "Loan Performance",
        "Climate Resilience Outcomes",
        "Area Under Improved<br>Practices (ha)",
        "Soil Fertility Improved<br>(Reports)",
        "Training &amp; Capacity Building",
        "training-value-with-icon",
        "Recent Data Submissions",
        "Program Impact Goal",
        "Increase the resilience of food crop farmers<br>to climate change through finance,<br>technology and capacity building.",
        "goal-person",
        "Prototype dashboard using demonstration data",
        "May 1 – May 31, 2025",
    ):
        require_text(DASHBOARD, expected)
    for forbidden in (
        "aria-labelledby=\"tacatdp-dashboard-title\"",
        "<h1 id=\"tacatdp-dashboard-title\">Dashboard</h1>",
        "Programme Impact Goal",
        "dashboard-status-footer",
        "map: 'tanzania-adm1'",
    ):
        if forbidden in DASHBOARD.read_text():
            fail(f"dashboard component must not keep retired content/header/footer pattern: {forbidden}")
    for expected in (
        "dashboard-card__header",
        "dashboard-card__content",
        "dashboard-card__footer",
        "<slot name=\"header\">",
        "<slot name=\"footer\" />",
    ):
        require_text(DASHBOARD_CARD, expected)


def validate_prototype_data() -> None:
    for expected in (
        "Active Loans",
        "12,458",
        "Active Borrowers",
        "18,732",
        "Total Disbursed",
        "TZS 152.6B",
        "Repayment Rate",
        "Farmers Trained",
        "tCO₂e Avoided",
        "Morogoro",
        "TZS 21.8B",
        "Solar-powered irrigation pumps",
        "Water Harvesting (Reservoirs)",
    ):
        require_text(DATA, expected)


def validate_geojson() -> None:
    if not MAP.exists():
        fail("Tanzania ADM1 GeoJSON map file is missing")
    data = json.loads(MAP.read_text())
    if data.get("type") != "FeatureCollection":
        fail("Tanzania ADM1 map must be a GeoJSON FeatureCollection")
    features = data.get("features")
    if not isinstance(features, list) or len(features) < 25:
        fail("Tanzania ADM1 map must contain regional boundary features")
    names = {
        feature.get("properties", {}).get("shapeName")
        for feature in features
        if isinstance(feature, dict)
    }
    for expected in ("Morogoro", "Mwanza", "Kagera", "Dodoma", "Pwani"):
        if expected not in names:
            fail(f"Tanzania ADM1 map missing expected region: {expected}")


def main() -> None:
    validate_route_split()
    validate_dashboard_component()
    validate_prototype_data()
    validate_geojson()
    print("Dedicated TACATDP dashboard route validation passed.")


if __name__ == "__main__":
    main()
