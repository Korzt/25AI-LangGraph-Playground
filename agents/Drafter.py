import os
import re
from typing import Annotated, Sequence, TypedDict
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

document_content = ""
RESOURCES_DIR = Path("resources")
RESOURCES_DIR.mkdir(exist_ok=True)
FILENAME_REGEX = re.compile(r'^[\w\-\.]+$')

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def update(content: str) -> str:
    """Updates the in-memory document content."""
    global document_content
    document_content = content
    return f"Document has been updated successfully! The current content is:\n{document_content}"

@tool
def save(filename: str) -> str:
    """Saves the in-memory document content to a file in the 'resources/' directory."""
    global document_content

    # if not filename.endswith('.txt'):
    #     filename += '.txt'

    if not FILENAME_REGEX.match(filename):
        return "❌ Invalid filename. Use only letters, numbers, dashes, underscores, and extensions."

    full_path = (RESOURCES_DIR / filename).resolve()
    if not str(full_path).startswith(str(RESOURCES_DIR.resolve())):
        return "❌ Access outside the 'resources/' directory is not allowed."

    try:
        with full_path.open('w') as file:
            file.write(document_content)
        print(f"\n💾 Document has been saved to: {full_path}")
        return f"✅ Document has been saved successfully to '{full_path}'."
    except Exception as e:
        return f"❌ Error saving document: {str(e)}"

@tool
def load(filename: str) -> str:
    """Loads content from a file in the 'resources/' directory into memory."""
    if not FILENAME_REGEX.match(filename):
        return "❌ Invalid filename. Use only letters, numbers, dashes, underscores, and extensions."

    full_path = (RESOURCES_DIR / filename).resolve()
    if not str(full_path).startswith(str(RESOURCES_DIR.resolve())):
        return "❌ Access outside the 'resources/' directory is not allowed."

    if not full_path.exists():
        return f"❌ File '{filename}' does not exist."

    try:
        global document_content
        document_content = full_path.read_text()
        return f"📄 Document '{filename}' loaded successfully. Current content:\n{document_content}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"

@tool
def list_files() -> str:
    """Lists all files in the 'resources/' directory."""
    files = list(RESOURCES_DIR.glob("*"))
    if not files:
        return "📁 No files found in the 'resources/' directory."
    return "📂 Available files:\n" + "\n".join(f.name for f in files)

tools = [update, save, load, list_files]
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash").bind_tools(tools)

def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.

    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - If the user wants to load an existing document, use the 'load' tool.
    - You can list available documents using the 'list_files' tool.
    - Make sure to always show the current document state after modifications.

    The current document content is:{document_content}
    """)

    if not state["messages"]:
        user_input = "I'm ready to help you update a document. What would you like to create?"
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)

    print(f"\n🤖 AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    if not messages:
        return "continue"
    for message in reversed(messages):
        if isinstance(message, ToolMessage) and "saved" in message.content.lower() and "document" in message.content.lower():
            return "end"
    return "continue"

def print_messages(messages):
    if not messages:
        return
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n🛠️ TOOL RESULT: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges("tools", should_continue, {"continue": "agent", "end": END})
app = graph.compile()

def run_document_agent():
    print("\n ===== DRAFTER =====")
    state = {"messages": []}
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    print("\n ===== DRAFTER FINISHED =====")

if __name__ == "__main__":
    run_document_agent()
