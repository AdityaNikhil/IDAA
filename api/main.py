from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflow.graph import create_workflow
import os
from utils.database import test_db_connection
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
    data: str = ""
    sources: list[str] = []
    web_results: list[str] = []
    summarized_results: list[str] = []
    agents: str = ""
    response: str = ""

@app.post("/process")
async def process_query(query: Query):
    # Your existing workflow logic here
    workflow = create_workflow()
    response = workflow.invoke(query.dict())
    return response

@app.get("/health")
async def health_check():

    # Execute a simple query to check database connection
    db, db_connection = test_db_connection()
    if db_connection == 'Error':
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    return {"status": "healthy", "database": "connected"}

