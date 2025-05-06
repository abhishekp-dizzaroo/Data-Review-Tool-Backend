# from langchain_community.utilities import SQLDatabase
# from langchain.chat_models import init_chat_model
# from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain_core.messages import HumanMessage
# from langgraph.prebuilt import create_react_agent
# import os
# import json
# from typing import Dict, List, Any, Optional, Union
# from dotenv import load_dotenv
# load_dotenv()



# host=os.getenv("DB_HOST")
# user=os.getenv("DB_USER")
# password=os.getenv("DB_PASSWORD")
# dbname=os.getenv("DB_NAME")
# port=os.getenv("DB_PORT")

# def execute_sql_query_with_llm_summary(
#     question: str,
#     db_uri: str = f"postgresql://{user}:{password}@{host}:{port}/{dbname}",
#     api_key: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Execute an SQL query based on a natural language question and return structured results.
    
#     Args:
#         question: Natural language question to be converted to SQL query
#         db_uri: Database connection URI
#         api_key: OpenAI API key (optional if already set in environment)
    
#     Returns:
#         Dictionary containing:
#         - success: Boolean indicating if the query was successful
#         - data: The raw SQL query result data
#         - sql_query: The SQL query that was executed
#         - answer: LLM's summary of the results
#         - message: Additional message (error or success)
#         - rowcount: Number of rows returned
#     """
#     # Set up OpenAI API key
#     if api_key:
#         os.environ["OPENAI_API_KEY"] = api_key
#     elif not os.environ.get("OPENAI_API_KEY"):
#         raise ValueError("OpenAI API key must be provided either directly or through environment variables")
    
#     # Initialize database connection
#     try:
#         db = SQLDatabase.from_uri(db_uri)
#     except Exception as e:
#         return {
#             'success': False,
#             'data': None,
#             'sql_query': None,
#             'answer': '',
#             'message': f"Database connection error: {str(e)}",
#             'rowcount': 0
#         }
    
#     # Initialize the language model
#     try:
#         llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        
#         # Create SQL tools and agent
#         toolkit = SQLDatabaseToolkit(db=db, llm=llm)
#         tools = toolkit.get_tools()
        
#         # Create system message for the agent
#         system_message = """
#         You are an agent designed to interact with a SQL database.
#         Given an input question, create a syntactically correct PostgreSQL query to run,
#         then look at the results of the query and return the answer. Unless the user
#         specifies a specific number of examples they wish to obtain, always limit your
#         query to at most 10 results.

#         You can order the results by a relevant column to return the most interesting
#         examples in the database. Never query for all the columns from a specific table,
#         only ask for the relevant columns given the question.

#         You MUST double check your query before executing it. If you get an error while
#         executing a query, rewrite the query and try again.

#         DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
#         database.

#         To start you should ALWAYS look at the tables in the database to see what you
#         can query. Do NOT skip this step.

#         Then you should query the schema of the most relevant tables.
#         """
        
#         # Create the agent
#         agent_executor = create_react_agent(llm, tools, prompt=system_message)
        
#         # Execute the agent
#         response_steps = []
#         sql_query = None
#         query_result = None
        
#         for step in agent_executor.stream(
#             {"messages": [{"role": "user", "content": question}]},
#             stream_mode="values",
#         ):
#             response_steps.append(step["messages"][-1])
            
#             # Try to extract SQL query from agent steps
#             content = step["messages"][-1].content if hasattr(step["messages"][-1], "content") else ""
#             if "```sql" in content:
#                 sql_start = content.find("```sql") + 6
#                 sql_end = content.find("```", sql_start)
#                 if sql_start > 0 and sql_end > sql_start:
#                     sql_query = content[sql_start:sql_end].strip()
            
#             # Look for query results in tool responses
#             if hasattr(step["messages"][-1], "additional_kwargs") and "tool_calls" in step["messages"][-1].additional_kwargs:
#                 for tool_call in step["messages"][-1].additional_kwargs.get("tool_calls", []):
#                     if tool_call.get("function", {}).get("name") == "sql_db_query":
#                         # This might contain query results
#                         args = json.loads(tool_call["function"].get("arguments", "{}"))
#                         if "query" in args:
#                             sql_query = args["query"]
        
#         # Extract the final answer from the last message
#         final_answer = response_steps[-1].content if response_steps else ""
        
#         # Execute the extracted SQL query directly to get results
#         # This is a fallback in case we couldn't extract results from the agent
#         if sql_query and not query_result:
#             try:
#                 query_result = db.run(sql_query)
#                 rowcount = len(query_result.split('\n')) - 2 if isinstance(query_result, str) else 0
#             except Exception as e:
#                 return {
#                     'success': False,
#                     'data': None,
#                     'sql_query': sql_query,
#                     'answer': final_answer,
#                     'message': f"Error executing SQL query: {str(e)}",
#                     'rowcount': 0
#                 }
        
#         return {
#             'success': True,
#             'data': query_result,
#             'sql_query': sql_query,
#             'answer': final_answer,
#             'message': "Query executed successfully",
#             'rowcount': rowcount if 'rowcount' in locals() else 0
#         }
        
#     except Exception as e:
#         return {
#             'success': False,
#             'data': None,
#             'sql_query': None,
#             'answer': '',
#             'message': f"Error: {str(e)}",
#             'rowcount': 0
#         }



