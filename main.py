from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from app.services.sql_query_generation_llm import generate_sql_query_by_sqlCoder, generate_sql_query_by_gemini, generate_sql_query_by_openai
from app.rag.generate_sql_query_by_rag import generate_sql_query_by_rag
from app.services.execute_query import execute_query
from app.services.gemini_ai import generate_response
from app.langchain.generate_and_execute_sql_query_by_langchain import generate_and_execute_sql_query_by_langchain
from app.langchain.agent import generate_sql_query_and_execute_by_agent

from app.routes import user

from app.db.mongo_db_connection import connect_to_mongodb, close_mongodb_connection



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup database connection events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongodb_connection()


@app.get("/")   
async def root():
    return {"message": "Hello World"}

class PromptRequest(BaseModel):
    prompt: str
    model: str

@app.post("/query", tags=["Query"])
async def handle_query(request: PromptRequest):
    prompt = request.prompt
    model = request.model
    print("PROMPT", prompt)
    print("MODEL", model)

    if model == "sqlCoder":
        sql_query = await generate_sql_query_by_sqlCoder(prompt)
        result = execute_query(sql_query)
    elif model == "gemini":
        sql_query = await generate_sql_query_by_gemini(prompt)
        result = execute_query(sql_query)
    elif model == "openAI":
        sql_query = await generate_sql_query_by_openai(prompt)
        result = execute_query(sql_query)
    elif model == "langchain":
        result = generate_and_execute_sql_query_by_langchain(prompt)
    
    elif model == "agent":
        result = generate_sql_query_and_execute_by_agent(prompt)
    else:
        sql_query = generate_sql_query_by_rag(prompt)
        result = execute_query(sql_query)
    
    print("RESULT", result)
    return {"data": result}



app.include_router(user.router, prefix="/user", tags=["User"])


# print(execute_query("""SELECT "Arm", COUNT(*) as subject_count FROM subjects GROUP BY "Arm"; """))
# print(execute_query("""SELECT tr."Subject_ID", tr."Visit", tr."Response" FROM tumor_response tr WHERE tr."Assessed_By" = 'Independent';"""))


@app.get("/chat", tags=["Chat"])
async def chat():
    result = await generate_response("Hello, How Are you?")
    return {"response": result}