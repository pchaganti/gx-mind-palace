import re
import json
import streamlit as st

def sanitize_text(text):
    """Remove special characters Mermaid does not support."""
    return re.sub(r'[^a-zA-Z0-9\s\-\>\:\.]', '', text)  # Remove symbols except `->`, `:`, '.'

def extract_json(text):
    """Extracts valid JSON from AI response, sanitizing invalid characters."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        
        # Fix common JSON issues (e.g., trailing commas)
        json_str = re.sub(r",\s*}", "}", json_str)  # Remove trailing commas before closing brace
        json_str = re.sub(r",\s*\]", "]", json_str)  # Remove trailing commas before closing bracket
        
        try:
            return json.loads(json_str)  # Convert to JSON
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            print(f"Invalid JSON Received:\n{json_str}")
            st.cache_data.clear
            return None  # Return None if JSON is invalid
    return None

def extract_json_1(text):
    """Extracts valid JSON from AI response, sanitizing invalid characters."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)

        # Fix common JSON issues (e.g., trailing commas)
        json_str = re.sub(r",\s*}", "}", json_str)  # Remove trailing commas before closing brace
        json_str = re.sub(r",\s*\]", "]", json_str)  # Remove trailing commas before closing bracket
        
        # Fix invalid escape sequences
        json_str = json_str.replace("\\", "\\\\")  # Double escape backslashes to make them valid in JSON
        
        try:
            data = json.loads(json_str)  # Convert to JSON dictionary

            # Check if "topics" exists and is a list
            if "topics" in data and isinstance(data["topics"], list):
                for topic in data["topics"]:
                    # Ensure topic has "content" key and it's a string
                    if "content" in topic and isinstance(topic["content"], str):
                        topic["content"] = topic["content"].replace("'", "").replace('"', "")

            return data  # Return the modified JSON object

        except json.JSONDecodeError as e:
            st.write(f"JSON Error: {e}")
            st.write(f"Invalid JSON Received:\n{json_str}")
            st.cache_data.clear
            return None  # Return None if JSON is invalid
    return None