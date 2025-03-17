# app/agents/supervisor.py
from models import State, QueryOutput
from config import llm, SUPERVISOR_LLM_PROMPT
from langchain.prompts.chat import ChatPromptTemplate

def supervisor_agent(state: State):
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
    elif state["agents"].lower() == "advisor":
        return "advisor"
    elif state["agents"].lower() == "prof":
        return "prof"
    else:
        return "Irrelevant Query"
    
def end_node(state: State):
    
    state['response'] = "Sorry, I can only answer questions relating to the digital assets."

    return state
