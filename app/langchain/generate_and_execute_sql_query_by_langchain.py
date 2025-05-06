import os
import getpass
from langchain_community.utilities import SQLDatabase
from typing_extensions import TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv()


host=os.getenv("DB_HOST", "localhost")
user=os.getenv("DB_USER", "postgres")
password=os.getenv("DB_PASSWORD", "admin")
dbname=os.getenv("DB_NAME", "clinical_study_db")
port=os.getenv("DB_PORT", "5432")


# Define the State type for the graph
class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

# Connect to PostgreSQL database
db = SQLDatabase.from_uri(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

# Set up OpenAI API key
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY environment variable is not set")

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# # Initialize the language model
# llm = init_chat_model("gpt-4o-mini", model_provider="openai")


if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Pull the SQL query system prompt from the hub
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

# Define the output structure for the SQL query generation
class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 50,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

def execute_query(state: State):
    """Execute SQL query and return structured results."""
    # Instead of using the QuerySQLDatabaseTool directly, we'll handle the execution ourselves
    # to ensure consistent formatting of results
    
    try:
        # Create a connection using the db's engine
        engine = db._engine
        with engine.connect() as connection:
            # Execute the query
            result = connection.execute(text(state["query"]))
            
            # Get column names
            columns = result.keys()
            
            # Convert rows to list of dictionaries (same format as first file)
            structured_result = [dict(zip(columns, row)) for row in result]
            
    except Exception as e:
        # If there's an error, return empty list and log the error
        print(f"Error executing SQL query: {e}")
        structured_result = []
    
    return {"result": structured_result}

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

# Build the graph
graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()


def generate_and_execute_sql_query_by_langchain(prompt):
    """
    Generates and executes SQL query using LangChain and returns results in a format 
    matching the first file's structure.
    """
    try:
        # Invoke the graph with the user prompt
        result = graph.invoke({"question": prompt})
        
        # Get the result (which should now be properly structured as a list of dictionaries)
        structured_data = result.get('result', [])
        
        return {
            'success': True,
            'data': structured_data,  # This will be a list of dictionaries matching first file
            'sql_query': result.get('query', ''),
            'answer': result.get('answer', ''),
            'message': 'Query executed successfully',
            'rowcount': len(structured_data)
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'sql_query': '',
            'message': str(e),
            'rowcount': 0,
            'answer': ''
        }