# agent.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from tools import read_notebook, write_notebook, query_csv, analyze_csv, save_file, get_file

load_dotenv()

# Group them into the list the agent expects
TOOLS = [read_notebook, write_notebook, query_csv, analyze_csv]

SYSTEM_MESSAGE = (
    "You are a helpful assistant that can read/write text files and analyze CSV data. "
    "When a file_id is provided (e.g., 'Use file_id: xyz'), use analyze_csv with that file_id. "
    "When a CSV filepath is provided, use query_csv. "
    "Use analyze_csv first when analyzing uploaded files."
)

# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.1-70b-versatile", 
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Create the agent
agent = create_agent(llm, TOOLS, system_prompt=SYSTEM_MESSAGE)

def run_agent(user_input: str) -> str:
    """Run the agent with a user query."""
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"recursion_limit": 50}
        )
        return result["messages"][-1].content
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(run_agent("Check what is inside my sales_data_v1.csv file and summarize it."))