from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    aggregate_data,
    assess_data_sufficiency,
    execute_tool_calls,
    generate_insight,
    generate_visualization_spec,
    interpret_question,
    message_insufficient,
    plan_tool_calls,
    repair_plan,
    route_after_assess,
    route_after_interpret,
    validate_response,
)
from app.graph.state import GraphState


def build_pipeline():
    graph = StateGraph(GraphState)

    graph.add_node("interpret_question", interpret_question)
    graph.add_node("plan_tool_calls", plan_tool_calls)
    graph.add_node("execute_tool_calls", execute_tool_calls)
    graph.add_node("assess_data_sufficiency", assess_data_sufficiency)
    graph.add_node("repair_plan", repair_plan)
    graph.add_node("aggregate_data", aggregate_data)
    graph.add_node("generate_visualization_spec", generate_visualization_spec)
    graph.add_node("generate_insight", generate_insight)
    graph.add_node("validate_response", validate_response)
    graph.add_node("message_insufficient", message_insufficient)

    graph.add_edge(START, "interpret_question")

    graph.add_conditional_edges(
        "interpret_question",
        route_after_interpret,
        {"end": END, "continue": "plan_tool_calls"},
    )
    graph.add_edge("plan_tool_calls", "execute_tool_calls")
    graph.add_edge("execute_tool_calls", "assess_data_sufficiency")

    graph.add_conditional_edges(
        "assess_data_sufficiency",
        route_after_assess,
        {
            "end": END,
            "aggregate": "aggregate_data",
            "repair": "repair_plan",
            "give_up": "message_insufficient",
        },
    )

    graph.add_edge("repair_plan", "execute_tool_calls")
    graph.add_edge("aggregate_data", "generate_visualization_spec")
    graph.add_edge("generate_visualization_spec", "generate_insight")
    graph.add_edge("generate_insight", "validate_response")
    graph.add_edge("validate_response", END)
    graph.add_edge("message_insufficient", END)

    return graph.compile()


_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
    return _pipeline
