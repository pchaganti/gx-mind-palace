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
# st.logo("logo_mp.png", size='large')
# st.header('mindpalace')
LOGO_IMAGE = "logo_mp.png"

st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        font-weight:625 !important;
        font-size:35px !important;
        color: #ffffff !important;
        padding-top: 0px !important;
    }
    .logo-img {
        float:right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
        <p class="logo-text">mindpalace</p>
    </div>
    """,
    unsafe_allow_html=True
)
# col1, col3, col2=st.columns([1,0.1,7])
# with col1:
#     st.image("logo_mp_2.png",)
# with col2:
#     st.write('## mindpalace')

# Input selection and collection
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
    # Display content
    if st.session_state.input_option == "github repository":
        st.write("#### contents")
        with st.expander("# repository contents"):
            st.code(st.session_state.extracted_text)
    elif st.session_state.input_option == "pdf document":
        st.write("#### contents")
        with st.expander("# extracted text"):
            st.write(st.session_state.extracted_text)
    
    # Create tabs for mindmap and chat
    if st.session_state.topic_data:
        # Add tab selector
        tab_selection = st.radio("Select View", ["mindpalace", "ask ai"], 
                               horizontal=True, 
                               key="tab_selection")
        
        # Show content based on selected tab
        if tab_selection == "ask ai":
            # Initialize vectorstore if needed
            with st.spinner(text="preparing ai system...", show_time=False):
                st.session_state.vectorstore = create_embeddings(st.session_state.extracted_text)
            
            # Create a container with fixed height for chat messages
            chat_container = st.container(height=475)
            
            # Chat input before container
            if prompt := st.chat_input("ask a question"):
                st.session_state.messages.append(HumanMessage(prompt))
                
                # Get response from RAG
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 8})
                docs = retriever.invoke(prompt)
                
                system_prompt = f"""You are an AI assistant tasked with answering questions based on the provided context.
                Your goal is to generate a **comprehensive and detailed answer** for the given question using the information available in the context.
                Context: {docs}"""
                
                st.session_state.messages.append(SystemMessage(system_prompt))

            # Display all messages in container, including new ones
            with chat_container:
                for message in st.session_state.messages:
                    if isinstance(message, HumanMessage):
                        with st.chat_message("user"):
                            st.markdown(message.content)
                    elif isinstance(message, AIMessage):
                        with st.chat_message("assistant"):
                            st.markdown(message.content)
                
                # Show thinking spinner and generate response inside container
                if prompt:
                    with st.chat_message("assistant"):
                        with st.spinner("thinking..."):
                            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.8)
                            result = llm.invoke(st.session_state.messages).content
                            st.markdown(result)
                            st.session_state.messages.append(AIMessage(result))
        else:
            generate(st.session_state.topic_data)
            st.session_state.mindmap_generated = True