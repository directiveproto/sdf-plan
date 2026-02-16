from __future__ import annotations

import pytest

from sdf_plan.policy import load_default_tool_risk_map, load_tool_risk_map


def test_default_loads_v2_map() -> None:
    m = load_default_tool_risk_map()
    assert "web.search" in m
    assert "cloud.deploy" in m
    assert len(m) >= 30


def test_explicit_version_v2_matches_default() -> None:
    a = load_default_tool_risk_map()
    b = load_default_tool_risk_map(version="v2")
    assert a == b


def test_legacy_default_alias_map_loads() -> None:
    m = load_default_tool_risk_map(version="v1")
    assert "filesystem.write" in m
    assert m["filesystem.write"]["category"] in {"write_local", "write_external"}


def test_v2_is_materially_different_from_v1() -> None:
    v1 = load_default_tool_risk_map(version="v1")
    v2 = load_default_tool_risk_map(version="v2")
    assert v1 != v2
    assert v1["filesystem.copy"]["category"] == "write_local"
    assert v2["filesystem.copy"]["category"] == "write_external"
    assert "browser.navigate" in v2
    assert "browser.navigate" not in v1


def test_load_tool_risk_map_respects_version_with_overrides() -> None:
    override = {"custom.tool": {"category": "network", "risk_flags": ["network_access"]}}
    merged = load_tool_risk_map(override, version="v2")
    assert "custom.tool" in merged
    assert merged["custom.tool"]["category"] == "network"


def test_invalid_version_raises() -> None:
    with pytest.raises(ValueError, match="unsupported tool map version"):
        load_default_tool_risk_map(version="v9")

