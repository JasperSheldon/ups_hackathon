# agent.py
from google.adk.agents import LlmAgent
from google.genai.types import HarmCategory, HarmBlockThreshold, SafetySetting
from tools import log_reader_tool # Only LogReaderTool is needed now
from google.adk.models.lite_llm import LiteLlm
import os
from pydantic import BaseModel, Field
from typing import Dict, Any


# Initialize the model
model = LiteLlm(
    model="openrouter/google/gemma-3-27b-it:free",
    api_key="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",
)

class JSONInput(BaseModel):
    # Changed logData to log_data and type to Dict[str, Any] to accept a JSON object
    instruction: str = Field(description="High-level instruction for the agent.")
    log_data: Dict[str, Any] = Field(description="Raw customer session log data to be analyzed.")

class PolicyAnalystAgent(LlmAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="PolicyAnalyst",
            model=model, # Using Pro for stronger reasoning capabilities on raw data
            instruction="""
            You are an expert Security Policy Analyst specializing in Open Policy Agent (OPA) Rego policies.
            Your primary task is to deeply analyze raw customer session log data, identify distinct fraud patterns
            by examining the 'fraud_scenario' and associated session/user profile details, and then generate
            Rego policies for each identified fraud scenario.


            ***Crucially, your input will be a JSON string with two main keys:**
            * `"instruction"`: This will contain your high-level directive (e.g., "analyze logs and generate Rego policies").
            * `"log_data"`: This will contain the raw JSON log data itself, specifically the `fraud_detection_logs` object. This `log_data` will be a parsed JSON object (Python dictionary), not a string.

            **Here's your refined workflow:**
            1.  **Understand the Request:** The user will provide a path to a JSON log file.
            2.  **Read Logs:** Use the `log_reader_tool` to load the JSON log data. This tool will provide a raw list of user objects, each containing their 'user_profile', 'sessions', and 'fraud_scenario'.
            3.  **Perform Deep Analysis & Pattern Identification (Your Core Task):**
                * Iterate through the provided list of user entries.
                * For each user, identify their `fraud_scenario`.
                * **Crucially, for each unique `fraud_scenario` (excluding "normal_behavior"), examine the associated 'user_profile' and 'sessions' data (including 'device_info', 'network_info', and 'events' within sessions) to infer the specific conditions that define that fraud pattern.**
                * **Examples of patterns to look for:**
                    * **Velocity Fraud:** How many "order_create" events occur in a short time within a session, especially for a user's total orders or account age? What are the declared values?
                    * **New User High Value Order:** Is the `account_age_days` very low (e.g., 0 or 1)? Is `verification_status` "unverified"? Is there a single, unusually high `declared_value` order in their initial session(s)?
                    * **IP Change Suspicious:** Are there multiple distinct `ip_address` values across different sessions for the same user, especially if these changes occur rapidly or are geographically disparate (infer from city/country)?
                * Identify concrete thresholds and conditions from the data.
            4.  **Generate Rego Policies:** For each distinct fraud scenario you identify (based on `fraud_scenario` field), generate a corresponding Rego policy.
                * The output for each policy **must be a JSON object** with the following structure:
                    ```json
                    {
                      "scenario": "Name of the fraud scenario (e.g., 'Velocity Fraud')",
                      "description": "A concise explanation of this fraud scenario and the policy's purpose, derived from your analysis of the patterns.",
                      "rego_policy": "```rego\npackage fraud_detection\n\n# Policy rules here\n\n```"
                    }
                    ```
                * The `rego_policy` field should contain the *actual Rego code* inside a markdown code block (triple backticks).
                * **Rego `input` structure:** The policy will receive a *single user object* (from the log file) as `input`. This means your Rego rules will refer to paths like `input.user_profile.account_age_days`, `input.sessions[i].events[j].event_type`, `input.sessions[k].network_info.ip_address`, etc.
                * For rules that need to check events or sessions, use Rego's `some` keyword for iteration (e.g., `some i, session in input.sessions`).
                * Policies should generally define a `deny` rule or a `fraud_detected` boolean. For this exercise, use `deny` with a `msg`.
                * Infer reasonable numeric and categorical thresholds directly from the provided sample data.
            5.  **Present Results:** Present each generated Rego policy JSON object, along with a concluding summary of the policies created. Ensure each policy output is a valid, separate JSON block.

            **Constraints & Best Practices:**
            * **Output Format Strictness:** Adhere precisely to the specified JSON output format for each policy.
            * **Rego Syntax:** Ensure generated Rego is syntactically correct.
            * **Data Driven:** Base your policy conditions strictly on patterns observable in the provided log data. Do not invent rules that aren't supported by the sample.
            * **Time-Based Logic (in Rego):** If a pattern is time-sensitive (e.g., velocity), aim to incorporate `time.parse_rfc3339()` and `time.diff()` if possible within Rego, or simplify if necessary by relying on pre-calculated fields like `account_age_days`. Given the current structure, direct `time.diff` on event timestamps is harder for the LLM to write perfectly, so focus on `account_age_days` and general counts/values, but acknowledge the need for time-based logic where relevant.
            * **Explanations:** Each policy should have a good `description` explaining the logic.
            """,
            input_schema=JSONInput,
            output_key="rego policies",  # Store final JSON response
        )
        