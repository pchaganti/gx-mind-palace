import streamlit as st
from github_scraper import github_extractor
from generator import generate
from segmentor_summarizer import ss_pdf_text, ss_repo_text
from pdf_ocr import extract_from_mistral
from new_rag import rag, create_embeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import partial
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# Initialize session state variables
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.extracted_text = ""
    st.session_state.vectorstore = None
    st.session_state.messages = [SystemMessage("You are an assistant for question-answering tasks.")]
    st.session_state.content_generated = False
    st.session_state.topic_data = None
    st.session_state.active_tab = 0
    st.session_state.mindmap_generated = False
    st.session_state.tab_selection = "Mindmap"  # Initialize tab selection

# Add this cache decorator for the generate function
@st.cache_data(show_spinner=False)
def cached_generate(topic_data):
    return generate(topic_data)

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
    st.session_state.vectorstore = None
    st.session_state.active_tab = 0
    st.session_state.mindmap_generated = False  # Reset mindmap generation flag
    
    success = False
    if st.session_state.input_option == "github repository":
        success = process_github()
    else:
        success = process_pdf()
        
    if success:
        with st.spinner(text=f"analysing {'repository' if st.session_state.input_option == 'github repository' else 'pdf'}", show_time=False):
            if st.session_state.input_option == "github repository":
                st.session_state.topic_data = ss_repo_text(st.session_state.extracted_text)
            else:
                st.session_state.topic_data = ss_pdf_text(st.session_state.extracted_text)

def switch_tab(tab_index):
    st.session_state.active_tab = tab_index

# Main UI
st.set_page_config(page_title="mindpalace", page_icon="logo.png", layout="wide")
st.header('mindpalace')

# Input selection and collection
st.radio("select input source", ("github repository", "pdf document"), key="input_option")

if st.session_state.input_option == "github repository":
    st.text_input("enter gitHub repository url", key="github_url")
else:
    st.file_uploader("Upload your PDF", type="pdf", key="pdf")

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
    else:
        with st.expander("### Extracted Text"):
            st.write(st.session_state.extracted_text)
    
    # Create tabs for mindmap and chat
    if st.session_state.topic_data:
        # Add tab selector
        tab_selection = st.radio("Select View", ["Mindmap", "AI Chat"], 
                               horizontal=True, 
                               key="tab_selection")
        
        # Show content based on selected tab
        if tab_selection == "Mindmap":
            cached_generate(st.session_state.topic_data)
            st.session_state.mindmap_generated = True
        else:
            # Initialize vectorstore if needed
            if not st.session_state.vectorstore:
                with st.spinner(text="preparing AI system...", show_time=False):
                    st.session_state.vectorstore = create_embeddings(st.session_state.extracted_text)
            
            # Create a container with fixed height for chat messages
            chat_container = st.container(height=600)
            
            # Chat input before container
            if prompt := st.chat_input("Ask a question about the document"):
                st.session_state.messages.append(HumanMessage(prompt))
                
                # Get response from RAG
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 5})
                docs = retriever.invoke(prompt)
                
                system_prompt = f"""You are an AI assistant tasked with answering questions based solely on the provided context.
                Your goal is to generate a comprehensive answer for the given question using only the information available in the context.
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
                        with st.spinner("Thinking..."):
                            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.8)
                            result = llm.invoke(st.session_state.messages).content
                            st.markdown(result)
                            st.session_state.messages.append(AIMessage(result))
