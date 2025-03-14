from typing import TypedDict
from pydantic import BaseModel, Field

class State(TypedDict):
    question: str
    sql_query: str
    query_result: str
    sources: list[str]
    web_results: list[str]
    summarized_results: list[str]
    data: str
    agents: str
    response: str

class ConvertToSQL(BaseModel):
    sql_query: str = Field(
        description="The SQL query corresponding to the user's natural language question."
    )

class sqlquery(BaseModel):
    sql_query: str = Field(..., title="Syntactically correct SQL Query")

class QueryOutput(BaseModel):
    category: str = Field(description="Category of the query: analyst, prof, or finish")

class CheckPrompt(BaseModel):
    prompt_type: str = Field(description="Category of the prompt: YES or NO")
