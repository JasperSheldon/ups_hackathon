# tools.py
import json
from typing import List, Dict, Any
# from google.adk.tools import tool # <--- Import the tool decorator


async def log_reader_tool(file_path: str) -> List[Dict]: # Renamed to lowercase per Python conventions, removed 'self'
    """
    Reads a JSON file from the specified path and returns its content.
    """
    file_path="D:/Projects/ups_hackathon/agent1/sample_logs_v2.json"
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Ensure safe access to nested keys
            return data.get("fraud_detection_logs", {}).get("users", [])
    except FileNotFoundError:
        # Return a structured error that the LLM can interpret
        return {"error": f"File not found: {file_path}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in file: {file_path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}