# def execute_query(state: State):
#     """Execute SQL query and return structured results."""
#     # Instead of using the QuerySQLDatabaseTool directly, we'll handle the execution ourselves
#     # to ensure consistent formatting of results
    
#     try:
#         # Create a connection using the db's engine
#         engine = db._engine
#         with engine.connect() as connection:
#             # Execute the query
#             result = connection.execute(text(state["query"]))
            
#             # Get column names
#             columns = result.keys()
            
#             # Convert rows to list of dictionaries (same format as first file)
#             structured_result = [dict(zip(columns, row)) for row in result]
            
#     except Exception as e:
#         # If there's an error, return empty list and log the error
#         print(f"Error executing SQL query: {e}")
#         structured_result = []
    
#     return {"result": structured_result}

# def generate_sql_query_and_execute_by_agent(prompt):
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     result = execute_sql_query_with_llm_summary(
#         question=prompt,
#         api_key=OPENAI_API_KEY
#     )

#     return result







from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
import os
import json
import re
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv
from sqlalchemy import text
load_dotenv()

# Database connection parameters
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
dbname = os.getenv("DB_NAME")
port = os.getenv("DB_PORT")

def execute_sql_query_with_llm_summary(
    question: str,
    db_uri: str = f"postgresql://{user}:{password}@{host}:{port}/{dbname}",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute an SQL query based on a natural language question and return structured results.
    
    Args:
        question: Natural language question to be converted to SQL query
        db_uri: Database connection URI
        api_key: OpenAI API key (optional if already set in environment)
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if the query was successful
        - data: The structured SQL query result (list of dictionaries)
        - sql_query: The SQL query that was executed
        - answer: LLM's summary of the results
        - message: Additional message (error or success)
        - rowcount: Number of rows returned
    """
    # Set up OpenAI API key
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    elif not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OpenAI API key must be provided either directly or through environment variables")
    
    # Initialize database connection
    try:
        db = SQLDatabase.from_uri(db_uri)
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'sql_query': None,
            'answer': '',
            'message': f"Database connection error: {str(e)}",
            'rowcount': 0
        }
    
    # Initialize the language model
    try:
        llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        
        # Create SQL tools and agent
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()
        
        # Create system message for the agent
        system_message = """
        You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct PostgreSQL query to run,
        then look at the results of the query and return the answer.

        You can order the results by a relevant column to return the most interesting
        examples in the database. Never query for all the columns from a specific table,
        only ask for the relevant columns given the question.

        You MUST double check your query before executing it. If you get an error while
        executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
        database.

        To start you should ALWAYS look at the tables in the database to see what you
        can query. Do NOT skip this step.

        Then you should query the schema of the most relevant tables.
        """
        
        # Create the agent
        agent_executor = create_react_agent(llm, tools, prompt=system_message)
        
        # Execute the agent
        response_steps = []
        sql_query = None
        
        for step in agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
        ):
            response_steps.append(step["messages"][-1])
            
            # Try to extract SQL query from agent steps
            content = step["messages"][-1].content if hasattr(step["messages"][-1], "content") else ""
            if "```sql" in content:
                sql_start = content.find("```sql") + 6
                sql_end = content.find("```", sql_start)
                if sql_start > 0 and sql_end > sql_start:
                    sql_query = content[sql_start:sql_end].strip()
            
            # Look for query results in tool responses
            if hasattr(step["messages"][-1], "additional_kwargs") and "tool_calls" in step["messages"][-1].additional_kwargs:
                for tool_call in step["messages"][-1].additional_kwargs.get("tool_calls", []):
                    if tool_call.get("function", {}).get("name") == "sql_db_query":
                        # This might contain the SQL query
                        args = json.loads(tool_call["function"].get("arguments", "{}"))
                        if "query" in args:
                            sql_query = args["query"]
        
        # Extract the final answer from the last message
        final_answer = response_steps[-1].content if response_steps else ""
        
        # Execute the extracted SQL query directly to get structured results
        if sql_query:
            try:
                # Create a connection using the db's engine
                engine = db._engine
                with engine.connect() as connection:
                    # Execute the query
                    result = connection.execute(text(sql_query))
                    
                    # Get column names
                    columns = result.keys()
                    
                    # Convert rows to list of dictionaries
                    structured_data = [dict(zip(columns, row)) for row in result]
                    
                    return {
                        'success': True,
                        'data': structured_data,  # This will be a list of dictionaries
                        'sql_query': sql_query,
                        'answer': final_answer,
                        'message': 'Query executed successfully',
                        'rowcount': len(structured_data)
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'data': [],
                    'sql_query': sql_query,
                    'answer': final_answer,
                    'message': f"Error executing SQL query: {str(e)}",
                    'rowcount': 0
                }
        
        # If we couldn't extract or execute a SQL query
        return {
            'success': False,
            'data': [],
            'sql_query': sql_query,
            'answer': final_answer,
            'message': "Could not extract or execute a valid SQL query",
            'rowcount': 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'data': [],
            'sql_query': None,
            'answer': '',
            'message': f"Error: {str(e)}",
            'rowcount': 0
        }

def generate_sql_query_and_execute_by_agent(prompt):
    """
    Generate and execute an SQL query based on a natural language prompt.
    
    Args:
        prompt: The natural language question to convert to SQL
        
    Returns:
        Dictionary with structured query results
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    result = execute_sql_query_with_llm_summary(
        question=prompt,
        api_key=OPENAI_API_KEY
    )
    
    return result