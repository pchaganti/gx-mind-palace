import re
import json
import streamlit as st

def sanitize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s\-\>\:\.\*\=\-\^\\]', '', text)  # remove symbols except `->`, `:`, '.'

def extract_json(text):
    """Extracts valid json from response, sanitizing invalid characters."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        

        json_str = re.sub(r",\s*}", "}", json_str)  
        json_str = re.sub(r",\s*\]", "]", json_str)  
        
        try:
            return json.loads(json_str)  
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            print(f"Invalid JSON Received:\n{json_str}")
            st.cache_data.clear
            return None  
    return None

def extract_json_1(text):
    """Extracts valid json from response, sanitizing invalid characters."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)

        json_str = re.sub(r",\s*}", "}", json_str)  
        json_str = re.sub(r",\s*\]", "]", json_str)  
        
        json_str = json_str.replace("\\", "\\\\")  
        
        try:
            data = json.loads(json_str)  

            if "topics" in data and isinstance(data["topics"], list):
                for topic in data["topics"]:
                    if "content" in topic and isinstance(topic["content"], str):
                        topic["content"] = topic["content"].replace("'", "").replace('"', "")

            return data  

        except json.JSONDecodeError as e:
            st.write(f"JSON Error: {e}")
            st.write(f"Invalid JSON Received:\n{json_str}")
            st.cache_data.clear
            return None  
    return None