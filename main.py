from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from app.services.sql_query_generation_llm import generate_sql, generate_sql_query_by_gemini, generate_sql_query_by_openai
from app.services.execute_query import execute_query
from app.services.gemini_ai import generate_response


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")   
async def root():
    return {"message": "Hello World"}

class PromptRequest(BaseModel):
    prompt: str

@app.post("/query", tags=["Query"])
async def handle_query(request: PromptRequest):
    prompt = request.prompt
    print("PROMPT", prompt)

    # sql_query = generate_sql(prompt) 
    # sql_query = await generate_sql_query_by_gemini(prompt)
    sql_query = await generate_sql_query_by_openai(prompt)
    print("SQL QUERY", sql_query)
    
    result = execute_query(sql_query)
    print("RESULT", result)

    return {"data": result}

# app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
# app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])


# print(execute_query("""SELECT "Arm", COUNT(*) as subject_count FROM subjects GROUP BY "Arm"; """))
# print(execute_query("""SELECT tr."Subject_ID", tr."Visit", tr."Response" FROM tumor_response tr WHERE tr."Assessed_By" = 'Independent';"""))


@app.get("/chat", tags=["Chat"])
async def chat():
    result = await generate_response("Hello, How Are you?")
    return {"response": result}