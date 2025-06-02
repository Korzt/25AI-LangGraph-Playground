import asyncio
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

async def main():
    client = MultiServerMCPClient({
        "Math": {
            "command": "python",
            "args": ["mcp-servers/math-server.py"],
            "transport": "stdio"
        },
        "Weather": {
            "command": "python",
            "args": ["mcp-servers/weather-server.py"],
            "transport": "stdio"
        },
    })

    tools = await client.get_tools()

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash").bind_tools(tools)

    async def model_call(state: AgentState) -> AgentState:
        system_prompt = SystemMessage(content="You are my AI assistant, please answer my query to the best of your ability.")
        response = await model.ainvoke([system_prompt] + state["messages"])
        return {"messages": state["messages"] + [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "continue"
        return "end"

    graph = StateGraph(AgentState)
    graph.add_node("our_agent", model_call)
    graph.add_node("tools", ToolNode(tools=tools))
    graph.set_entry_point("our_agent")
    graph.add_conditional_edges("our_agent", should_continue, {
        "continue": "tools",
        "end": END
    })
    graph.add_edge("tools", "our_agent")

    app = graph.compile()

    inputs = {"messages": [HumanMessage(content="Add 40 + 12 and then multiply the result by 6. Also briefly tell me the weather alerts in CA")]}
    
    async def print_stream(stream):
        async for step in stream:
            msg = step["messages"][-1]
            print(getattr(msg, "content", msg))

    await print_stream(app.astream(inputs, stream_mode="values"))

asyncio.run(main())
