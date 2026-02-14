from sdf_plan.integrations.crewai import SDFTool


def main():
    tool = SDFTool(api_base="http://localhost:8080", api_key="sk_test_replace_me")
    print("Created CrewAI-style tool adapter:", tool.name)
    print("Call tool.run(goal, context=..., tools=...) once your API key is configured.")


if __name__ == "__main__":
    main()
