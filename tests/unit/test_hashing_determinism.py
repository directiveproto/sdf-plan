from __future__ import annotations

import pytest

from sdf_plan.core.hashing import canonical_json, hash_canonical


def test_hash_is_stable_for_dict_key_order_variance() -> None:
    a = {"tool": "x", "args": {"b": 2, "a": 1}}
    b = {"args": {"a": 1, "b": 2}, "tool": "x"}
    assert canonical_json(a) == canonical_json(b)
    assert hash_canonical(a) == hash_canonical(b)


def test_hash_is_stable_for_nested_key_order_variance() -> None:
    a = {"x": {"k2": {"n": 1, "m": 2}, "k1": True}}
    b = {"x": {"k1": True, "k2": {"m": 2, "n": 1}}}
    assert hash_canonical(a) == hash_canonical(b)


def test_numeric_and_string_values_are_distinct() -> None:
    assert hash_canonical({"x": 1}) != hash_canonical({"x": "1"})


def test_integral_float_and_int_are_canonicalized_same() -> None:
    assert hash_canonical({"x": 1}) == hash_canonical({"x": 1.0})


def test_nulls_are_stable() -> None:
    a = {"x": None, "y": [1, None, {"z": None}]}
    b = {"y": [1, None, {"z": None}], "x": None}
    assert hash_canonical(a) == hash_canonical(b)


def test_non_finite_floats_raise() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        canonical_json({"x": float("nan")})
