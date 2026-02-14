import sdf_plan


def test_version_attr_present():
    assert isinstance(sdf_plan.__version__, str)
    assert len(sdf_plan.__version__) > 0
