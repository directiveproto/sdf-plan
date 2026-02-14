from sdf_plan.compat import assert_schema_compat


def test_unknown_version_raises():
    try:
        assert_schema_compat("9.9.9", "hash")
        assert False, "expected RuntimeError"
    except RuntimeError:
        assert True
