from langgraph.graph import StateGraph, START, END
from models import State
from agents.supervisor import supervisor_llm, supervisor_router
from agents.analyst import analyst_llm
from agents.educator import educate_llm
from utils.database import correct_query, execute_query, generate_answer


def create_workflow():
    workflow = StateGraph(State)

    workflow.add_node("supervisor", supervisor_llm)
    workflow.add_node("analyst", analyst_llm)
    workflow.add_node("educate", educate_llm)
    workflow.add_node("correct_query", correct_query)
    workflow.add_node("execute_sql", execute_query)
    workflow.add_node("generate_human_readable_answer", generate_answer)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "analyst": "analyst",
            "educate": "educate",
            "finish": END
        },
    )

    workflow.add_edge("analyst", "correct_query")
    workflow.add_edge("correct_query", "execute_sql")
    workflow.add_edge("execute_sql", "generate_human_readable_answer")

    workflow.add_edge("educate", END)
    workflow.add_edge("generate_human_readable_answer", END)

    return workflow.compile()
