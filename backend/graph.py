from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from tools import extract_interaction_tool, summarize_tool, suggest_tool
from db import save_interaction
from llm import ask_llm


# =========================
# STATE STRUCTURE
# =========================
class CRMState(TypedDict):
    input: str
    intent: str
    data: dict
    response: str


# =========================
# NODE 1: CLASSIFY INTENT
# =========================
def classify_intent(state: CRMState):
    text = state["input"].lower()

    if any(x in text for x in ["doctor", "met", "treatment"]):
        state["intent"] = "create"
    elif "update" in text or "change" in text:
        state["intent"] = "update"
    elif "summary" in text:
        state["intent"] = "summary"
    elif "suggest" in text or "next" in text:
        state["intent"] = "suggest"
    else:
        state["intent"] = "chat"

    return state


# =========================
# NODE 2: CREATE INTERACTION
# =========================
def create_node(state: CRMState):
    data = extract_interaction_tool(state["input"])
    save_interaction(data)
    state["data"] = data
    state["response"] = data
    return state


# =========================
# NODE 3: SUMMARY
# =========================
def summary_node(state: CRMState):
    state["response"] = summarize_tool(state["input"], state.get("data"))
    return state


# =========================
# NODE 4: SUGGESTION
# =========================
def suggest_node(state: CRMState):
    state["response"] = suggest_tool(state["input"], state.get("data"))
    return state


# =========================
# NODE 5: CHAT (DEFAULT)
# =========================
def chat_node(state: CRMState):
    state["response"] = ask_llm(state["input"])
    return state


# =========================
# ROUTER
# =========================
def route(state: CRMState):
    return state["intent"]


# =========================
# BUILD GRAPH
# =========================
workflow = StateGraph(CRMState)

workflow.add_node("classify", classify_intent)
workflow.add_node("create", create_node)
workflow.add_node("summary", summary_node)
workflow.add_node("suggest", suggest_node)
workflow.add_node("chat", chat_node)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    route,
    {
        "create": "create",
        "update": "create",   # reuse create logic
        "summary": "summary",
        "suggest": "suggest",
        "chat": "chat"
    }
)

workflow.add_edge("create", END)
workflow.add_edge("summary", END)
workflow.add_edge("suggest", END)
workflow.add_edge("chat", END)

app_graph = workflow.compile()


# =========================
# MAIN FUNCTION (USED IN FASTAPI)
# =========================
def run_graph(user_input: str):
    result = app_graph.invoke({
        "input": user_input,
        "intent": "",
        "data": {},
        "response": ""
    })

    return result["response"]