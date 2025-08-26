import google.generativeai as genai
import streamlit as st
from sanitizer import extract_json_1, extract_json
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key=st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=gemini_api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

# def ss_repo_text(text):
#     model = genai.GenerativeModel(
#         model_name="gemini-2.0-flash",
#         generation_config=generation_config,
#         system_instruction = f"""
#         Extract **file-based topics** from the given text, ensuring each topic is a **file name** from the GitHub repository.

#         **Rules:**
#         - Each topic must be **a file name** (e.g., `app.py`, `config.toml`).
#         - Segregate the contents on the basis of the files present in the given github repo.
#         - Include **one topic** for repository structure and **one for the pipeline or flow**.
#         - Ignore `.gitignore`, `CONTRIBUTING`, and `LICENSE` files.
#         - Cover as many relevant files as possible.
#         - Provide a **detailed summary (5-7 sentences)** for each file. Cover **all important files**.
#         - The summary should describe **the file's role, functionality, flow, working, dependencies (if applicable), and interactions** within the repository.
#         - **Strictly return JSON format only.**
        
#         **Example Output:**
#         {{
#             "topics": [
#                 {{"topic": "app.py", "summary": "This file serves as the main entry point for the application, handling user interactions and backend logic using Streamlit."}},
#                 {{"topic": "fraud_detection.py", "summary": "Implements machine learning models for fraud detection, leveraging libraries such as scikit-learn and pandas for data analysis."}}
#             ]
#         }}
#         """,
#     )
#     response = model.start_chat().send_message(text)
#     return extract_json_1(response.text)

@st.cache_data(show_spinner=False)
def ss_repo_text(text):
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction="""
        Extract **all relevant files** from the GitHub repository and generate a **detailed, structured summary**.

        **Rules:**
        - Identify **all important files** (code files, config files, documentation, assets, workflows).
        - **Group files** into categories (e.g., Backend, Frontend, Configurations, Testing, Documentation).
        - **Ignore unnecessary** files like `.gitignore`, `LICENSE`, `.DS_Store`, `CONTRIBUTING`
        - For each file, provide:
          1. **File Purpose** - Explain what the file does and its significance in the repository.
          2. **Key Functions & Classes** - List all major functions, methods, and classes with descriptions.
          3. **Dependencies** - Mention which other files or external libraries it interacts with.
          4. **Execution Flow** - Describe how this file contributes to the overall project.
          5. **Important Configurations or Constants** (if applicable).
          6. **Data Handling** (if applicable) - How the file processes or transforms data.
        - Ensure summaries are **very detailed (8-12 sentences per file)**.
        - Include **one topic for repository structure named 'Repository Structure'** and **one for the pipeline or flow named 'Pipeline'**.
        - **Strictly return JSON format only.**
        - **Return a single, properly formatted JSON object.**
        - Ensure all quotes are properly escaped.
        - Avoid using newlines within text fields.

        **Example Output:**
        {
            "topics": [
                {
                    "topic": "main.py",
                    "summary": "This file serves as the primary entry point of the application. It initializes the main execution loop, loads configuration settings from `config.yaml`, and manages API requests. It calls helper functions from `utils.py` and `database.py` for data handling. The main function defines the initialization of UI components and calls `model.py` for inference if needed."
                },
                {
                    "topic": "config.yaml",
                    "summary": "Stores all environment configurations, model hyperparameters, and API keys. This file is used across multiple scripts to ensure a standardized setup."
                }
            ]
        }
        """,
    )
    response = model.start_chat().send_message(text)
    return extract_json(response.text)

@st.cache_data(show_spinner=False)
def ss_pdf_text(text):
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction="""
        Extract **all key topics** from the given PDF and generate **detailed summaries**.

        **Rules:**
        - Identify and list **all major topics and subtopics**.
        - Summarize each topic in **8-12 sentences**.
        - Ensure that no important topic is omitted.
        - Avoid generic summaries—**provide technical depth and clarity**.
        - **Strictly return JSON format only.**

        **Example Output:**
        {
            "topics": [
                {
                    "topic": "Deep Learning",
                    "summary": "Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers to learn representations of data. It is widely used in computer vision, natural language processing, and autonomous systems. Popular architectures include CNNs (for image processing), RNNs (for sequential data), and Transformers (for NLP tasks). Challenges include large data requirements and computational costs."
                },
                {
                    "topic": "Gradient Descent",
                    "summary": "Gradient descent is an optimization algorithm used to minimize the loss function in machine learning models. It updates model parameters iteratively by computing gradients. Variants include Stochastic Gradient Descent (SGD), Mini-Batch Gradient Descent, and Adam Optimizer."
                }
            ]
        }
        """,
    )
    response = model.start_chat().send_message(text)
    return extract_json(response.text)
