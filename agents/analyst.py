from models import State, ConvertToSQL
from config import llm, ANALYST_SYS_PROMPT
from langchain.prompts.chat import ChatPromptTemplate
from langchain.tools import QuerySQLDatabaseTool


def analyst_llm(state: State):
    system = ANALYST_SYS_PROMPT
    question = state["question"]
    human = f"Question: {question}"

    convert_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])

    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm
    result = sql_generator.invoke({})
    state["sql_query"] = result.sql_query
    return state




