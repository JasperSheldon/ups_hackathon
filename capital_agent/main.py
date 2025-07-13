import json # Needed for pretty printing dicts
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field
from google.adk.models.lite_llm import LiteLlm
import os


APP_NAME = "agent_comparison_app"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "openrouter/anthropic/claude-3-haiku"  # Updated to use Claude

class CountryInput(BaseModel):
    country: str = Field(description="The country to get information about.")


class CapitalInfoOutput(BaseModel):
    capital: str = Field(description="The capital city of the country.")
    # Note: Population is illustrative; the LLM will infer or estimate this
    # as it cannot use tools when output_schema is set.
    population_estimate: str = Field(description="An estimated population of the capital city.")


model = LiteLlm(
    model=MODEL_NAME,
    api_key="",
    # headers={
    #     "HTTP-Referer": "https://github.com/JasperSheldon/machine-learning-models",
    #     "X-Title": "Capital City Information Agent"
    # }
)


# --- 3. Define the Tool (Only for the first agent) ---
def get_capital_city(country: str) -> str:
    """Retrieves the capital city of a given country."""
    print(f"\n-- Tool Call: get_capital_city(country='{country}') --")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "japan": "Tokyo",
    }
    result = country_capitals.get(country.lower(), f"Sorry, I couldn't find the capital for {country}.")
    print(f"-- Tool Result: '{result}' --")
    return result

# --- 4. Configure Agents ---

# Agent 1: Uses a tool and output_key
# capital_agent_with_tool = LlmAgent(
#     model=model,
#     name="capital_agent_tool",
#     description="Retrieves the capital city using a specific tool.",
#     instruction="""You are a helpful agent that provides capital city information.
# Your task is to:
# 1. Parse the input JSON containing a country name in format {"country": "country_name"}
# 2. Use the get_capital_city tool to find the capital
# 3. Respond with a clear, concise message stating: "The capital of [country] is [capital]."
# Be direct and avoid any additional commentary.
# """,
#     tools=[get_capital_city],
#     input_schema=CountryInput,
#     output_key="capital_tool_result", # Store final text response
# )

# Agent 2: Uses output_schema (NO tools possible)
structured_info_agent_schema = LlmAgent(
    model=model,
    name="structured_info_agent_schema",
    description="Provides capital and estimated population in a specific JSON format.",
    instruction=f"""You are an agent that provides country information.
The user will provide the country name in a JSON format like {{"country": "country_name"}}.

Use your knowledge to determine the capital and estimate the population. Do not use any tools.
""",
    # *** NO tools parameter here - using output_schema prevents tool use ***
    input_schema=CountryInput,
    # Enforce JSON output structure
    output_key="structured_info_result", # Store final JSON response
)

async def main():
# --- 5. Set up Session Management and Runners ---
    session_service = InMemorySessionService()
    print("Session Service Initialized.")
    # Create separate sessions for clarity, though not strictly necessary if context is managed
    # await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_TOOL_AGENT)
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_SCHEMA_AGENT)

# Create a runner for EACH agent
    # capital_runner = Runner(
    #     agent=capital_agent_with_tool,
    #     app_name=APP_NAME,
    #     session_service=session_service
    # )
    structured_runner = Runner(
        agent=structured_info_agent_schema,
        app_name=APP_NAME,
        session_service=session_service
    )

    # --- 6. Define Agent Interaction Logic ---
    async def call_agent_and_print(
        runner_instance: Runner,
        agent_instance: LlmAgent,
        session_id: str,
        query_json: str
    ):
        """Sends a query to the specified agent/runner and prints results."""
        print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {query_json}")

        user_content = types.Content(role='user', parts=[types.Part(text=query_json)])

        final_response_content = "No final response received."
        async for event in runner_instance.run_async(user_id=USER_ID, session_id=session_id, new_message=user_content):
            # print(f"Event: {event.type}, Author: {event.author}") # Uncomment for detailed logging
            if event.is_final_response() and event.content and event.content.parts:
                # For output_schema, the content is the JSON string itself
                final_response_content = event.content.parts[0].text

        print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

        current_session = session_service.get_session(app_name=APP_NAME,
                                                    user_id=USER_ID,
                                                    session_id=session_id)
        stored_output = current_session.state.get(agent_instance.output_key)

        # Pretty print if the stored output looks like JSON (likely from output_schema)
        print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
        try:
            # Attempt to parse and pretty print if it's JSON
            parsed_output = json.loads(stored_output)
            print(json.dumps(parsed_output, indent=2))
        except (json.JSONDecodeError, TypeError):
            # Otherwise, print as string
            print(stored_output)
        print("-" * 30)


# --- 7. Run Interactions ---

    print("--- Testing Agent with Tool ---")
    # await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "France"}')
    # await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "Canada"}')

    print("\n\n--- Testing Agent with Output Schema (No Tool Use) ---")
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "France"}')
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "Japan"}')

if __name__ == "__main__":
    asyncio.run(main())
