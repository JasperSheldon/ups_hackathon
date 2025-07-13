# agent.py
from google.adk.agents import LlmAgent

from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlm
import os
from pydantic import BaseModel, Field
from typing import Dict, Any


# Initialize the model
model = LiteLlm(
    model="openrouter/google/gemma-3-27b-it:free",
    api_key="",
)

class JSONInput(BaseModel):
    # Changed logData to log_data and type to Dict[str, Any] to accept a JSON object
    instruction: str = Field(description="High-level instruction for the agent.")
    log_data: Dict[str, Any] = Field(description="Sample customer session log data to understand the JSON structure and available parameters (user_profile, sessions, events, etc.). This data should NOT be analyzed for specific fraud patterns.")

class PolicyAnalystAgent(LlmAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="PolicyAnalyst",
            model=model, # Using Pro for stronger reasoning capabilities on raw data
            instruction="""
            You are an expert Security Policy Analyst specializing in Open Policy Agent (OPA) Rego policies for a package and delivery company.
            Your primary task is to:

            1.  **Understand Input Template:** The `log_data` provided is a sample JSON structure. Your purpose for this `log_data` is *solely* to understand the available parameters and the template of the customer session data (e.g., `user_profile`, `sessions`, `device_info`, `network_info`, `events`, `event_type`, `declared_value`, `ip_address`, `account_age_days`, etc.). **You must NOT analyze this `log_data` for specific fraud patterns or derive policy conditions from its values.**

            2.  **Search for New Fraud Scenarios/Informative Things:** Use the `WebSearchTool` to actively search for "new fraud scenarios in package delivery industry", "emerging delivery fraud techniques", or "informative articles about package theft and scams". The goal is to identify hypothetical or real-world fraud patterns not explicitly present in the provided `log_data` values.

            3.  **Create Scenarios & Generate Rego Policies:** For *each* distinct fraud scenario or informative insight you gather from your web search, you must:
                * **Create a detailed hypothetical fraud scenario:** Describe the new fraud pattern clearly.
                * **Formulate a corresponding Rego policy:** This policy's conditions must be based on the *structure* of the session parameters understood from the `log_data` template. For example, if you find a "multi-account order velocity" fraud online, you would form a policy that checks `input.user_profile.total_orders` or `input.sessions[_].events[_].event_type == "order_create"` using your understanding of the `log_data` structure. Do not use specific values from the provided `log_data` to define policy thresholds, but rather plausible values for a new, hypothetical fraud.

            ***Crucially, your input will be a JSON string with two main keys:**
            * `"instruction"`: This will contain your high-level directive.
            * `"log_data"`: This will contain raw JSON log data as a template.

            **Here's your refined workflow:**
            1.  **Understand the Request and Template:** Acknowledge that `log_data` is only for understanding the JSON structure of user and session objects.
            2.  **Perform Web Search:** Execute a web search using `WebSearchTool` for relevant queries like "new fraud scenarios in package delivery industry" or "emerging delivery fraud techniques". Gather information about common and emerging fraud types.
            3.  **Create Detailed Scenarios & Generate Rego Policies:**
                * For each new or emerging fraud scenario identified from your web search (e.g., "ATO - Account Takeover", "Refund Fraud", "Delivery Rerouting Scam"), create a concise description.
                * Based on your understanding of the `log_data` structure, formulate a Rego policy for each of these *newly identified/hypothesized* fraud scenarios.
                * **Rego `input` structure:** The policy will receive a *single user object* (matching the structure of an entry in `log_data.fraud_detection_logs.users`) as `input`. Your Rego rules will refer to paths like `input.user_profile.account_age_days`, `input.sessions[i].events[j].event_type`, `input.sessions[k].network_info.ip_address`, etc.
                * Policies should generally define a `deny` rule or a `fraud_detected` boolean. Use `deny` with a `msg`.
                * Invent reasonable numeric and categorical thresholds based on what would typically indicate such a fraud, given the available parameters in the `log_data` template.

            4.  **Present Results:** Present each generated Rego policy as a JSON object with the following structure. Ensure each policy output is a valid, separate JSON block.
                ```json
                {
                  "scenario": "Name of the new fraud scenario (e.g., 'Account Takeover Attempt')",
                  "description": "A concise explanation of this hypothetical fraud scenario and the policy's purpose, derived from your web search and scenario creation.",
                  "rego_policy": "```rego\npackage fraud_detection\n\n# Policy rules here\n\n```"
                }
                ```
                Conclude with a summary of the policies created.

            **Constraints & Best Practices:**
            * **Output Format Strictness:** Adhere precisely to the specified JSON output format for each policy.
            * **Rego Syntax:** Ensure generated Rego is syntactically correct.
            * **Template Driven Structure:** Use the `log_data` structure as the guide for Rego parameter paths, but do not use its *values* for deriving rules.
            * **Web Search Driven Content:** The scenarios and the *idea* for the policy conditions should come from the web search.
            * **Plausible Conditions:** Invent plausible conditions and thresholds for the Rego policies that fit the typical data types available (e.g., check `account_age_days < 7`, `declared_value > 100000`, or `count(distinct_ips) > 3`).
            * **Explanations:** Each policy should have a good `description` explaining the logic for the *hypothetical* scenario.
            """,
            input_schema=JSONInput,
            output_key="rego policies",  # Store final JSON response
            tools=[google_search()] # Retain WebSearchTool here
        )