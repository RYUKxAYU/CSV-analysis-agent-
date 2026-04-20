import streamlit as st
import requests
import os
import base64
from io import StringIO

st.set_page_config(page_title="CSV AI Agent", layout="wide")
st.title("🤖 CSV AI Agent")

# Determine API URL based on environment
API_URL = os.environ.get("API_URL", "https://csv-analysis-agent.onrender.com")

# Sidebar: File Upload
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload a new CSV", type=["csv"])
    
    if uploaded_file is not None:
        # Read CSV content
        csv_content = uploaded_file.getvalue().decode("utf-8")
        st.success(f"Loaded: {uploaded_file.name}")

# Main Chat Interface
st.subheader("Chat with your Data")
user_query = st.text_input("Ask a question about your files:")

if st.button("Send"):
    if user_query:
        with st.spinner("Agent is thinking..."):
            try:
                request_data = {"user_input": user_query}
                
                # If file is uploaded, include CSV content
                if uploaded_file is not None:
                    request_data["csv_content"] = base64.b64encode(csv_content.encode()).decode()
                    request_data["filename"] = uploaded_file.name
                
                response = requests.post(f"{API_URL}/ask", json=request_data)
                
                if response.status_code == 200:
                    st.markdown(f"**Agent:** {response.json()['agent_response']}")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI: {e}")
    else:
        st.warning("Please enter a question.")