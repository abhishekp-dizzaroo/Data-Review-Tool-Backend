# from mysql.connector import Error
# from ..db.db_connection import get_connection, close_connection


# def execute_query(validated_sql):
#     """
#     Executes a validated SQL query and returns the result.
    
#     Args:
#         validated_sql (str): A validated SQL query to execute
        
#     Returns:
#         dict: A dictionary containing:
#             - 'success' (bool): Whether the query executed successfully
#             - 'data' (list): The result rows if applicable (for SELECT queries)
#             - 'message' (str): Success or error message
#             - 'rowcount' (int): Number of affected rows for non-SELECT queries
#     """
#     connection = None
#     cursor = None
#     result = {
#         'success': False,
#         'data': None,
#         'sql_query': validated_sql,
#         'message': '',
#         'rowcount': 0
#     }
    
#     try:
#         connection = get_connection()
#         if not connection:
#             result['message'] = "Failed to connect to database"
#             return result
            
#         cursor = connection.cursor(dictionary=True)
#         cursor.execute(validated_sql)
        
#         # Check if query is a SELECT statement
#         if validated_sql.strip().upper().startswith("SELECT"):
#             result['data'] = cursor.fetchall()
#             result['message'] = f"Query executed successfully. Returned {len(result['data'])} rows."
#             result['rowcount']=len(result['data'])
#         else:
#             connection.commit()
#             result['rowcount'] = cursor.rowcount
#             result['message'] = f"Query executed successfully. Affected {cursor.rowcount} rows."
        
#         result['success'] = True
        
#     except Error as e:
#         result['message'] = f"Error executing query: {e}"
#         # Rollback transaction if error occurred
#         if connection:
#             connection.rollback()
    
#     finally:
#         # Close cursor
#         if cursor:
#             cursor.close()
#         # Close connection
#         close_connection(connection)
        
#     return result













from psycopg2 import Error
from ..db.db_connection import get_connection, close_connection

def execute_query(validated_sql):
    """
    Executes a validated SQL query and returns the result.
    
    Args:
        validated_sql (str): A validated SQL query to execute
        
    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether the query executed successfully
            - 'data' (list): The result rows if applicable (for SELECT queries)
            - 'message' (str): Success or error message
            - 'rowcount' (int): Number of affected rows for non-SELECT queries
    """
    connection = None
    cursor = None
    result = {
        'success': False,
        'data': None,
        'sql_query': validated_sql,
        'message': '',
        'rowcount': 0
    }
    
    try:
        connection = get_connection()
        if not connection:
            result['message'] = "Failed to connect to database"
            return result
            
        cursor = connection.cursor()
        cursor.execute(validated_sql)
        
        # Check if query is a SELECT statement
        if validated_sql.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            columns = [desc[0] for desc in cursor.description]
            result['data'] = [dict(zip(columns, row)) for row in rows]
            result['message'] = f"Query executed successfully. Returned {len(result['data'])} rows."
            result['rowcount'] = len(result['data'])
        else:
            connection.commit()
            result['rowcount'] = cursor.rowcount
            result['message'] = f"Query executed successfully. Affected {cursor.rowcount} rows."
        
        result['success'] = True
        
    except Error as e:
        result['message'] = f"Error executing query: {e}"
        # Rollback transaction if error occurred
        if connection:
            connection.rollback()
    
    finally:
        # Close cursor
        if cursor:
            cursor.close()
        # Close connection
        close_connection(connection)
        
    return result