from graph import run_graph


# =========================
# 🚀 MAIN AGENT ENTRY POINT
# =========================
def agent_logic(input_text: str):
    """
    Single entry point for all AI logic.
    Now fully controlled by LangGraph.
    """
    return run_graph(input_text)