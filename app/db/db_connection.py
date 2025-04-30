# import mysql.connector
# from mysql.connector import Error
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file (optional but recommended)
# load_dotenv()

# def get_connection():
#     """
#     Creates and returns a connection to MySQL database using environment variables.
    
#     Returns:
#         connection: MySQL database connection object if successful, None otherwise
#     """
#     try:
#         connection = mysql.connector.connect(
#             host=os.getenv("DB_HOST", "localhost"),
#             user=os.getenv("DB_USER", "root"),
#             password=os.getenv("DB_PASSWORD", "12345678"),
#             database=os.getenv("DB_NAME", "clinical_study_db")
#         )
        
#         if connection.is_connected():
#             print("Database connected Successfully !!!!")
#             return connection
            
#     except Error as e:
#         print(f"Error connecting to MySQL database: {e}")
#         return None

# def close_connection(connection):
#     """
#     Safely closes a database connection.
    
#     Args:
#         connection: MySQL connection object to close
#     """
#     if connection and connection.is_connected():
#         connection.close()





import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional but recommended)
load_dotenv()

def get_connection():
    """
    Creates and returns a connection to PostgreSQL database using environment variables.
    
    Returns:
        connection: PostgreSQL database connection object if successful, None otherwise
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "admin"),
            dbname=os.getenv("DB_NAME", "clinical_study_db"),
            port=os.getenv("DB_PORT", "5432")
        )
        
        print("Database connected Successfully !!!!")
        return connection
            
    except Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def close_connection(connection):
    """
    Safely closes a database connection.
    
    Args:
        connection: PostgreSQL connection object to close
    """
    if connection:
        connection.close()