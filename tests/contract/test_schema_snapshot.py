import json
import os
from pathlib import Path

from sdf_plan.models import PlanSpecEnvelope


SNAPSHOT = Path(__file__).resolve().parents[1] / "fixtures" / "schema" / "current.schema.json"


def _canonical_schema() -> str:
    schema = _normalize_schema(PlanSpecEnvelope.model_json_schema())
    return json.dumps(schema, sort_keys=True, indent=2) + "\n"


def _normalize_schema(value):
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            # Pydantic may include this explicitly in some environments.
            if key == "additionalProperties" and item is True:
                continue
            out[key] = _normalize_schema(item)
        return out
    if isinstance(value, list):
        return [_normalize_schema(v) for v in value]
    return value


def test_schema_snapshot():
    current = _canonical_schema()
    if os.getenv("UPDATE_SCHEMA_SNAPSHOT") == "1":
        SNAPSHOT.write_text(current, encoding="utf-8")
    expected_obj = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    expected = json.dumps(_normalize_schema(expected_obj), sort_keys=True, indent=2) + "\n"
    assert current == expected
