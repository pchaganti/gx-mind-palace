import streamlit as st
from github_scraper import github_extractor
from generator import generate
from segmentor_summarizer import ss_pdf_text, ss_repo_text
from pdf_ocr import extract_from_mistral
from new_rag import create_embeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import base64

def reset_state():
    st.session_state.content_generated = False
    st.session_state.extracted_text = None
    st.session_state.topic_data = None
    st.session_state.vectorstore = None
    st.session_state.messages = [SystemMessage("You are an assistant for question-answering tasks.")]
    st.session_state.mindmap_generated = False

# Initialize session state variables
if "init" not in st.session_state:
    st.session_state.init = True
    reset_state()

def process_github():
    if st.session_state.github_url:
        modified_url = st.session_state.github_url.replace("https://github.com/", "").strip('/').split('/')
        if len(modified_url) >= 2:
            with st.spinner(text="fetching repository contents", show_time=False):
                text = github_extractor(modified_url)
                st.session_state.extracted_text = text
                st.session_state.content_generated = True
                return True
        elif st.session_state.github_url=="":
            st.error("invalid github repository url. please enter a valid url.")
        else:
            st.error("invalid github repository url. please enter a valid url.")
    return False

def process_pdf():
    if st.session_state.pdf:
        with st.spinner(text="fetching pdf contents", show_time=False):
            text = extract_from_mistral(st.session_state.pdf)
            if text.strip():
                st.session_state.extracted_text = text
                st.session_state.content_generated = True
                return True
            else:
                st.error("No text could be extracted from the PDF.")
    else:
        st.error("invalid pdf. please enter a valid pdf.")
    return False

def on_generate():
    st.session_state.content_generated = False
    st.session_state.extracted_text = None
    st.session_state.vectorstore = None
    st.session_state.messages = [SystemMessage("You are an assistant for question-answering tasks.")]  # Reset chat messages
    st.session_state.mindmap_generated = False  # Reset mindmap generation flag
    
    if os.path.exists("faiss_index"):
        import shutil
        shutil.rmtree("faiss_index")
    
    
    if st.session_state.input_option == "github repository":
        process_github()
        with st.spinner("analysing repository"):
            st.session_state.topic_data = ss_repo_text(st.session_state.extracted_text)
    elif st.session_state.input_option == "pdf document":
        process_pdf()
        with st.spinner("analysing pdf"):
            st.session_state.topic_data = ss_pdf_text(st.session_state.extracted_text)

# Main UI
st.set_page_config(page_title="mindpalace", page_icon="logo_mp.png", layout="wide")
st.header('mindpalace')

input_option=st.radio("select input source", ("github repository", "pdf document"), key="input_option")

if "previous_input_option" not in st.session_state:
    st.session_state.previous_input_option = None

if st.session_state.previous_input_option != input_option:
    reset_state()
    st.session_state.previous_input_option = input_option

if st.session_state.input_option == "github repository":
    st.text_input("enter gitHub repository url", key="github_url")
else:
    st.file_uploader("upload your pdf", type="pdf", key="pdf")

button=st.button("generate mindpalace", type="primary")
if button:
    on_generate()
st.divider()

# Display content and generate diagrams
if st.session_state.content_generated:
    if st.session_state.input_option == "github repository":
        st.write("#### contents")
        with st.expander("# repository contents"):
            st.code(st.session_state.extracted_text)
    elif st.session_state.input_option == "pdf document":
        st.write("#### contents")
        with st.expander("# extracted text"):
            st.markdown(st.session_state.extracted_text)
    
    # tabs for mindmap and chat
    if st.session_state.topic_data:
        tab_selection = st.radio("Select View", ["mindpalace", "ask ai"], 
                               horizontal=True, 
                               key="tab_selection")
        
        if tab_selection == "ask ai":
            # Initialize vectorstore if needed
            with st.spinner(text="preparing ai system...", show_time=False):
                st.session_state.vectorstore = create_embeddings(st.session_state.extracted_text)
            
            chat_container = st.container(height=475)
            
            if prompt := st.chat_input("ask a question"):
                st.session_state.messages.append(HumanMessage(prompt))
                
                # Get response from RAG
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 8})
                docs = retriever.invoke(prompt)
                
                system_prompt = f"""You are an AI assistant tasked with answering questions based on the provided context.
                Your goal is to generate a **detailed** answer for the given question taking reference from the information available in the context. The answer should be very detailed, giving the most relevant answer to the user's question.
                
                Context: {docs}"""
                
                st.session_state.messages.append(SystemMessage(system_prompt))

            with chat_container:
                for message in st.session_state.messages:
                    if isinstance(message, HumanMessage):
                        with st.chat_message("user"):
                            st.markdown(message.content)
                    elif isinstance(message, AIMessage):
                        with st.chat_message("assistant"):
                            st.markdown(message.content)
                
                if prompt:
                    with st.chat_message("assistant"):
                        with st.spinner("thinking..."):
                            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8)
                            result = llm.invoke(st.session_state.messages).content
                            st.markdown(result)
                            st.session_state.messages.append(AIMessage(result))
        else:
            generate(st.session_state.topic_data)
            st.session_state.mindmap_generated = True