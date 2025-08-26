import google.generativeai as genai
from sanitizer import extract_json
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
gemini_api_key=st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=gemini_api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
    "response_schema": {
  "type": "object",
  "properties": {
    "topics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "topic": {
            "type": "string"
          },
          "summary": {
            "type": "string"
          }
        },
        "required": [
          "topic",
          "summary"
        ]
      }
    }
  },
  "required": [
    "topics"
  ]
}
}

# def extract_relationships(topic_text):
#     model = genai.GenerativeModel(
#         model_name="gemini-2.0-flash",
#         generation_config=generation_config,
#         system_instruction=f"""
#         Identify relationships between the given topics and subtopics.

#         **Rules:**
#         - Use **short, precise** relationship descriptions.
#         - Organize topics into subcategories.
#         - Identify main topics, then branch further. For e.g. Topic then subtopics then further subtopics.
#         - Group related topics under **subcategories** (e.g., "AI in Healthcare" under "AI Applications").
#         - Relationships should not be **too obvious** (avoid generic links).
#         - Ensure **a natural progression** from general → specific.
#         - Do cover all important points.
#         - Do not use brackets anywhere
#         - **Return JSON format only.**
#         - No extra text before or after JSON.

#         **Example Output:**
#         {{
#             "relationships": [
#                 {{"from": "AI in Medicine", "to": "Machine Learning", "relationship": "Uses ML models"}},
#                 {{"from": "Fraud Detection", "to": "AI in Finance", "relationship": "Prevents financial crimes"}}
#             ]
#         }}
#         """,
#     )
#     response = model.start_chat().send_message(topic_text)
#     return extract_json(response.text)

@st.cache_data(show_spinner=False)
def extract_relationships(topic_text):
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction="""
        Identify **logical relationships** between topics and structure them **hierarchically** for a mind map.

        **Rules:**
        - Organize topics into **main topics → subtopics → deeper breakdowns**.
        - Clearly define **why** one topic relates to another (not just that it does).
        - **Group related concepts** under larger umbrella topics.
        - Ensure **a natural progression** from general → specific.
        - Do cover all important points.
        - Relationships should not be **too obvious** (avoid generic links).
        - Ensure a good level of interconnection between topics.
        - Ensure **completeness**—cover all key topics.
        - **Strictly return JSON format only.**

        **Example Output:**
        {
            "relationships": [
                {"from": "Deep Learning", "to": "Neural Networks", "relationship": "Built upon"},
                {"from": "Convolutional Neural Networks", "to": "Image Processing", "relationship": "Used for"}
            ]
        }
        """,
    )
    response = model.start_chat().send_message(topic_text)
    return extract_json(response.text)
