#!/usr/bin/env python3
"""Validate the read-only User Activation Diagnostics slice."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
TYPES = ROOT / "powerpages/webforms-spa/src/powerpages-api/types.ts"
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"
DOC = ROOT / "docs/powerpages-odk-webforms/access-activation-diagnostics-20260731.md"
WEBAPI_CONFIG = ROOT / "scripts/powerpages-configure-webapi.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require_terms(path: Path, terms: tuple[str, ...]) -> None:
    text = read(path)
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing required term: {term}")


def main() -> int:
    require_terms(
        TYPES,
        (
            "UserActivationDiagnostic",
            "ActivationCheckState",
            "ActivationNextAction",
            "'Send code'",
            "'Await redemption'",
            "'Ready'",
        ),
    )
    require_terms(
        CLIENT,
        (
            "listUserActivationDiagnostics",
            "listContactDiagnosticsByEmail",
            "listInvitationDiagnosticsByContact",
            "listExternalIdentityDiagnosticsByContact",
            "toActivationDiagnostic",
            "resolveActivationNextAction",
            "describeActivationDiagnostic",
            "/_api/adx_invitations",
            "/_api/adx_externalidentities",
        ),
    )
    client_text = read(CLIENT)
    if "createRecord('/_api/adx_externalidentities'" in client_text or "createRecord('/_api/adx_invitations'" in client_text:
        fail("activation diagnostics must not create authentication or invitation records")
    require_terms(
        VIEW,
        (
            "activationDiagnostics",
            "activeSystemActivitySection === 'onboarding'",
            "User activation diagnostics",
            "Activation proof",
            "formatActivationState",
            "nextActionTone",
            "Refresh activation diagnostics",
        ),
    )
    require_terms(
        DOC,
        (
            "invitation redemption creates a Power Pages external identity",
            "Do not create contacts, invitations, assignments, or external identities",
            "diagnostics tables are not exposed",
            "Hosted CRDB verification",
        ),
    )
    require_terms(
        WEBAPI_CONFIG,
        (
            '"logical": "adx_invitation"',
            '"logical": "adx_externalidentity"',
            "TACATDP Invitations Admin Diagnostics",
            "TACATDP ExternalIdentities Admin Diagnostics",
            "adx_identity_username,adx_identity_logonenabled,adx_identity_emailaddress1confirmed",
        ),
    )
    print("PASS: User Activation Diagnostics slice is present and read-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
