from sdf_plan.core import normalize_to_ir


def test_openai_variants_normalize_to_same_ir() -> None:
    v1 = {
        "tool_calls": [
            {
                "id": "tc_1",
                "name": "filesystem.write",
                "arguments": {"path": "/tmp/a", "content": "x"},
            }
        ]
    }

    v2 = {
        "tool_calls": [
            {
                "id": "tc_1",
                "function": {
                    "name": "filesystem.write",
                    "arguments": '{"content":"x","path":"/tmp/a"}',
                },
            }
        ]
    }

    v3 = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "id": "tc_1",
                            "type": "function",
                            "function": {
                                "name": "filesystem.write",
                                "arguments": '{"path":"/tmp/a","content":"x"}',
                            },
                        }
                    ]
                }
            }
        ]
    }

    ir1 = normalize_to_ir(v1, input_format="openai").model_dump()
    ir2 = normalize_to_ir(v2, input_format="openai").model_dump()
    ir3 = normalize_to_ir(v3, input_format="openai").model_dump()

    # ignore metadata differences not part of semantic equivalence in this test
    for ir in (ir1, ir2, ir3):
        ir["actions"][0]["meta"].pop("type", None)

    assert ir1 == ir2 == ir3
