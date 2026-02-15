from sdf_plan.core import normalize_to_ir


def test_generic_single_call_normalization() -> None:
    payload = {
        "tool": "db.execute",
        "args": {"query": "update x set y=1"},
        "meta": {"caller": "agent"},
    }

    ir = normalize_to_ir(payload, input_format="generic")
    assert ir.version == "sdf.ir.v1"
    assert len(ir.actions) == 1
    assert ir.actions[0].tool_name == "db.execute"
    assert ir.actions[0].args == {"query": "update x set y=1"}


def test_generic_list_order_is_preserved_deterministically() -> None:
    payload = [
        {"id": "1", "tool": "filesystem.read", "args": {"path": "/a"}},
        {"id": "2", "tool": "filesystem.write", "args": {"path": "/a", "content": "x"}},
    ]
    ir = normalize_to_ir(payload, input_format="generic")
    assert [a.id for a in ir.actions] == ["1", "2"]
    assert [a.tool_name for a in ir.actions] == ["filesystem.read", "filesystem.write"]


def test_generic_dict_tool_calls_variants() -> None:
    payload = {
        "tool_calls": [
            {"name": "payments.send", "arguments": {"amount": 100}},
            {"tool": "filesystem.read", "args": {"path": "/tmp/x"}},
        ]
    }
    ir = normalize_to_ir(payload, input_format="generic")
    assert len(ir.actions) == 2
    assert ir.actions[0].tool_name == "payments.send"
    assert ir.actions[1].tool_name == "filesystem.read"
