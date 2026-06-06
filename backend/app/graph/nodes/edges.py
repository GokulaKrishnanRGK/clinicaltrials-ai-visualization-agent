from __future__ import annotations

from app.graph.state import GraphState

MAX_REPAIRS = 2


def route_after_interpret(state: GraphState) -> str:
    return "end" if state.get("final_response") else "continue"


def route_after_assess(state: GraphState) -> str:
    if state.get("final_response"):
        return "end"
    if state["records"]:
        return "aggregate"
    if state["repair_count"] < MAX_REPAIRS:
        return "repair"
    return "give_up"
