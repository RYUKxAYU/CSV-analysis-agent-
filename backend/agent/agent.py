from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from agent.tools import build_csv_tools

SYSTEM_PROMPT = """You are DataLens AI, a data analyst assistant.
You have ALREADY been given access to the user's uploaded CSV file.
NEVER ask the user for a file path, file name, or file location.
The file is already loaded. Use your tools directly to answer questions.
Always be concise and present numbers clearly."""


def build_agent(file_id: str, chat_history: list):
    """Build an agent executor for a specific file_id."""
    llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
    tools = build_csv_tools(file_id)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


def build_agent_with_memory(file_id: str, chat_history: list):
    """Build an agent with conversation memory."""
    llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
    tools = build_csv_tools(file_id)

    # Create memory
    memory = ConversationBufferWindowMemory(
        k=10,
        memory_key="chat_history",
        return_messages=True
    )

    # Add chat history to memory
    for msg in chat_history:
        if msg["role"] == "user":
            memory.add_user_message(msg["content"])
        else:
            memory.add_ai_message(msg["content"])

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False)


async def run_agent_query(file_id: str, message: str, chat_history: list = None) -> str:
    """Run a query against the agent."""
    if chat_history is None:
        chat_history = []
    
    agent_executor = build_agent_with_memory(file_id, chat_history)
    
    result = await agent_executor.ainvoke({
        "input": message,
    })
    
    return result.get("output", "I could not process that request.")