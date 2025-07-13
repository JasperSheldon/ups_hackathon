# main.py
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import json
import os
from dotenv import load_dotenv
from agent import PolicyAnalystAgent

load_dotenv() # Load environment variables from .env


async def main():
    
    session_service = InMemorySessionService()
    app_name = "fraud_policy_generator_app_v2"
    user_id = "user_rego_gen"
    session_id = "policy_gen_session_v2_001"
    sample_logs_content = {
          "fraud_detection_logs": {
            "analysis_date": "2025-07-11",
            "platform": "mobile_delivery_app",
            "users": [
              {
                "uid": "USER_001",
                "user_profile": { "account_created": "2025-01-15T08:30:00Z", "email": "normal.user@email.com", "phone": "+91-9876543210", "verification_status": "verified", "total_orders": 45, "account_age_days": 177 },
                "fraud_scenario": "normal_behavior",
                "risk_score": 0.1,
                "sessions": [ { "session_id": "SESS_001_001", "start_time": "2025-07-11T09:00:00Z", "end_time": "2025-07-11T09:15:00Z", "duration_minutes": 15, "device_info": { "device_id": "DEV_SAMSUNG_001", "device_type": "mobile", "os": "Android", "os_version": "14.0", "app_version": "2.1.3", "device_model": "Samsung Galaxy S24" }, "network_info": { "ip_address": "192.168.1.100", "location": { "latitude": 28.7041, "longitude": 77.1025, "city": "New Delhi", "country": "IN" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-11T09:00:00Z", "details": { "login_method": "password", "success": "true" } }, { "event_type": "order_create", "timestamp": "2025-07-11T09:05:00Z", "details": { "order_id": "ORD_001_001", "package_type": "document", "pickup_address": "123 Main St, New Delhi, IN", "delivery_address": "456 Oak Ave, New Delhi, IN", "declared_value": 500, "payment_method": "credit_card", "payment_id": "PAY_001_001" } }, { "event_type": "logout", "timestamp": "2025-07-11T09:15:00Z", "details": { "logout_type": "manual" } } ] } ]
              }    
              
            ]
          }
        }

    # Create a session
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

    # Initialize your agent
    policy_agent = PolicyAnalystAgent()
    runner = Runner(agent=policy_agent, app_name=app_name, session_service=session_service)

    # --- 6. Define Agent Interaction Logic ---
    async def call_agent_and_print(
        runner_instance: Runner,
        agent_instance: PolicyAnalystAgent,
        session_id: str,
        # query_json expects a string that is a JSON object like {"instruction": "...", "log_data": {...}}
        query_json_string: str # Renamed for clarity
    ):
        """Sends a query to the specified agent/runner and prints results."""
        print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {query_json_string}")

        # Pass the pre-formatted JSON string directly as text
        user_content = types.Content(role='user', parts=[types.Part(text=query_json_string)])

        final_response_content = "No final response received."
        async for event in runner_instance.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text

        print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

        current_session = session_service.get_session(app_name=app_name,
                                                    user_id=user_id,
                                                    session_id=session_id)
        stored_output = current_session.state.get(agent_instance.output_key)

        print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
        try:
            parsed_output = json.loads(stored_output)
            print(json.dumps(parsed_output, indent=2))
        except (json.JSONDecodeError, TypeError):
            print(stored_output)
        print("-" * 30)

    # Construct the query JSON as requested: {"instruction": "...", "log_data": {...}}
    query_payload = {
        "instruction": "Please analyze the provided raw log data for distinct fraud patterns (referring to 'fraud_scenario' and associated data) and generate Rego policies in the exact JSON format for each unique fraud scenario. Make sure the Rego policies operate on a single 'user' object as input.",
        "log_data": sample_logs_content # Directly embed the Python dictionary
    }

    # Convert the entire payload to a JSON string before passing to the agent
    user_message_json_string = json.dumps(query_payload, indent=2)

    await call_agent_and_print(runner, policy_agent, session_id, user_message_json_string)

if __name__ == "__main__":
    print("Starting Fraud Policy Generation Agent...")
    asyncio.run(main())