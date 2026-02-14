from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib import error, request

from sdf_plan.compat import assert_schema_compat, package_version


def get_server_schema(api_base: str, timeout_sec: float = 15.0) -> Dict[str, Any]:
    url = api_base.rstrip("/") + "/v1/schema"
    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"SDF schema HTTP {e.code}: {body}") from e
    except error.URLError as e:
        raise RuntimeError(f"SDF schema connection error: {e}") from e


def decompose_via_api(
    *,
    api_base: str,
    api_key: str,
    goal: str,
    context: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    mode: str = "deterministic",
    max_steps: int = 12,
    safety_mode: str = "safe",
    output_format: str = "sdf.v1.2",
    timeout_sec: float = 15.0,
    check_schema_compat: bool = True,
) -> Dict[str, Any]:
    if check_schema_compat:
        schema = get_server_schema(api_base=api_base, timeout_sec=timeout_sec)
        server_hash = schema.get("schema_hash")
        if server_hash:
            assert_schema_compat(package_version(), server_hash)

    payload = {
        "goal": goal,
        "context": context or {},
        "tools": tools or [],
        "mode": mode,
        "options": {
            "max_steps": max_steps,
            "safety_mode": safety_mode,
            "output_format": output_format,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    url = api_base.rstrip("/") + "/v1/decompose"
    req = request.Request(
        url,
        method="POST",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"SDF API HTTP {e.code}: {body}") from e
    except error.URLError as e:
        raise RuntimeError(f"SDF API connection error: {e}") from e
