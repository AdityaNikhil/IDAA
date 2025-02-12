from models import State
from config import llm
from models import sqlquery
from langchain_community.utilities import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import QuerySQLDataBaseTool
import os
import time

db_path = os.environ.get("DATABASE_URI")
db = SQLDatabase.from_uri(db_path, include_tables=["cryptocurrencies", "market_data"])

# Test Database connection
def test_db_connection(db):
    try:
        test_connection = {
            'table_1':db.run("SELECT * FROM cryptocurrencies LIMIT 1"),
            'table_2':db.run("SELECT * FROM market_data LIMIT 1")
        }
        for _, status in enumerate(test_connection):
            if 'Error' in status:
                return 'Error'
        return 'Success'
    except:
        return 'Error'

def correct_query(state: State): 
    query = state["sql_query"]
    question = state['question']
    schema = db.get_table_info()
    
    query_check_system = f"""You are a Postgres SQL expert with a strong attention to detail.
    For the given question: {question}, double check the Postgres SQL query if it is relevant to the given question and check for common mistakes, including:
    - Using NOT IN with NULL values
    - Using UNION when UNION ALL should have been used
    - Using BETWEEN for exclusive ranges
    - Data type mismatch in predicates
    - Properly quoting identifiers
    - Using the correct number of arguments for functions
    - Casting to the correct data type
    - Using the proper columns for joins

    If there are any of the above mistakes or the query is irrelevant to the given question, rewrite the query. 
    If there are no mistakes, just reproduce the original query.
    DO NOT provide any explanations, comments, or additional context.
    ONLY output the SQL query itself.

    Here's the original table schema:
    {schema}

    """
    max_retries = 3
    retry_delay = 2

    query_check_prompt = ChatPromptTemplate.from_messages(
        [("system", query_check_system), 
         ("human", f"{query}")]
    )

    query_check = query_check_prompt | llm.with_structured_output(sqlquery) 
    
    for attempt in range(max_retries):
        try:
            query = query_check.invoke({}).sql_query
            response = db.run_no_throw(query)
            
            if 'Error' in response:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    state['sql_query'] = ""
                    break
            
            # Extract the SQL query if successful
            state['sql_query'] = query
            break
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            else:
                state['sql_query'] = ""
                break
    
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
            
            ** STRICTLY DO NOT MENTION how you obtained the result, WHERE YOU GOT the result from or any of sql calculations. **
             """),
        ]
    )
    chain = prompt | llm 
    response = chain.invoke({})
    state["agent_result"] = response.content
    
    return state
