from mistralai import Mistral
import base64
import time
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
#  changing this to mistral ocr
mistral_api_key= os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=mistral_api_key)
def extract_from_mistral(pdf_file):
    pdf_bytes=pdf_file.read()
    encoded_pdf=base64.b64encode(pdf_bytes).decode('utf-8')
    document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
    try:
        ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
        time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
        
        pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
        result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
    except Exception as e:
        result_text = f"Error extracting result: {e}"
        st.cache_data.clear()
    # ocr_response = client.ocr.process(
    #     model="mistral-ocr-latest",
    #     document={
    #         "type": "uploaded",
    #         "document_url": signed_url.url,
    #     }
    # )
    return result_text
