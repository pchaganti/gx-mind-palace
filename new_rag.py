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

@st.dialog("ask ai")
def rag(vectorstore):

    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    # Chat input persists
    if "user_query" not in st.session_state:
        st.session_state.user_query = ""

    user_query = st.chat_input("Chat input: ")
    
    if user_query:
        st.session_state.user_query = user_query
        st.session_state.messages.append(HumanMessage(user_query))

        with st.chat_message("user"):
            st.markdown(user_query)
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.8)

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(user_query)

        system_prompt = f"""You are an AI assistant tasked with answering questions based solely on the provided context.
        Your goal is to generate a comprehensive answer for the given question using the information available in the context.
        Context: {docs}"""

        st.session_state.messages.append(SystemMessage(system_prompt))

        result = llm.invoke(st.session_state.messages).content

        with st.chat_message("assistant"):
            st.markdown(result)
            st.session_state.messages.append(AIMessage(result))
