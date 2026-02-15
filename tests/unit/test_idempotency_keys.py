from __future__ import annotations

from sdf_plan.gate.idempotency import apply_exclusions, args_hash, generate_idempotency_key


def test_same_semantic_args_same_hash_and_key() -> None:
    args_a = {"b": 2, "a": {"x": 1, "y": 2}}
    args_b = {"a": {"y": 2, "x": 1}, "b": 2}

    assert args_hash(args_a) == args_hash(args_b)
    assert generate_idempotency_key(scope="w1", tool_name="db.execute", args=args_a) == generate_idempotency_key(
        scope="w1", tool_name="db.execute", args=args_b
    )


def test_scope_affects_idempotency_key() -> None:
    args = {"query": "update"}
    k1 = generate_idempotency_key(scope="workspace-A", tool_name="db.execute", args=args)
    k2 = generate_idempotency_key(scope="workspace-B", tool_name="db.execute", args=args)
    assert k1 != k2


def test_tool_name_affects_idempotency_key() -> None:
    args = {"path": "/tmp/x"}
    k1 = generate_idempotency_key(scope="w1", tool_name="filesystem.write", args=args)
    k2 = generate_idempotency_key(scope="w1", tool_name="filesystem.delete", args=args)
    assert k1 != k2


def test_excluded_top_level_field_ignored() -> None:
    a = {"path": "/tmp/a", "timestamp": 111}
    b = {"path": "/tmp/a", "timestamp": 222}
    assert args_hash(a, exclude_fields=["timestamp"]) == args_hash(b, exclude_fields=["timestamp"])


def test_excluded_nested_field_ignored() -> None:
    a = {"payload": {"id": "x", "meta": {"nonce": "n1"}}}
    b = {"payload": {"id": "x", "meta": {"nonce": "n2"}}}
    ex = ["payload.meta.nonce"]
    assert args_hash(a, exclude_fields=ex) == args_hash(b, exclude_fields=ex)


def test_apply_exclusions_does_not_mutate_input() -> None:
    src = {"a": 1, "meta": {"nonce": "n"}}
    out = apply_exclusions(src, exclude_fields=["meta.nonce"])
    assert src["meta"]["nonce"] == "n"
    assert out["meta"] == {}


def test_numeric_string_edge_case_remains_distinct() -> None:
    k1 = generate_idempotency_key(scope="w1", tool_name="x", args={"v": 1})
    k2 = generate_idempotency_key(scope="w1", tool_name="x", args={"v": "1"})
    assert k1 != k2
