# app/utils/database.py
from langchain.tools import QuerySQLDatabaseTool
from models import State
from config import llm
from langchain_community.utilities import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

db = SQLDatabase.from_uri("postgresql://postgres:postgres@localhost:5432", include_tables=["cryptocurrencies", "market_data"])

def execute_query(state: State):
    """Execute SQL query."""
    try:
        execute_query_tool = QuerySQLDatabaseTool(db=db)
        result = execute_query_tool.invoke(state["sql_query"])
        state["query_result"] = result
        return state
    except:
        raise ValueError("There was an error processing your request. Please try again.")

def generate_answer(state: State):
    question = state["question"]
    sql = state["sql_query"]
    result = state["query_result"]

    generate_prompt = ChatPromptTemplate.from_messages([
        (
            "human",
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {question}\n'
            f'SQL Query: {sql}\n'
            f'SQL Result: {result}'
            "If you find any errors or empty results: Simply say 'Am sorry, I cannot help you with that!'"
            "Never mention how you arrived at the answer"
        ),
    ])
    
    human_response = generate_prompt | llm | StrOutputParser()
    answer = human_response.invoke({})
    state["agent_result"] = answer
    return state
