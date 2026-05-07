import os
from pathlib import Path
from dotenv import load_dotenv
from typing import TypedDict, List

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)

from .tools import TOOLS
from .prompts import SYSTEM_PROMPT

# =========================
# LOAD ENV
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY non trouvée")

print(f"✅ Model: {GROQ_MODEL}")

# =========================
# LLM + TOOLS
# =========================
llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=GROQ_TEMPERATURE,
    api_key=GROQ_API_KEY
)

llm_with_tools = llm.bind_tools(TOOLS)

# =========================
# STATE
# =========================
class AgentState(TypedDict):
    messages: List
    session_id: str

# =========================
# LIMIT TOOL CALLS (SECURITY)
# =========================
MAX_STEPS = 10

# =========================
# NODE 1: CALL MODEL
# =========================
def call_model(state: AgentState):
    messages = state["messages"]

    system_message = SystemMessage(
        content=SYSTEM_PROMPT.format(
            tools=", ".join([t.name for t in TOOLS])
        )
    )

    response = llm_with_tools.invoke([system_message] + messages)

    return {
        "messages": messages + [response]
    }

# =========================
# ROUTER
# =========================
def should_continue(state: AgentState):
    last = state["messages"][-1]

    if hasattr(last, "tool_calls") and last.tool_calls:
        return "execute_tool"

    return END

# =========================
# NODE 2: EXECUTE TOOL
# =========================
def execute_tool(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    tools_map = {t.name: t for t in TOOLS}
    tool_messages = []

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:

        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id")

            print(f"🔧 TOOL CALL: {tool_name} -> {tool_args}")

            if tool_name not in tools_map:
                result = f"❌ Tool '{tool_name}' introuvable"
            else:
                try:
                    # sécurisation args
                    if isinstance(tool_args, str):
                        import json
                        tool_args = json.loads(tool_args)

                    result = tools_map[tool_name].invoke(tool_args)

                except Exception as e:
                    result = f"❌ Tool error: {str(e)}"

            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                )
            )

    return {
        "messages": messages + tool_messages
    }

# =========================
# BUILD GRAPH
# =========================
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_tool)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "execute_tool": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

app = workflow.compile(checkpointer=MemorySaver())

# =========================
# MAIN FUNCTION
# =========================
def get_bot_response(message: str, session_id: str):
    try:
        config = {"configurable": {"thread_id": session_id}}

        state = {
            "messages": [HumanMessage(content=message)],
            "session_id": session_id
        }

        final_state = app.invoke(state, config=config)

        # ✅ Debug : afficher tous les messages
        print("\n===== DEBUG MESSAGES =====")
        for msg in final_state["messages"]:
            print(f"TYPE: {type(msg).__name__}")
            print(f"CONTENT: {msg.content}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"TOOL_CALLS: {msg.tool_calls}")
            print("---")
        print("==========================\n")

        return final_state["messages"][-1].content

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Erreur technique: {str(e)}"