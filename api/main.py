# api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from workflow.graph import create_workflow

app = FastAPI()

class Query(BaseModel):
    question: str
    sql_query: str = ""
    query_result: str = ""
    agents: str = ""
    agent_result: str = ""

@app.post("/process")
async def process_query(query: Query):
    # Your existing workflow logic here
    workflow = create_workflow()
    response = workflow.invoke(query.dict())
    return response
