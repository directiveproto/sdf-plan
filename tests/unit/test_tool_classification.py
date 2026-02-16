import json

from sdf_plan.policy import classify_tool, load_default_tool_risk_map, load_tool_risk_map


def test_unknown_tool_defaults_to_unknown_category() -> None:
    c = classify_tool("not.real.tool")
    assert c.category == "unknown"
    assert c.risk_flags == ["unknown_tool"]


def test_default_risk_map_contains_known_tools() -> None:
    m = load_default_tool_risk_map()
    assert "filesystem.write" in m
    assert m["filesystem.write"]["category"] == "write_local"


def test_override_loading_from_dict_is_deterministic() -> None:
    override = {
        "filesystem.write": {"category": "write_external", "risk_flags": ["write", "prod_change"]},
        "custom.op": {"category": "network", "risk_flags": ["network_access"]},
    }
    a = load_tool_risk_map(override)
    b = load_tool_risk_map(override)
    assert a == b
    assert a["filesystem.write"]["category"] == "write_external"
    assert a["custom.op"]["risk_flags"] == ["network_access"]


def test_override_loading_from_file_matches_dict(tmp_path) -> None:
    override = {
        "payments.send": {"category": "money", "risk_flags": ["payment", "write"]},
        "another.tool": {"category": "read_only", "risk_flags": []},
    }
    f = tmp_path / "override.json"
    f.write_text(json.dumps(override), encoding="utf-8")

    from_dict = load_tool_risk_map(override)
    from_file = load_tool_risk_map(f)
    assert from_dict == from_file


def test_classify_tool_uses_override_map() -> None:
    merged = load_tool_risk_map({"x.y": {"category": "privileged", "risk_flags": ["shell_exec"]}})
    c = classify_tool("x.y", merged)
    assert c.category == "privileged"
    assert c.risk_flags == ["shell_exec"]


def test_exact_match_overrides_prefix_match() -> None:
    merged = load_tool_risk_map(
        {
            "filesystem.*": {"category": "write_local", "risk_flags": ["write"]},
            "filesystem.read": {"category": "read_only", "risk_flags": []},
        }
    )
    c = classify_tool("filesystem.read", merged)
    assert c.category == "read_only"
    assert c.risk_flags == []


def test_longest_prefix_match_wins() -> None:
    merged = load_tool_risk_map(
        {
            "filesystem.*": {"category": "write_local", "risk_flags": ["write"]},
            "filesystem.secure.*": {"category": "privileged", "risk_flags": ["credential_access"]},
        }
    )
    c = classify_tool("filesystem.secure.write", merged)
    assert c.category == "privileged"
    assert c.risk_flags == ["credential_access"]


def test_prefix_matching_is_deterministic_for_ties() -> None:
    merged = load_tool_risk_map(
        {
            "alpha.beta.*": {"category": "network", "risk_flags": ["network_access"]},
            "alpha.betb.*": {"category": "write_external", "risk_flags": ["write"]},
        }
    )
    first = classify_tool("alpha.beta.tool", merged)
    second = classify_tool("alpha.beta.tool", merged)
    assert first.model_dump() == second.model_dump()
