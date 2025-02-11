from models import State
from config import llm
from langchain_community.utilities import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import QuerySQLDataBaseTool
import os

db_path = os.environ.get("DATABASE_URI")
db = SQLDatabase.from_uri(db_path, include_tables=["cryptocurrencies", "market_data"])

def correct_query(state: State): 
    query = state["sql_query"]
    schema = db.get_table_info()
    query_check_system = f"""You are a Postgres SQL expert with a strong attention to detail.
    Double check the Postgres SQL query for common mistakes, including:
    - Using NOT IN with NULL values
    - Using UNION when UNION ALL should have been used
    - Using BETWEEN for exclusive ranges
    - Data type mismatch in predicates
    - Properly quoting identifiers
    - Using the correct number of arguments for functions
    - Casting to the correct data type
    - Using the proper columns for joins

    If there are any of the above mistakes, rewrite the query. 
    If there are no mistakes, just reproduce the original query.
    
    **DO NOT provide any explanations, comments, or additional context.
    ONLY output the SQL query itself.**

    Here's the original table schema:
    {schema}

    """

    query_check_prompt = ChatPromptTemplate.from_messages(
        [("system", query_check_system), 
         ("human", f"{query}")]
    )
    query_check = query_check_prompt | llm | StrOutputParser()
    state['sql_query'] = query_check.invoke({})

    return state


def execute_query(state: State):
    execute_query_tool = QuerySQLDataBaseTool(db=db)
    try: 
        result = execute_query_tool.invoke(state["sql_query"])
        state["query_result"] = result
    except:
        state["query_result"] = ""

    return state


def generate_answer(state: State):
    question = state["question"]
    query = state["sql_query"]
    result = state["query_result"]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",f""" Given the following user question, corresponding SQL query, and the result 
            question {question},
            query {query},
            and the result {result}, provide a detailed response to the user.
            Do not mention how you obtained the result, where you got the result from or any of your calculations. 
             """),
        ]
    )
    chain = prompt | llm 
    response = chain.invoke({})
    state["agent_result"] = response.content
    
    return state
