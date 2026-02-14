import json
import os
from pathlib import Path

from sdf_plan.models import PlanSpecEnvelope


SNAPSHOT = Path(__file__).resolve().parents[1] / "fixtures" / "schema" / "current.schema.json"


def _canonical_schema() -> str:
    schema = PlanSpecEnvelope.model_json_schema()
    return json.dumps(schema, sort_keys=True, indent=2) + "\n"


def test_schema_snapshot():
    current = _canonical_schema()
    if os.getenv("UPDATE_SCHEMA_SNAPSHOT") == "1":
        SNAPSHOT.write_text(current, encoding="utf-8")
    expected = SNAPSHOT.read_text(encoding="utf-8")
    assert current == expected
