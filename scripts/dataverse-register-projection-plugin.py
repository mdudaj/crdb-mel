#!/usr/bin/env python3
"""Register the TACATDP reporting projection plug-in in a dev Dataverse environment.

The command is dry-run by default. Assembly/type registration can be performed
without an execution user; step/image registration requires an explicit,
enabled, non-deployment Dataverse user.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


DEFAULT_ASSEMBLY = Path(
    "dataverse/Tacatdp.ReportingProjection.Plugin/bin/Release/net462/"
    "Tacatdp.ReportingProjection.Plugin.dll"
)
DEFAULT_CONTRACT = Path(
    "dataverse/Tacatdp.ReportingProjection.Plugin/registration-contract.json"
)
REQUIRED_EXECUTION_ROLE = "TACATDP Projection Processor"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register the TACATDP reporting projection plug-in."
    )
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--assembly-file", default=str(DEFAULT_ASSEMBLY))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument(
        "--execution-user-id",
        help="Dedicated Dataverse system-user GUID for plug-in impersonation.",
    )
    parser.add_argument(
        "--assembly-only",
        action="store_true",
        help="Register/update only the assembly and plug-in type.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform writes. Without this flag, print a dry-run plan.",
    )
    return parser.parse_args()


def load_deploy_module() -> ModuleType:
    path = Path(__file__).with_name("dataverse-schema-deploy.py")
    spec = importlib.util.spec_from_file_location("tacatdp_dataverse_deploy", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Unable to load Dataverse helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def one(dataverse: Any, path: str, label: str) -> dict[str, Any] | None:
    values = dataverse.get_json(path)["value"]
    if len(values) > 1:
        raise SystemExit(f"Multiple {label} records matched; registration is ambiguous.")
    return values[0] if values else None


def guid(value: str) -> str:
    normalized = value.strip().strip("{}").lower()
    if len(normalized) != 36 or normalized.count("-") != 4:
        raise SystemExit("Execution user ID must be a Dataverse GUID.")
    return normalized


def created_id(response: Any) -> str | None:
    entity_uri = response.headers.get("OData-EntityId", "")
    if "(" not in entity_uri:
        return None
    return entity_uri.rsplit("(", 1)[1].rstrip(")").lower()


def patch(dataverse: Any, path: str, payload: dict[str, Any]) -> None:
    response = dataverse.request("PATCH", path, payload=payload, solution_header=True)
    if response.status_code >= 400:
        raise RuntimeError(
            f"PATCH {path} failed: HTTP {response.status_code} "
            f"{dataverse_module.safe_error(response)}"
        )


def validate_target(settings: Any) -> None:
    if settings.deploy_target.strip().lower() not in {"dev", "development"}:
        raise SystemExit(
            f"Refusing plug-in registration for TACATDP_DEPLOY_TARGET={settings.deploy_target!r}."
        )
    if settings.solution_unique_name != "tacatdp_prototype":
        raise SystemExit(
            "Refusing registration outside the tacatdp_prototype development solution."
        )


def validate_execution_user(
    dataverse: Any, execution_user_id: str, deployment_client_id: str
) -> dict[str, Any]:
    user = one(
        dataverse,
        "systemusers?$select=systemuserid,fullname,applicationid,isdisabled"
        f"&$filter=systemuserid eq {execution_user_id}",
        "execution user",
    )
    if user is None:
        raise SystemExit("Execution user does not exist in the target environment.")
    if user.get("isdisabled"):
        raise SystemExit("Execution user is disabled.")
    if str(user.get("applicationid") or "").lower() == deployment_client_id.lower():
        raise SystemExit(
            "Refusing to run the plug-in as the deployment service principal. "
            "Provide a dedicated least-privilege user."
        )
    roles = dataverse.get_json(
        f"systemusers({execution_user_id})/systemuserroles_association?$select=roleid,name"
    )["value"]
    role_names = sorted(role["name"] for role in roles)
    if REQUIRED_EXECUTION_ROLE not in role_names:
        raise SystemExit(
            f"Execution user must have the reviewed {REQUIRED_EXECUTION_ROLE!r} role."
        )
    user["roles"] = role_names
    return user


def find_message_filter(dataverse: Any, message_name: str, entity: str) -> tuple[str, str]:
    message = one(
        dataverse,
        f"sdkmessages?$select=sdkmessageid,name&$filter=name eq '{message_name}'",
        "SDK message",
    )
    if message is None:
        raise SystemExit(f"SDK message not found: {message_name}")
    message_id = message["sdkmessageid"]
    message_filter = one(
        dataverse,
        "sdkmessagefilters?$select=sdkmessagefilterid,primaryobjecttypecode"
        f"&$filter=_sdkmessageid_value eq {message_id} "
        f"and primaryobjecttypecode eq '{entity}'",
        "SDK message filter",
    )
    if message_filter is None:
        raise SystemExit(f"SDK message filter not found: {message_name}/{entity}")
    return message_id, message_filter["sdkmessagefilterid"]


def register_assembly_and_type(
    dataverse: Any,
    contract: dict[str, Any],
    assembly_path: Path,
    execute: bool,
) -> tuple[str | None, str | None]:
    assembly_name = contract["assembly"]
    type_name = contract["type"]
    assembly = one(
        dataverse,
        "pluginassemblies?$select=pluginassemblyid,name,version"
        f"&$filter=name eq '{assembly_name}'",
        "plug-in assembly",
    )
    plugin_type = one(
        dataverse,
        "plugintypes?$select=plugintypeid,typename,_pluginassemblyid_value"
        f"&$filter=typename eq '{type_name}'",
        "plug-in type",
    )
    if not execute:
        return (
            assembly.get("pluginassemblyid") if assembly else None,
            plugin_type.get("plugintypeid") if plugin_type else None,
        )

    content = base64.b64encode(assembly_path.read_bytes()).decode("ascii")
    assembly_payload = {
        "name": assembly_name,
        "description": "TACATDP asynchronous reporting projection refresh.",
        "content": content,
        "isolationmode": 2,
        "sourcetype": 0,
        "version": "1.0.0.0",
    }
    if assembly:
        assembly_id = assembly["pluginassemblyid"]
        patch(dataverse, f"pluginassemblies({assembly_id})", assembly_payload)
    else:
        response = dataverse.post(
            "pluginassemblies", assembly_payload, solution_header=True
        )
        assembly_id = created_id(response)
        if assembly_id is None:
            assembly_id = one(
                dataverse,
                "pluginassemblies?$select=pluginassemblyid"
                f"&$filter=name eq '{assembly_name}'",
                "plug-in assembly",
            )["pluginassemblyid"]

    type_payload = {
        "name": type_name,
        "typename": type_name,
        "friendlyname": "TACATDP Reporting Projection Refresh",
        "description": "Refresh reporting projections after canonical version creation.",
        "pluginassemblyid@odata.bind": f"/pluginassemblies({assembly_id})",
    }
    if plugin_type:
        type_id = plugin_type["plugintypeid"]
        patch(dataverse, f"plugintypes({type_id})", type_payload)
    else:
        response = dataverse.post("plugintypes", type_payload, solution_header=True)
        type_id = created_id(response)
        if type_id is None:
            type_id = one(
                dataverse,
                "plugintypes?$select=plugintypeid"
                f"&$filter=typename eq '{type_name}'",
                "plug-in type",
            )["plugintypeid"]
    return assembly_id, type_id


def register_step_and_image(
    dataverse: Any,
    contract: dict[str, Any],
    type_id: str,
    execution_user_id: str,
    execute: bool,
) -> tuple[str | None, str | None]:
    step_contract = contract["step"]
    image_contract = contract["postImage"]
    step_name = step_contract["name"]
    message_id, filter_id = find_message_filter(
        dataverse, step_contract["message"], step_contract["primaryEntity"]
    )
    step = one(
        dataverse,
        "sdkmessageprocessingsteps?"
        "$select=sdkmessageprocessingstepid,name,stage,mode,rank,_impersonatinguserid_value"
        f"&$filter=name eq '{step_name}'",
        "plug-in step",
    )
    step_payload = {
        "name": step_name,
        "description": "Refresh TACATDP reporting projection asynchronously.",
        "stage": 40,
        "mode": 1,
        "rank": int(step_contract["executionOrder"]),
        "supporteddeployment": 0,
        "asyncautodelete": False,
        "eventhandler_plugintype@odata.bind": f"/plugintypes({type_id})",
        "sdkmessageid@odata.bind": f"/sdkmessages({message_id})",
        "sdkmessagefilterid@odata.bind": f"/sdkmessagefilters({filter_id})",
        "impersonatinguserid@odata.bind": f"/systemusers({execution_user_id})",
    }
    if not execute:
        return (step.get("sdkmessageprocessingstepid") if step else None, None)
    if step:
        step_id = step["sdkmessageprocessingstepid"]
        patch(dataverse, f"sdkmessageprocessingsteps({step_id})", step_payload)
    else:
        response = dataverse.post(
            "sdkmessageprocessingsteps", step_payload, solution_header=True
        )
        step_id = created_id(response)
        if step_id is None:
            step_id = one(
                dataverse,
                "sdkmessageprocessingsteps?$select=sdkmessageprocessingstepid"
                f"&$filter=name eq '{step_name}'",
                "plug-in step",
            )["sdkmessageprocessingstepid"]

    alias = image_contract["alias"]
    image = one(
        dataverse,
        "sdkmessageprocessingstepimages?"
        "$select=sdkmessageprocessingstepimageid,name,entityalias,attributes"
        f"&$filter=_sdkmessageprocessingstepid_value eq {step_id} "
        f"and entityalias eq '{alias}'",
        "post image",
    )
    image_payload = {
        "name": alias,
        "entityalias": alias,
        "imagetype": 1,
        "messagepropertyname": "Target",
        "attributes": ",".join(image_contract["columns"]),
        "sdkmessageprocessingstepid@odata.bind": (
            f"/sdkmessageprocessingsteps({step_id})"
        ),
    }
    if image:
        image_id = image["sdkmessageprocessingstepimageid"]
        patch(dataverse, f"sdkmessageprocessingstepimages({image_id})", image_payload)
    else:
        response = dataverse.post(
            "sdkmessageprocessingstepimages", image_payload, solution_header=True
        )
        image_id = created_id(response)
    return step_id, image_id


def main() -> int:
    args = parse_args()
    args.schema_dir = None
    args.schema_file = None
    global dataverse_module
    dataverse_module = load_deploy_module()
    settings = dataverse_module.build_settings(args)
    validate_target(settings)
    assembly_path = Path(args.assembly_file).resolve()
    contract_path = Path(args.contract).resolve()
    if not assembly_path.is_file():
        raise SystemExit(f"Assembly not found: {assembly_path}")
    if not contract_path.is_file():
        raise SystemExit(f"Registration contract not found: {contract_path}")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["solutionUniqueName"] != settings.solution_unique_name:
        raise SystemExit("Contract and configured solution do not match.")

    env = dataverse_module.load_env(Path(args.env_file).resolve())
    execution_user_id = args.execution_user_id or env.get(
        "TACATDP_PROJECTION_EXECUTION_USER_ID"
    )
    if not args.assembly_only and not execution_user_id:
        raise SystemExit(
            "A dedicated --execution-user-id (or "
            "TACATDP_PROJECTION_EXECUTION_USER_ID) is required for step registration."
        )

    dataverse = dataverse_module.Dataverse(
        settings, dataverse_module.get_token(settings)
    )
    user = None
    if execution_user_id:
        execution_user_id = guid(execution_user_id)
        user = validate_execution_user(
            dataverse, execution_user_id, env["POWER_PLATFORM_CLIENT_ID"]
        )

    assembly_id, type_id = register_assembly_and_type(
        dataverse, contract, assembly_path, args.execute
    )
    step_id = image_id = None
    if not args.assembly_only:
        if type_id is None and not args.execute:
            type_id = "<created-plugin-type-id>"
        step_id, image_id = register_step_and_image(
            dataverse,
            contract,
            type_id,
            execution_user_id,
            args.execute,
        )

    result = {
        "mode": "execute" if args.execute else "dry-run",
        "target": settings.environment_url,
        "solution": settings.solution_unique_name,
        "scope": "assembly-and-type" if args.assembly_only else "full-registration",
        "execution_user": (
            {"systemuserid": execution_user_id, "roles": user["roles"]} if user else None
        ),
        "component_ids": {
            "assembly": assembly_id,
            "type": type_id,
            "step": step_id,
            "post_image": image_id,
        },
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
