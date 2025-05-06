import os
from typing import List, Dict, Any


from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.document import Document

# 1. Set up environment
def setup_environment():
    """Set up environment variables for API keys."""
    # For OpenAI - you should store this in a secure environment variable
    # rather than hardcoding in production
    os.environ["OPENAI_API_KEY"] = "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"
    
    # If using other services, add their keys here
    # os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your-huggingface-token"

# 2. Load and prepare schema metadata from different file types
def load_schema_metadata(schema_file: str):
    """Load the database schema metadata from a file (PDF or TXT)."""
    try:
        file_extension = os.path.splitext(schema_file)[1].lower()
        
        if file_extension == '.pdf':
            # Use PyPDFLoader for PDF files
            loader = PyPDFLoader(schema_file)
            documents = loader.load()
            # Combine all pages into a single text
            schema_metadata = "\n".join([doc.page_content for doc in documents])
        elif file_extension == '.txt':
            # Use TextLoader for text files
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_metadata = f.read()
        
            
        print(f"Loaded schema metadata from {schema_file} ({len(schema_metadata)} characters)")
        return schema_metadata
    except Exception as e:
        print(f"Error loading schema metadata: {e}")
        # Fallback to default metadata if file not found or error occurs
        print("Using default schema metadata.")

# 3. Split schema metadata into chunks for embedding
def prepare_schema_chunks(schema_metadata, chunk_size=1500, chunk_overlap=300):
    """Split schema metadata into manageable chunks."""
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    
    # Create Document objects manually
    doc = Document(page_content=schema_metadata, metadata={"source": "schema_metadata"})
    chunks = text_splitter.split_documents([doc])
    
    print(f"Split schema metadata into {len(chunks)} chunks")
    return chunks

# 4. Create vector embeddings
def create_embeddings(chunks, embedding_type="openai", persist_directory="sql_db"):
    """Create and store vector embeddings."""
    
    # Choose embedding model
    if embedding_type == "openai":
        embeddings = OpenAIEmbeddings()
    elif embedding_type == "huggingface":
        # Use a free, locally-runnable model
        model_name = "sentence-transformers/all-mpnet-base-v2"
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
    else:
        print(f"Unknown embedding type: {embedding_type}. Using OpenAI embeddings.")
        embeddings = OpenAIEmbeddings()
        
    # Create vector store
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    # Persist the database
    vectordb.persist()
    
    return vectordb

# 5. Create SQL generation chain
def create_sql_chain(vectordb, model_name="gpt-4o-mini", temperature=0):
    """Create the SQL generation chain."""
    
    # Initialize LLM
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    
    # Create a custom prompt template for SQL generation
    # This is specifically designed to output ONLY the SQL query

    template = """
        Given an input question, create a syntactically correct PostgreSQL query to
        run to help find the answer. 
        You can order the results by a relevant column to
        return the most interesting examples in the database.

        Never query for all the columns from a specific table, only ask for a the
        few relevant columns given the question.

        Pay attention to use only the column names that you can see in the schema
        description. Be careful to not query for columns that do not exist. Also,
        pay attention to which column is in which table.

        
        Only use the following tables:
        {context}

    
        User Request:
        {question}

        SQL:
    """
    # template = """
    #     You are an expert SQL developer specializing in clinical trial databases.

    #     Below is the relevant database schema and sample data context:
    #     {context}

    #     Instructions:
    #     - Analyze the user's request carefully.
    #     - Take the column name properly without any syntax error.
    #     - Only include the necessary tables and columns in your SQL.
    #     - Use proper JOINs and WHERE clauses.
    #     - Ensure all column names and table names match the schema exactly.
    #     - If date comparisons are needed, use available DATE columns only.
    #     - Do NOT generate any explanatory text, markdown formatting, or comments.
    #     - Output must be a single-line SQL query, syntactically correct.

    #     User Request:
    #     {question}

    #     SQL:
    # """
    
    prompt = PromptTemplate.from_template(template)
    
    # Set up the retriever with increased K to get more context
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 40})
    
    # Create the RAG chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    sql_chain = (
        {"context": retriever | format_docs, 
         "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return sql_chain

# 6. Main SQL RAG system
class SQLQueryGenerator:
    def __init__(self, schema_file=None, embedding_type="openai", model_name="gpt-4o"):
        """Initialize the SQL Query Generator."""
        # Setup
        setup_environment()
        
        # Load schema metadata (from file or use default)
        if schema_file:
            schema_metadata = load_schema_metadata(schema_file)

        
        # Process schema
        chunks = prepare_schema_chunks(schema_metadata)
        
        # Create vector store
        self.vectordb = create_embeddings(chunks, embedding_type)
        
        # Create SQL chain
        self.sql_chain = create_sql_chain(self.vectordb, model_name, temperature=0)
    
    def generate_query(self, natural_language_request: str) -> str:
        """Generate SQL query from natural language."""
        # Generate SQL query
        sql_query = self.sql_chain.invoke(natural_language_request)
        
        # Clean the output to ensure it's just one line with no extra formatting
        sql_query = sql_query.strip()
        
        # Remove any markdown code block formatting if present
        if sql_query.startswith('```sql') and '```' in sql_query:
            sql_query = sql_query.split('```sql')[1].split('```')[0].strip()
        elif sql_query.startswith('```') and sql_query.endswith('```'):
            sql_query = sql_query[3:-3].strip()
            
        # Replace any newlines with spaces for a single line SQL query
        sql_query = ' '.join(sql_query.split())
            
        return sql_query
    
    def validate_sql(self, sql_query: str) -> bool:
        """
        Basic validation of SQL query syntax.
        Could be extended in the future to connect to a database for full validation.
        """
        # Basic validation checks
        sql_lower = sql_query.lower()
        
        # Check for basic SQL structure
        has_select = "select" in sql_lower
        has_from = "from" in sql_lower
        
        # Check balance of parentheses
        balanced_parens = sql_query.count('(') == sql_query.count(')')
        
        # Check for common syntax errors
        no_double_commas = ",," not in sql_query
        
        return has_select and has_from and balanced_parens and no_double_commas

# Constants from the provided data








def generate_sql_query_by_rag(prompt):
    # Use correct relative path to the constant directory
    schema_file_path = "app/constant/file.txt" 

    sql_generator = SQLQueryGenerator(schema_file=schema_file_path)
    
    print(f"\nNatural language request: {prompt}")
    sql = sql_generator.generate_query(prompt)
    print(f"SQL query: {sql}")
        
    # Validate the SQL query
    if sql_generator.validate_sql(sql):
        print("✓ SQL syntax validation passed")
    else:
        print("✗ SQL syntax validation failed")

    return sql
    









# # Example usage
# if __name__ == "__main__":
#     # Initialize SQL Query Generator with file path
#     # Replace with your actual schema file path
#     schema_file_path = "../constant/file.txt"  # or schema_metadata.pdf
    
#     # Check if file exists, otherwise use default
#     if os.path.exists(schema_file_path):
#         sql_generator = SQLQueryGenerator(schema_file=schema_file_path)
    
    
#     # Example queries to test
#     request = "List all female subjects with their enrollment dates."
    
#     # Generate and print SQL queries
#     print(f"\nNatural language request: {request}")
#     sql = sql_generator.generate_query(request)
#     print(f"SQL query: {sql}")
        
#     # Validate the SQL query
#     if sql_generator.validate_sql(sql):
#         print("✓ SQL syntax validation passed")
#     else:
#         print("✗ SQL syntax validation failed")