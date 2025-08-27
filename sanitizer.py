import re
import json
import streamlit as st

def sanitize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s\-\>\:\.\*\=\-\^\+\,\<\>\?\%\\]', '', text)  # remove symbols except `->`, `:`, '.'

def extract_json(text):
    """Extracts valid JSON from AI response, sanitizing invalid characters."""
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        
        # Fix common JSON issues
        json_str = re.sub(r",\s*}", "}", json_str)  # Remove trailing commas before closing brace
        json_str = re.sub(r",\s*\]", "]", json_str)  # Remove trailing commas before closing bracket
        json_str = re.sub(r"}\s*{", "},{", json_str)  # Fix missing commas between objects
        json_str = re.sub(r'(?<!\\)"(?=(,|\s*[}\]])|$)', '\\"', json_str)  # Escape unescaped quotes
        json_str = re.sub(r'\\+"', '\\"', json_str)  # Fix multiple backslashes
        json_str = re.sub(r'(?<!\\)"([^"]*?)(?<!\\)"', r'"\1"', json_str)  # Fix unescaped quotes in strings
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            st.error(f"JSON Error: {e}")
            st.error(f"Invalid JSON Received:\n{json_str}")
            st.cache_data.clear()
            return None
    return None

def extract_json_1(text):
    """Extracts valid json from response, sanitizing invalid characters."""
    if not text:
        return None    
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)

        # Fix common JSON issues
        json_str = re.sub(r",\s*}", "}", json_str)  # Remove trailing commas before closing brace
        json_str = re.sub(r",\s*\]", "]", json_str)  # Remove trailing commas before closing bracket
        json_str = re.sub(r"}\s*{", "},{", json_str)  # Fix missing commas between objects
        json_str = re.sub(r'(?<!\\)"(?=(,|\s*[}\]])|$)', '\\"', json_str)  # Escape unescaped quotes
        json_str = re.sub(r'\\+"', '\\"', json_str)  # Fix multiple backslashes
        json_str = re.sub(r'(?<!\\)"([^"]*?)(?<!\\)"', r'"\1"', json_str)  # Fix unescaped quotes in strings
        
        try:
            data = json.loads(json_str)  

            if "topics" in data and isinstance(data["topics"], list):
                for topic in data["topics"]:
                    if "content" in topic and isinstance(topic["content"], str):
                        topic["content"] = topic["content"].replace("'", "").replace('"', "")

            return data  

        except json.JSONDecodeError as e:
            st.write(f"JSON Error 1: {e}")
            st.write(f"Invalid JSON Received:\n{json_str}")
            st.cache_data.clear()
            return None  
    return None