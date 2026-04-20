import streamlit as st
import requests
import os

st.set_page_config(page_title="CSV AI Agent", layout="wide")
st.title("🤖 CSV AI Agent")

# Sidebar: File Upload
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload a new CSV", type=["csv"])
    
    if uploaded_file is not None:
        # Save the file locally to the project folder
        with open(os.path.join(os.getcwd(), uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved: {uploaded_file.name}")

# Main Chat Interface
st.subheader("Chat with your Data")
user_query = st.text_input("Ask a question about your files:")

if st.button("Send"):
    if user_query:
        with st.spinner("Agent is thinking..."):
            # Send request to your FastAPI backend
            try:
                response = requests.post("API_URL"="https://csv-analysis-agent.onrender.com, json={"user_input": user_query})
                
                if response.status_code == 200:
                    st.markdown(f"**Agent:** {response.json()['agent_response']}")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI: {e}")
    else:
        st.warning("Please enter a question.")
