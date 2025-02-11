from models import State
from config import llm
from langchain.chains import create_sql_query_chain
from utils.database import db

def analyst_llm(state: State):
    question = state['question']
    generate_query = create_sql_query_chain(llm, db)

    query = generate_query.invoke({"question": question}) 
    state['sql_query']=query
        
    return state



