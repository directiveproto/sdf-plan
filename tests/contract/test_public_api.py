import sdf_plan


def test_public_api_symbols_exist():
    from sdf_plan import PlanSpecEnvelope, PlanStep, preflight_lint

    assert PlanSpecEnvelope is not None
    assert PlanStep is not None
    assert callable(preflight_lint)
    assert hasattr(sdf_plan, "__version__")
