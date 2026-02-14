from sdf_plan.integrations.langgraph import sdf_node


def main():
    node = sdf_node(api_base="http://localhost:8080", api_key="sk_test_replace_me")
    print("Created LangGraph-compatible node:", node.__name__)
    print("Use with state keys: goal, context, tools, mode, options")


if __name__ == "__main__":
    main()
