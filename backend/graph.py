from typing import TypedDict
from langgraph.graph import StateGraph, END
from tools import extract_interaction_tool, summarize_tool, suggest_tool
from db import save_interaction, get_last_interaction, update_last_interaction
from llm import ask_llm
import re


# =========================
# STATE
# =========================
class CRMState(TypedDict):
    input: str
    intent: str
    data: dict
    response: str


# =========================
# INTENT CLASSIFIER
# =========================
def classify_intent(state: CRMState):
    text = state["input"].lower()

    # ✅ update MUST come before create
    if any(x in text for x in ["update", "change", "modify", "rename"]):
        state["intent"] = "update"

    elif any(x in text for x in ["doctor", "met", "treatment", "discussed", "visit"]):
        state["intent"] = "create"

    elif "summary" in text or "summarize" in text:
        state["intent"] = "summary"

    elif any(x in text for x in ["suggest", "next"]):
        state["intent"] = "suggest"

    else:
        state["intent"] = "chat"

    return state


# =========================
# CREATE NODE
# =========================
def create_node(state: CRMState):
    data = extract_interaction_tool(state["input"])
    state["data"] = data
    state["response"] = data
    return state


# =========================
# UPDATE PARSER
# =========================
def parse_update_fields(text):
    updates = {}
    text_lower = text.lower()

    # doctor
    match = re.search(r"(?:doctor|dr\.?)\s*(?:to|name)?\s*([a-zA-Z ]+)", text_lower)
    if match:
        updates["doctor"] = match.group(1).strip().title()

    # date
    match = re.search(r"date\s*(?:to)?\s*([a-zA-Z0-9 ]+)", text_lower)
    if match:
        updates["date"] = match.group(1).strip()

    # type
    match = re.search(r"type\s*(?:to)?\s*([a-zA-Z ]+)", text_lower)
    if match:
        updates["type"] = match.group(1).strip().lower()

    # notes
    match = re.search(r"notes?\s*(?:to)?\s*(.+)", text_lower)
    if match:
        updates["notes"] = match.group(1).strip()

    return updates


# =========================
# UPDATE NODE
# =========================
def update_node(state: CRMState):
    last = get_last_interaction()

    if not last:
        state["response"] = "No interaction to update."
        return state

    updates = parse_update_fields(state["input"])

    if not updates:
        state["response"] = "No valid fields found to update."
        return state

    merged = {
        "doctor": updates.get("doctor", last["doctor"]),
        "date":   updates.get("date",   last["date"]),
        "type":   updates.get("type",   last["type"]),
        "notes":  updates.get("notes",  last["notes"]),
    }

    update_last_interaction(merged)

    # ✅ Send only changed fields to frontend
    state["data"] = updates
    state["response"] = updates
    return state


# =========================
# SUMMARY NODE
# =========================
def summary_node(state: CRMState):
    last = get_last_interaction()

    if not last:
        state["response"] = "No interaction to summarize."
    else:
        state["response"] = summarize_tool(state["input"], last)

    return state


# =========================
# SUGGEST NODE
# =========================
def suggest_node(state: CRMState):
    last = get_last_interaction()

    if not last:
        state["response"] = "No interaction available."
    else:
        state["response"] = suggest_tool(state["input"], last)

    return state


# =========================
# CHAT NODE
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
# GRAPH BUILD
# =========================
workflow = StateGraph(CRMState)

workflow.add_node("classify", classify_intent)
workflow.add_node("create", create_node)
workflow.add_node("update", update_node)
workflow.add_node("summary", summary_node)
workflow.add_node("suggest", suggest_node)
workflow.add_node("chat", chat_node)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    route,
    {
        "create": "create",
        "update": "update",
        "summary": "summary",
        "suggest": "suggest",
        "chat": "chat"
    }
)

workflow.add_edge("create", END)
workflow.add_edge("update", END)
workflow.add_edge("summary", END)
workflow.add_edge("suggest", END)
workflow.add_edge("chat", END)

app_graph = workflow.compile()


# =========================
# MAIN FUNCTION
# =========================
def run_graph(user_input: str):
    result = app_graph.invoke({
        "input": user_input,
        "intent": "",
        "data": {},
        "response": ""
    })

    return result["response"]