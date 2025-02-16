# app/agents/educator.py
from models import State
from config import llm, EDUCATE_SYS_PROMPT
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def educate_llm(state: State):
    system = EDUCATE_SYS_PROMPT
    question = state["question"]
    human = f"Question: {question}"
    
    check_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])

    edu_chain = check_prompt | llm | StrOutputParser()
    response = edu_chain.invoke({})
    state["agent_result"] = response
    return state