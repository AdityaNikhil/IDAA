from models import State
from config import llm
from models import sqlquery
from langchain_community.utilities import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import QuerySQLDataBaseTool
import os
import time
import json

# Test Database connection
def test_db_connection():
    db_path = os.environ.get("DATABASE_URI")
    global db
    try:
        db = SQLDatabase.from_uri(db_path, include_tables=["cryptocurrencies", "market_data"])
        test_connection = {
            'table_1':db.run("SELECT * FROM cryptocurrencies LIMIT 1"),
            'table_2':db.run("SELECT * FROM market_data LIMIT 1")
        }
        for _, status in enumerate(test_connection):
            if 'Error' in status:
                return False, 'Error'
        return db, 'Success'
    except:
        return False, 'Error'

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
        state["response"] = result
        state['query_result'] = result
    except:
        state["response"] = ""
        state['query_result'] = ""

    return state


def generate_response(state: State):
  
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
                Given the following user query and context, generate a response that directly answers the user query using relevant 
                information from the context. Ensure that the response is clear, concise, and well-structured. 

                Question: {question} 
                Context: {context} 
                sources: {sources}

                Provide a human-readable response directly addressing the user query in a proper markdown format.
             """
             )
        ]
    )
    chain = prompt | llm 

    if not state['sources'] :

        response = chain.invoke({"question": state["question"], "context": state["query_result"], "sources": ''})
        state["response"] = response.content
        
        return state

    content = "\n\n".join([summary for summary in state["summarized_results"]])
    response = chain.invoke({"question": state["question"], "context": content, "sources": state['sources']})
    state['response'] = response.content + '\n\n'+ '### References' + '\n' + '\n'.join([f'[{url}]({url})' for url in state['sources']]) # Add markdown links to the sources

    return state

def extract_response_and_code(response_text: str):
    try:
        # Split the response into sections
        parts = response_text.split("agent_response:")
        if len(parts) > 1:
            # Further split to separate agent response and python code
            content = parts[1].split("data:")

            # Extract and clean the agent response
            agent_response = content[0].strip()

            # Extract and clean the python code
            data = content[1].strip() if len(content) > 1 else ""

            return {
                "agent_response": agent_response,
                "data": data
            }
    except Exception as e:
        print(f"Error parsing response: {str(e)}")
        return None
    

def generate_chart(state: State):

    if "show" in state["question"].lower() or "plot" in state["question"].lower() or "generate" in state["question"].lower():
        question = state["question"]
        query_result = state["query_result"]
        response = state["response"]

        if not query_result == "": # In case the query was successful

            prompt = ChatPromptTemplate.from_messages(
                [
                ("system",f""" Given the user question {question}, and the human readable answer {response}, 
                 
                Generate a structured response for a chart instead of Python code.
                    
                    Extract:
                    - `x`: List of lists representing X-axis data points.
                        e.g. [2020,2021,2022,2023...]
                    - `series`: series of data to show on chart. 
                        e.g. uv:[100,200,300,400], pv:[100,200,300,400], ...
                    - `x_label`: String for X-axis label.
                    - `y_label`: String for Y-axis label.
                    - `title`: String for the chart title.
                    - `chart_type`: String specifying the type of chart ("line", "bar" only).

                
                ** STRICTLY DO NOT MENTION any extra details apart from the python code. **
                ** PROVIDE SYNTACTICALLY CORRECT PYTHON CODE ONLY. ENSURE EVERYTHING IS DEFINED PROPERLY**
                 
                Also, you will rewrite the human readable answer. Remove all other irrelevant details about generating the plot.  
                 
                Structure the response in the following format:
                
                agent_response: <your response>
                data: <a structured response>

                """),
                ]
            )
            chain = prompt | llm

            response = chain.invoke({})
            response = extract_response_and_code(response.content)

            state['response'] = response['agent_response']
            state['data'] = json.loads(response['data'])

            return state

    return state
