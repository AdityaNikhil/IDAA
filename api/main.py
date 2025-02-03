# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflow.graph import create_workflow
from langchain_community.utilities import SQLDatabase
import os
from utils.database import db

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

@app.get("/health")
async def health_check():
    try:
        # Execute a simple query to check database connection
        db.run("SELECT * FROM cryptocurrencies LIMIT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
