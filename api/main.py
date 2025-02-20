from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflow.graph import create_workflow
import os
from utils.database import db, test_db_connection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any domain (* for all)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class Query(BaseModel):
    question: str
    sql_query: str = ""
    query_result: str = ""
    agents: str = ""
    agent_result: str = ""
    viz_code: str = ""

@app.post("/process")
async def process_query(query: Query):
    # Your existing workflow logic here
    workflow = create_workflow()
    response = workflow.invoke(query.dict())
    return response

@app.get("/health")
async def health_check():

    # Execute a simple query to check database connection
    db_connection = test_db_connection(db)
    if db_connection == 'Error':
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    return {"status": "healthy", "database": "connected"}

