#import streamlit
import streamlit as st
import os
from dotenv import load_dotenv

# import pinecone
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter


# import langchain
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()
os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]

def create_embeddings(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_text(data)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # Load existing FAISS index if available
    vectorstore = FAISS.from_texts(text_chunks, embeddings)

    return vectorstore