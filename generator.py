import streamlit as st
import json
import string
from sanitizer import sanitize_text
import time
from relationship_generator import extract_relationships
import streamlit_mermaid as stmd
import requests

def get_node_label(index):
    """Generate a label like A, B, ..., Z, AA, AB, etc."""
    letters = string.ascii_uppercase
    label = ""
    while index >= 0:
        label = letters[index % 26] + label
        index = index // 26 - 1
    return label

def generate_mermaid_code(relationships_json):
    relationships = relationships_json["relationships"]
    mermaid_code = """%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#e66b22',
      'primaryTextColor': '#efefef',
      'primaryBorderColor': '#d9d9d9',
      'lineColor': '#8d8d8d',
      'secondaryColor': '#212121',
      'tertiaryColor': '#fff'
    }
  }
}%%\nflowchart LR;\n"""
    
    nodes = {}
    node_counter = 0  # Start from 0 and increment

    for relation in relationships:
        from_topic = sanitize_text(relation["from"])
        to_topic = sanitize_text(relation["to"])
        relation_text = sanitize_text(relation["relationship"])

        if from_topic not in nodes:
            nodes[from_topic] = get_node_label(node_counter)
            node_counter += 1
        if to_topic not in nodes:
            nodes[to_topic] = get_node_label(node_counter)
            node_counter += 1

        mermaid_code += f'  {nodes[from_topic]}["{from_topic}"] -->|{relation_text}| {nodes[to_topic]}["{to_topic}"];'
    mermaid_code += """
    classDef customStyle stroke:#e66b22,stroke-width:2px,rx:10px,ry:10px;
    """
    for node in nodes.values():
        mermaid_code += f'  class {node} customStyle;\n'
        mermaid_code += f'  style {node} font-size:20px;\n'
    return mermaid_code

def generate_mermaid_code_pipeline(relationships_json):
    relationships = relationships_json["relationships"]
    mermaid_code = """%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#e66b22',
      'primaryTextColor': '#efefef',
      'primaryBorderColor': '#d9d9d9',
      'lineColor': '#8d8d8d',
      'secondaryColor': '#212121',
      'tertiaryColor': '#fff'
    }
  }
}%%\nflowchart TD;\n"""
    
    nodes = {}
    node_counter = 0  # Start from 0 and increment

    for relation in relationships:
        from_topic = sanitize_text(relation["from"])
        to_topic = sanitize_text(relation["to"])
        relation_text = sanitize_text(relation["relationship"])

        if from_topic not in nodes:
            nodes[from_topic] = get_node_label(node_counter)
            node_counter += 1
        if to_topic not in nodes:
            nodes[to_topic] = get_node_label(node_counter)
            node_counter += 1

        mermaid_code += f'  {nodes[from_topic]}["{from_topic}"] -->|{relation_text}| {nodes[to_topic]}["{to_topic}"];'
    mermaid_code += """
    classDef customStyle stroke:#e66b22,stroke-width:2px,rx:10px,ry:10px;
    """
    for node in nodes.values():
        mermaid_code += f'  class {node} customStyle;\n'
        mermaid_code += f'  style {node} font-size:20px;\n'
    return mermaid_code

def generate_mermaid_code_final(relationships_json):
    # Handle both string and dict input
    if isinstance(relationships_json, str):
        try:
            relationships = json.loads(relationships_json)["relationships"]
        except json.JSONDecodeError:
            st.error("Invalid JSON format in relationships")
            st.cache_data.clear()
            return None
    else:
        relationships = relationships_json["relationships"]    
    mermaid_code = """%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#e66b22',
      'primaryTextColor': '#efefef',
      'primaryBorderColor': '#d9d9d9',
      'lineColor': '#8d8d8d',
      'secondaryColor': '#212121',
      'tertiaryColor': '#fff'
    }
  }
}%%\nflowchart TD;\n"""

    # Extract all unique nodes and assign letters
    unique_nodes = {}
    letters = string.ascii_uppercase
    node_index = 0

    for relation in relationships:
        for node in [relation["from"], relation["to"]]:
            if node not in unique_nodes:
                unique_nodes[node] = letters[node_index]
                node_index += 1
                if node_index >= len(letters):  # Prevent index out of range
                    node_index = 0 

    # Define nodes
    for node, letter in unique_nodes.items():
        mermaid_code += f'  {letter}["{node}"];\n'

    # Define relationships
    for relation in relationships:
        from_letter = unique_nodes[relation["from"]]
        to_letter = unique_nodes[relation["to"]]
        relation_text = relation["relationship"]
        mermaid_code += f'  {from_letter} -->|{relation_text}| {to_letter};\n'

    mermaid_code += "\nclassDef customStyle stroke:#e66b22,stroke-width:2px,rx:10px,ry:10px,font-size:16px;\n"
    for letter in unique_nodes.values():
        mermaid_code += f'  class {letter} customStyle;\n'
    return mermaid_code

def mermaid_to_png(mermaid_code: str):
    url = "https://kroki.io/mermaid/png"
    headers = {"Content-Type": "text/plain"}
    
    response = requests.post(url, data=mermaid_code.encode('utf-8'), headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        return none

def generate(topic_data):
    # Handle both string and dict input
    if isinstance(topic_data, str):
        try:
            topic_data = json.loads(topic_data)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in topic data")
            st.cache_data.clear()
            st.stop()
    if topic_data is None:
        st.error("Failed to summarize topics.")
        st.cache_data.clear()
        st.stop()
    i=0
    if topic_data:
        # col1, col2 = st.columns([0.55,0.45])
        st.write("#### topics and summaries")
        # st.write("### 🧠 Mind Maps")
        for topic in topic_data["topics"]:
            topic_name = topic["topic"]
            summary = topic["summary"]
            st.write(f"##### 📌 {topic_name}")
            st.write(f"{summary}")

            with st.spinner(text="generating mindmap", show_time=False):
                relationships = extract_relationships(summary)

                if relationships:
                    time.sleep(1)
                    if topic_name=="Pipeline":
                        mermaid_code=generate_mermaid_code_pipeline(relationships)
                    else:
                        mermaid_code=generate_mermaid_code(relationships)
                    image=mermaid_to_png(mermaid_code)
                    stmd.st_mermaid(mermaid_code)
            st.download_button(label="save as image", data=image,file_name="mindpalace_diagram.png", mime="image/png", key=i) # for saving image
            st.divider()
            i+=1
    else:
        st.error("No topics detected.")
        st.cache_data.clear()