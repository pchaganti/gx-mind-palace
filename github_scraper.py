import requests
import base64
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
EXCLUDED_FILE_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mp3", ".avi"}
HEADERS = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def fetch_repo_contents(baseurl, path=""):
    url = f"{baseurl}/{path}" if path else baseurl
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching {url}: {response.status_code}")
        st.cache_data.clear()
        return None

def get_file_content(file_url):
    """Fetches and decodes the content of a file from GitHub."""
    response = requests.get(file_url, headers=HEADERS)
    if response.status_code == 200:
        file_data = response.json()
        if file_data.get("content"):
            content = base64.b64decode(file_data["content"]).decode("utf-8", errors="ignore")
            return content
    else:
        st.error(f"Error fetching file content: {response.status_code}")
        st.cache_data.clear()
    return None

def get_repo_structure(baseurl, path="", indent_level=0):
    items = fetch_repo_contents(baseurl, path)
    structure = ""
    if items:
        for item in items:
            name = item["name"]
            file_extension = "." + name.split(".")[-1] if "." in name else ""
            indent = "    " * indent_level
            if item["type"] == "file":
                structure += f"{indent}- {name}\n"
            elif item["type"] == "dir":
                structure += f"{indent}- {name}/\n"
                structure += get_repo_structure(baseurl, item["path"], indent_level + 1)
    return structure

@st.cache_data(show_spinner=False)
def github_extractor(modified_url):
    owner, repo = modified_url[0], modified_url[1]
    baseurl = f"https://api.github.com/repos/{owner}/{repo}/contents"
    text = "\n================================================\nRepository Structure:\n================================================\n"
    repo_structure = get_repo_structure(baseurl)
    text+=str(repo_structure)
    all_files = fetch_repo_contents(baseurl)
    if all_files:
        for item in all_files:
            if item["type"] == "file":
                file_extension = "." + item["name"].split(".")[-1] if "." in item["name"] else ""
                if file_extension not in EXCLUDED_FILE_TYPES:
                    content = get_file_content(item["url"])
                    text+=f"\n================================================\nFile:{str(item["name"])}\n================================================\n"
                    text+=str(content)
    return text