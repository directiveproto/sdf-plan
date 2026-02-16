from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field


class ToolRiskEntry(BaseModel):
    category: str
    risk_flags: list[str] = Field(default_factory=list)


UNKNOWN_TOOL_ENTRY = ToolRiskEntry(category="unknown", risk_flags=["unknown_tool"])
_SUPPORTED_TOOL_MAP_VERSIONS = {"v1", "v2"}


def _normalize_tool_name(name: str) -> str:
    return (name or "").strip().lower()


def _canonicalize_map(raw: Dict[str, Any]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for key in sorted(raw.keys()):
        norm_key = _normalize_tool_name(key)
        entry = ToolRiskEntry.model_validate(raw[key])
        out[norm_key] = {
            "category": entry.category,
            "risk_flags": list(entry.risk_flags),
        }
    return out


def _map_filename_for_version(version: str) -> str:
    normalized = (version or "v2").strip().lower()
    if normalized not in _SUPPORTED_TOOL_MAP_VERSIONS:
        raise ValueError(f"unsupported tool map version: {version}")
    if normalized == "v1":
        return "default_tool_map.json"
    return "tool_map_v2.json"


def load_default_tool_risk_map(*, version: str = "v2") -> Dict[str, dict]:
    p = Path(__file__).with_name(_map_filename_for_version(version))
    raw = json.loads(p.read_text(encoding="utf-8"))
    return _canonicalize_map(raw)


def load_tool_risk_map(
    overrides: dict | str | Path | None = None,
    *,
    version: str = "v2",
) -> Dict[str, dict]:
    merged = load_default_tool_risk_map(version=version)
    if overrides is None:
        return merged

    if isinstance(overrides, (str, Path)):
        override_data = json.loads(Path(overrides).read_text(encoding="utf-8"))
    elif isinstance(overrides, dict):
        override_data = overrides
    else:
        raise TypeError("overrides must be dict, str, Path, or None")

    override_map = _canonicalize_map(override_data)
    merged.update(override_map)
    return {k: merged[k] for k in sorted(merged.keys())}


def classify_tool(tool_name: str, risk_map: Dict[str, dict] | None = None) -> ToolRiskEntry:
    table = risk_map or load_default_tool_risk_map()
    key = _normalize_tool_name(tool_name)
    raw = table.get(key)
    if raw is None:
        return ToolRiskEntry.model_validate(UNKNOWN_TOOL_ENTRY.model_dump())
    return ToolRiskEntry.model_validate(raw)
