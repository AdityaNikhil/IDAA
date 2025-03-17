from langgraph.graph import StateGraph, START, END
from models import State
from agents.supervisor import supervisor_agent, supervisor_router, end_node
from agents.analyst import analyst_agent
from agents.advisor import advisor_agent
from agents.educator import search_web, summarize_results
from utils.database import correct_query, execute_query, generate_response, generate_chart


def create_workflow():

    workflow = StateGraph(State)

    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("advisor", advisor_agent)
    workflow.add_node("correct_query", correct_query)
    workflow.add_node("execute_sql", execute_query)
    workflow.add_node("prof", search_web)
    workflow.add_node("summarize_results", summarize_results)
    workflow.add_node("generate_chart", generate_chart)
    workflow.add_node("end_node", end_node)
    workflow.add_node("generate_response", generate_response)
    # workflow.add_node("redirect_node", redirect_node)


    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "analyst": "analyst",
            "prof": "prof",
            "advisor": "advisor",
            "Irrelevant Query": "end_node"
        },
    )

    workflow.add_edge("prof", "summarize_results")
    workflow.add_edge("summarize_results", "generate_response")

    workflow.add_edge("analyst", "correct_query")
    workflow.add_edge("correct_query", "execute_sql")
    # workflow.add_edge("execute_sql", "redirect_node")
    workflow.add_edge("execute_sql", "generate_response")

    workflow.add_edge("advisor", "generate_response")
    workflow.add_edge("generate_response", "generate_chart")
    workflow.add_edge("generate_chart", END)
    workflow.add_edge("end_node", END)

    app = workflow.compile()

    return app



