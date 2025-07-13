# main.py
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
import json
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env



from agent import PolicyAnalystAgent

async def main():
    session_service = InMemorySessionService()
    app_name = "fraud_policy_generator_app_v2"
    user_id = "user_rego_gen"
    session_id = "policy_gen_session_v2_001"

    # Create a session
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

    # Initialize your agent
    policy_agent = PolicyAnalystAgent()
    runner = Runner(agent=policy_agent, app_name=app_name, session_service=session_service)

    log_file_path = "sample_logs_v2.json" # New log file name

    # Create the sample log file if it doesn't exist for testing
    if not os.path.exists(log_file_path):
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
              },
              {
                "uid": "USER_002",
                "user_profile": { "account_created": "2025-07-10T14:30:00Z", "email": "velocity.fraud@email.com", "phone": "+91-8765432109", "verification_status": "verified", "total_orders": 25, "account_age_days": 1 },
                "fraud_scenario": "velocity_fraud",
                "risk_score": 0.9,
                "sessions": [ { "session_id": "SESS_002_001", "start_time": "2025-07-11T10:00:00Z", "end_time": "2025-07-11T10:45:00Z", "duration_minutes": 45, "device_info": { "device_id": "DEV_IPHONE_001", "device_type": "mobile", "os": "iOS", "os_version": "17.5", "app_version": "2.1.3", "device_model": "iPhone 15 Pro" }, "network_info": { "ip_address": "203.192.45.78", "location": { "latitude": 19.0760, "longitude": 72.8777, "city": "Mumbai", "country": "IN" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-11T10:00:00Z", "details": { "login_method": "password", "success": "true" } }, { "event_type": "order_create", "timestamp": "2025-07-11T10:02:00Z", "details": { "order_id": "ORD_002_001", "package_type": "electronics", "pickup_address": "789 Tech Park, Mumbai, IN", "delivery_address": "101 Business District, Mumbai, IN", "declared_value": 50000, "payment_method": "credit_card", "payment_id": "PAY_002_001" } }, { "event_type": "order_create", "timestamp": "2025-07-11T10:05:00Z", "details": { "order_id": "ORD_002_002", "package_type": "electronics", "pickup_address": "789 Tech Park, Mumbai, IN", "delivery_address": "202 Commerce Hub, Mumbai, IN", "declared_value": 45000, "payment_method": "credit_card", "payment_id": "PAY_002_002" } }, { "event_type": "order_create", "timestamp": "2025-07-11T10:08:00Z", "details": { "order_id": "ORD_002_003", "package_type": "electronics", "pickup_address": "789 Tech Park, Mumbai, IN", "delivery_address": "303 Trade Center, Mumbai, IN", "declared_value": 52000, "payment_method": "credit_card", "payment_id": "PAY_002_003" } }, { "event_type": "order_create", "timestamp": "2025-07-11T10:12:00Z", "details": { "order_id": "ORD_002_004", "package_type": "electronics", "pickup_address": "789 Tech Park, Mumbai, IN", "delivery_address": "404 Business Plaza, Mumbai, IN", "declared_value": 48000, "payment_method": "credit_card", "payment_id": "PAY_002_004" } }, { "event_type": "order_create", "timestamp": "2025-07-11T10:15:00Z", "details": { "order_id": "ORD_002_005", "package_type": "electronics", "pickup_address": "789 Tech Park, Mumbai, IN", "delivery_address": "505 Corporate Tower, Mumbai, IN", "declared_value": 55000, "payment_method": "credit_card", "payment_id": "PAY_002_005" } } ] } ]
              },
              {
                "uid": "USER_003",
                "user_profile": { "account_created": "2025-07-11T09:00:00Z", "email": "new.user.high.value@email.com", "phone": "+91-7654321098", "verification_status": "unverified", "total_orders": 1, "account_age_days": 0 },
                "fraud_scenario": "new_user_high_value_order",
                "risk_score": 0.8,
                "sessions": [ { "session_id": "SESS_003_001", "start_time": "2025-07-11T11:00:00Z", "end_time": "2025-07-11T11:10:00Z", "duration_minutes": 10, "device_info": { "device_id": "DEV_ANDROID_TAB_001", "device_type": "tablet", "os": "Android", "os_version": "13.0", "app_version": "2.1.3", "device_model": "Samsung Tab S9" }, "network_info": { "ip_address": "10.0.0.1", "location": { "latitude": 12.9716, "longitude": 77.5946, "city": "Bengaluru", "country": "IN" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-11T11:00:00Z", "details": { "login_method": "otp", "success": "true" } }, { "event_type": "order_create", "timestamp": "2025-07-11T11:05:00Z", "details": { "order_id": "ORD_003_001", "package_type": "jewelry", "pickup_address": "123 Garden City, Bengaluru, IN", "delivery_address": "789 Tech Park, Bengaluru, IN", "declared_value": 150000, "payment_method": "bank_transfer", "payment_id": "PAY_003_001" } } ] } ]
              },
              {
                "uid": "USER_004",
                "user_profile": { "account_created": "2025-06-01T09:00:00Z", "email": "ip.change.suspicious@email.com", "phone": "+91-6543210987", "verification_status": "verified", "total_orders": 15, "account_age_days": 40 },
                "fraud_scenario": "ip_change_suspicious",
                "risk_score": 0.7,
                "sessions": [ { "session_id": "SESS_004_001", "start_time": "2025-07-11T12:00:00Z", "end_time": "2025-07-11T12:15:00Z", "duration_minutes": 15, "device_info": { "device_id": "DEV_SAMSUNG_002", "device_type": "mobile", "os": "Android", "os_version": "14.0", "app_version": "2.1.3", "device_model": "Samsung Galaxy S24" }, "network_info": { "ip_address": "10.10.10.1", "location": { "latitude": 34.0522, "longitude": -118.2437, "city": "Los Angeles", "country": "US" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-11T12:00:00Z", "details": { "login_method": "password", "success": "true" } }, { "event_type": "order_create", "timestamp": "2025-07-11T12:05:00Z", "details": { "order_id": "ORD_004_001", "package_type": "document", "pickup_address": "Hollywood Blvd, Los Angeles, US", "delivery_address": "Beverly Hills, Los Angeles, US", "declared_value": 100, "payment_method": "credit_card", "payment_id": "PAY_004_001" } } ] }, { "session_id": "SESS_004_002", "start_time": "2025-07-11T12:20:00Z", "end_time": "2025-07-11T12:30:00Z", "duration_minutes": 10, "device_info": { "device_id": "DEV_SAMSUNG_002", "device_type": "mobile", "os": "Android", "os_version": "14.0", "app_version": "2.1.3", "device_model": "Samsung Galaxy S24" }, "network_info": { "ip_address": "20.20.20.2", "location": { "latitude": 51.5074, "longitude": -0.1278, "city": "London", "country": "GB" } }, "events": [ { "event_type": "login", "timestamp": "2025-07-11T12:20:00Z", "details": { "login_method": "password", "success": "true" } }, { "event_type": "order_create", "timestamp": "2025-07-11T12:25:00Z", "details": { "order_id": "ORD_004_002", "package_type": "clothing", "pickup_address": "Oxford Street, London, GB", "delivery_address": "Regent Street, London, GB", "declared_value": 500, "payment_method": "credit_card", "payment_id": "PAY_004_002" } } ] } ]
              }
            ]
          }
        }

        with open(log_file_path, 'w') as f:
            json.dump(sample_logs_content, f, indent=2)
        print(f"Created dummy log file: {log_file_path}")

    log_file_path="sample_logs_v2.json"
    # User query to kick off the process
    # user_query = f"Please analyze the raw log data from '{log_file_path}' for distinct fraud patterns (referring to 'fraud_scenario' and associated data) and generate Rego policies in the exact JSON format for each unique fraud scenario. Make sure the Rego policies operate on a single 'user' object as input."
    user_query = f"Use the log_reader_tool to read the file located at 'file_path:{log_file_path}'. Then, analyze the raw log data for distinct fraud patterns (referring to 'fraud_scenario' and associated data) and generate Rego policies in the exact JSON format for each unique fraud scenario. Make sure the Rego policies operate on a single 'user' object as input."

    async for event in runner.run_async(session_id=session_id,user_id=user_id ,new_message=Content(parts=[Part.from_text(text=user_query)])):
        # if event.output and event.output.text:
        #     print(f"Agent Event: {event}")
        #     print(f"Agent Response: {event.output.text}")
        # elif event.tool_code_execution:
        #     print(f"Tool Code Executing: {event.tool_code_execution.tool_name}")
        #     print(f"Tool Args: {event.tool_code_execution.args}")
        # elif event.tool_code_result:
        #     try:
        #         result_val = json.loads(event.tool_code_result.value)
        #         print(f"Tool Result (JSON): {json.dumps(result_val, indent=2)}")
        #     except (json.JSONDecodeError, TypeError):
        #         print(f"Tool Result: {event.tool_code_result.value}")
        
        if event.is_final_response() and event.content and event.content.parts:
            # For output_schema, the content is the JSON string itself
            final_response_content = event.content.parts[0].text
            print(f"Final Agent Response: {final_response_content}")


if __name__ == "__main__":
    print("Starting Fraud Policy Generation Agent...")
    asyncio.run(main())