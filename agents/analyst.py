from models import State
from config import llm, ANALYST_SYS_PROMPT
from langchain.chains import create_sql_query_chain
from utils.database import db
from langchain.prompts import PromptTemplate

analyst_prompt = prompt = PromptTemplate(
    input_variables=["dialect", "table_info", "input", "top_k"],
    template=ANALYST_SYS_PROMPT
)

def analyst_agent(state: State):
    question = state['question']
    generate_query = create_sql_query_chain(llm, db, prompt=analyst_prompt)
    try:
        query = generate_query.invoke({"question": question}) 
        state['sql_query']=query.split('SQLQuery: ')[1]
    except:
        state['sql_query'] = ""
        
    return state


