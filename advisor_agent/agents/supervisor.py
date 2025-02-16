# app/agents/supervisor.py
from models import State, QueryOutput
from config import llm, SUPERVISOR_LLM_PROMPT
from langchain.prompts.chat import ChatPromptTemplate

def supervisor_llm(state: State):
    question = state["question"]
    if question == 'finish':
        state["agents"] = 'finish'
        return state

    system = SUPERVISOR_LLM_PROMPT
    human = f"Question: {question}"
    check_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])
    
    structured_llm = llm.with_structured_output(QueryOutput)
    agent_finder = check_prompt | structured_llm
    response = agent_finder.invoke({})
    state["agents"] = response.category
    return state

def supervisor_router(state: State):
    if state["agents"].lower() == "analyst":
        return "analyst"
    elif state["agents"].lower() == "finish":
        return "finish"
    return "educate"