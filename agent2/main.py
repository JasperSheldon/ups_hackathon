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
              # Example for a fraud scenario (add more based on your actual data for distinct policies)
              ,{
                "uid": "USER_002",
                "user_profile": { "account_created": "2025-07-10T10:00:00Z", "email": "fraud.user@email.com", "phone": "+91-9988776655", "verification_status": "unverified", "total_orders": 1, "account_age_days": 1 },
                "fraud_scenario": "new_user_high_value_order",
                "risk_score": 0.8,
                "sessions": [ { "session_id": "SESS_002_001", "start_time": "2025-07-10T10:05:00Z", "end_time": "2025-07-10T10:10:00Z", "duration_minutes": 5, "device_info": { "device_id": "DEV_ANDROID_002", "device_type": "mobile", "os": "Android", "os_version": "13.0", "app_version": "2.1.3", "device_model": "Xiaomi Redmi Note 12" }, "network_info": { "ip_address": "203.0.113.45", "location": { "latitude": 19.0760, "longitude": 72.8777, "city": "Mumbai", "country": "IN" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-10T10:05:00Z", "details": { "login_method": "otp", "success": "true" } }, { "event_type": "order_create", "timestamp": "2025-07-10T10:07:00Z", "details": { "order_id": "ORD_002_001", "package_type": "electronics", "pickup_address": "10 MG Road, Mumbai, IN", "delivery_address": "789 High St, Mumbai, IN", "declared_value": 150000, "payment_method": "upi", "payment_id": "PAY_002_001" } }, { "event_type": "logout", "timestamp": "2025-07-10T10:10:00Z", "details": { "logout_type": "manual" } } ] } ]
              },
              {
                "uid": "USER_003",
                "user_profile": { "account_created": "2025-06-01T12:00:00Z", "email": "suspicious.user@email.com", "phone": "+91-9000000000", "verification_status": "verified", "total_orders": 10, "account_age_days": 41 },
                "fraud_scenario": "ip_change_suspicious",
                "risk_score": 0.7,
                "sessions": [ 
                    { "session_id": "SESS_003_001", "start_time": "2025-07-11T14:00:00Z", "end_time": "2025-07-11T14:10:00Z", "duration_minutes": 10, "device_info": { "device_id": "DEV_IPHONE_003", "device_type": "mobile", "os": "iOS", "os_version": "17.0", "app_version": "2.1.3", "device_model": "iPhone 15 Pro" }, "network_info": { "ip_address": "103.20.100.10", "location": { "latitude": 30.7333, "longitude": 76.7794, "city": "Chandigarh", "country": "IN" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-11T14:00:00Z", "details": { "login_method": "password", "success": "true" } } ] },
                    { "session_id": "SESS_003_002", "start_time": "2025-07-11T14:15:00Z", "end_time": "2025-07-11T14:20:00Z", "duration_minutes": 5, "device_info": { "device_id": "DEV_IPHONE_003", "device_type": "mobile", "os": "iOS", "os_version": "17.0", "app_version": "2.1.3", "device_model": "iPhone 15 Pro" }, "network_info": { "ip_address": "45.10.20.30", "location": { "latitude": 12.9716, "longitude": 77.5946, "city": "Bengaluru", "country": "IN" } }, "events": [ { "event_type": "order_create", "timestamp": "2025-07-11T14:16:00Z", "details": { "order_id": "ORD_003_001", "package_type": "document", "pickup_address": "1 Fictional Rd, Chandigarh, IN", "delivery_address": "2 Fictional Blvd, Bengaluru, IN", "declared_value": 2000, "payment_method": "credit_card", "payment_id": "PAY_003_001" } } ] }
                ]
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
        "instruction": "The provided log_data is ONLY for understanding the JSON structure and available parameters. Please search the web for new or emerging fraud scenarios and informative things in the package delivery industry. Based on your search results, create detailed hypothetical fraud scenarios and then generate corresponding Rego policies. The Rego policies must utilize the session parameters from the log_data's structure (e.g., user_profile.account_age_days, sessions[i].events[j].event_type, network_info.ip_address) but should infer plausible conditions and thresholds for these new scenarios, not based on the sample data's values.",
        "log_data": sample_logs_content # Directly embed the Python dictionary
    }

    # Convert the entire payload to a JSON string before passing to the agent
    user_message_json_string = json.dumps(query_payload, indent=2)

    await call_agent_and_print(runner, policy_agent, session_id, user_message_json_string)

if __name__ == "__main__":
    print("Starting Fraud Policy Generation Agent...")
    asyncio.run(main())