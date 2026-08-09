#!/usr/bin/env python3
"""Assign a Power Pages enhanced-model web role to a portal contact.

This uses Dataverse Web API as an administrator/configuration channel. It is
intended for bounded dev/admin bootstrap work such as assigning a known tester
to the Administrators role after they have an active Contact row.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


def load_deploy_module() -> Any:
    module_path = Path(__file__).resolve().parent / "dataverse-schema-deploy.py"
    spec = importlib.util.spec_from_file_location("dataverse_schema_deploy", module_path)
    if not spec or not spec.loader:
        raise SystemExit(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dataverse_schema_deploy"] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assign a Power Pages web role to an active portal contact.")
    parser.add_argument("--env-file", default=".env", help="Environment file containing Power Platform settings.")
    parser.add_argument("--email", required=True, help="Portal contact email address.")
    parser.add_argument("--role", required=True, help="Power Pages web role name, for example Administrators.")
    parser.add_argument("--execute", action="store_true", help="Perform the role assignment. Without this flag only a dry-run summary is shown.")
    return parser.parse_args()


def escape_odata(value: str) -> str:
    return value.replace("'", "''")


class RoleAssigner:
    def __init__(self, deploy: Any, settings: Any, token: str) -> None:
        self.deploy = deploy
        self.dv = deploy.Dataverse(settings, token)

    def find_contact(self, email: str) -> str:
        data = self.dv.get_json(
            "contacts?$select=contactid,emailaddress1,statecode"
            f"&$filter=emailaddress1 eq '{escape_odata(email)}'&$top=1"
        )
        values = (data or {}).get("value") or []
        if not values:
            raise RuntimeError(f"Portal contact not found: {email}")
        if values[0].get("statecode") != 0:
            raise RuntimeError(f"Portal contact is not active: {email}")
        return values[0]["contactid"]

    def find_role(self, role_name: str) -> str:
        data = self.dv.get_json(
            "powerpagecomponents?$select=powerpagecomponentid,name,powerpagecomponenttype"
            f"&$filter=name eq '{escape_odata(role_name)}' and powerpagecomponenttype eq 11"
        )
        values = (data or {}).get("value") or []
        if not values:
            raise RuntimeError(f"Power Pages web role not found: {role_name}")
        if len(values) > 1:
            raise RuntimeError(f"Multiple Power Pages web roles named {role_name}; use a unique role name before assigning.")
        return values[0]["powerpagecomponentid"]

    def role_link_exists(self, role_id: str, contact_id: str) -> bool:
        existing = self.dv.get_json(
            f"powerpagecomponents({role_id})/powerpagecomponent_mspp_webrole_contact"
            "?$select=contactid&$top=500"
        )
        return any(row.get("contactid") == contact_id for row in (existing or {}).get("value", []))

    def ensure_role_link(self, role_id: str, contact_id: str, email: str, role_name: str, execute: bool) -> None:
        if self.role_link_exists(role_id, contact_id):
            print(f"exists: {email} already has Power Pages role {role_name}")
            return
        if not execute:
            print(f"would create: {email} -> Power Pages role {role_name}")
            return
        payload = {"@odata.id": f"{self.dv.base}/contacts({contact_id})"}
        response = self.dv.request("POST", f"powerpagecomponents({role_id})/powerpagecomponent_mspp_webrole_contact/$ref", payload=payload)
        if response.status_code >= 400:
            message = self.deploy.safe_error(response)
            if "already" not in message.lower() and "duplicate" not in message.lower():
                raise RuntimeError(f"Associate contact role failed: HTTP {response.status_code} {message}")
        if not self.role_link_exists(role_id, contact_id):
            raise RuntimeError("Associate contact role did not create a readable relationship link")
        print(f"created: {email} -> Power Pages role {role_name}")


def main() -> int:
    args = parse_args()
    deploy = load_deploy_module()
    settings = deploy.build_settings(argparse.Namespace(env_file=args.env_file, schema_dir=None, schema_file=None, execute=False, no_publish=False))
    if settings.deploy_target.lower() != "dev":
        raise SystemExit(f"Refusing non-dev deployment target: {settings.deploy_target}")
    token = deploy.get_token(settings)
    assigner = RoleAssigner(deploy, settings, token)
    contact_id = assigner.find_contact(args.email)
    role_id = assigner.find_role(args.role)
    print("# TACATDP Power Pages Web Role Assignment")
    print(f"Mode: {'execute' if args.execute else 'dry-run'}")
    print(f"Environment: {settings.environment_url}")
    print(f"Contact: {args.email}")
    print(f"Role: {args.role}")
    print(f"Contact ID: {contact_id}")
    print(f"Role ID: {role_id}")
    assigner.ensure_role_link(role_id, contact_id, args.email, args.role, args.execute)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
