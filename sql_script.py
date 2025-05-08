import psycopg2
import pandas as pd
import os
from io import StringIO
import sys

def set_environment_variables():
    """Set PostgreSQL environment variables if not already set"""
    # Only set if not already present in environment
    if 'PGHOST' not in os.environ:
        os.environ['PGHOST'] = 'data-review-tool-backend-server.postgres.database.azure.com'
    if 'PGUSER' not in os.environ:
        os.environ['PGUSER'] = 'nqbsiibsxa'
    if 'PGPORT' not in os.environ:
        os.environ['PGPORT'] = '5432'
    if 'PGDATABASE' not in os.environ:
        os.environ['PGDATABASE'] = 'postgres'  # Default database
    if 'PGPASSWORD' not in os.environ:
        os.environ['PGPASSWORD'] = 'puu8HnN$5PuhT9P7'
    
    print("Environment variables set for PostgreSQL connection.")

def create_connection():
    """Create a connection to the Azure PostgreSQL database using environment variables"""
    # Ensure environment variables are set
    set_environment_variables()
    
    try:
        print(f"Connecting to {os.environ.get('PGHOST')} as {os.environ.get('PGUSER')}...")
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            database=os.environ.get('PGDATABASE', 'postgres'),
            port=os.environ.get('PGPORT', '5432'),
            sslmode='require'
        )
        print("Successfully connected to the database!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        
        # Try alternative connection with server name in username
        try:
            print("\nTrying alternative connection method with server name in username...")
            host = os.environ.get('PGHOST')
            server_name = host.split('.')[0]  # Extract server name from host
            alternative_user = f"{os.environ.get('PGUSER')}@{server_name}"
            
            conn = psycopg2.connect(
                host=host,
                user=alternative_user,
                password=os.environ.get('PGPASSWORD'),
                database=os.environ.get('PGDATABASE', 'postgres'),
                port=os.environ.get('PGPORT', '5432'),
                sslmode='require'
            )
            print(f"Successfully connected using username: {alternative_user}")
            return conn
        except psycopg2.Error as alt_e:
            print(f"Alternative connection failed: {alt_e}")
            sys.exit(1)

# SQL statements to create database schema
CREATE_TABLES_SQL = """
CREATE DATABASE IF NOT EXISTS clinical_study_db;

CREATE TABLE IF NOT EXISTS subjects (
  subject_id INT NOT NULL,
  site_id VARCHAR(10) NULL,
  arm VARCHAR(45) NULL,
  dob DATE NULL,
  gender CHAR(1) NULL,
  enroll_date DATE NULL,
  PRIMARY KEY (subject_id)
);

CREATE TABLE IF NOT EXISTS aes (
  ae_id SERIAL NOT NULL,
  subject_id INT NOT NULL,
  ae_term VARCHAR(255) NULL,
  severity VARCHAR(45) NULL,
  start_date DATE NULL,
  end_date DATE NULL,
  related BOOLEAN NULL,
  PRIMARY KEY (ae_id),
  CONSTRAINT fk_aes_subjects
    FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id)
);

CREATE INDEX IF NOT EXISTS fk_aes_subjects_idx ON aes (subject_id);

CREATE TABLE IF NOT EXISTS labs (
  lab_id SERIAL NOT NULL,
  subject_id INT NOT NULL,
  visit VARCHAR(45) NULL,
  lab_test VARCHAR(45) NULL,
  value FLOAT NULL,
  units VARCHAR(45) NULL,
  normal_range VARCHAR(45) NULL,
  PRIMARY KEY (lab_id),
  CONSTRAINT fk_labs_subjects
    FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id)
);

CREATE INDEX IF NOT EXISTS fk_labs_subjects_idx ON labs (subject_id);

CREATE TABLE IF NOT EXISTS tumor_response (
  response_id SERIAL NOT NULL,
  subject_id INT NOT NULL,
  visit VARCHAR(45) NULL,
  response VARCHAR(10) NULL,
  assessed_by VARCHAR(45) NULL,
  PRIMARY KEY (response_id),
  CONSTRAINT fk_tumor_response_subjects
    FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id)
);

CREATE INDEX IF NOT EXISTS fk_tumor_response_subjects_idx ON tumor_response (subject_id);
"""

def create_database(conn):
    """Create the clinical_study_db database if it doesn't exist"""
    try:
        # Connect to default database first
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if the database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'clinical_study_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating clinical_study_db database...")
            cursor.execute("CREATE DATABASE clinical_study_db")
            print("Database created successfully!")
        else:
            print("clinical_study_db database already exists.")
            
        cursor.close()
        
        # Now reconnect to the clinical_study_db database
        conn.close()
        
        # Update environment variable
        os.environ['PGDATABASE'] = 'clinical_study_db'
        
        # Reconnect to the new database
        new_conn = create_connection()
        return new_conn
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        return conn  # Return the original connection if there was an error

def create_tables(conn):
    """Create the database tables"""
    try:
        cursor = conn.cursor()
        
        # Split the SQL into individual statements
        table_statements = [
            stmt.strip() for stmt in CREATE_TABLES_SQL.split(';')
            if stmt.strip() and not stmt.strip().startswith('CREATE DATABASE')
        ]
        
        # Execute each statement
        for stmt in table_statements:
            cursor.execute(stmt)
            
        conn.commit()
        print("Database tables created successfully!")
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()

def upload_csv_to_table(conn, file_path, table_name, columns=None):
    """
    Upload data from a CSV file to a database table using pandas and copy_from
    
    Args:
        conn: Database connection
        file_path: Path to the CSV file
        table_name: Name of the target table
        columns: List of column names (if None, use all columns from CSV)
    """
    try:
        # Read CSV file
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            return False
        
        print(f"Reading {file_path}...")
        df = pd.read_csv(file_path)
        
        # If columns are specified, use only those columns
        if columns:
            df = df[columns]
        
        # Handle date columns properly for each table
        if table_name == 'subjects':
            if 'dob' in df.columns:
                df['dob'] = pd.to_datetime(df['dob']).dt.strftime('%Y-%m-%d')
            if 'enroll_date' in df.columns:
                df['enroll_date'] = pd.to_datetime(df['enroll_date']).dt.strftime('%Y-%m-%d')
        
        if table_name == 'aes':
            if 'start_date' in df.columns:
                df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime('%Y-%m-%d')
            if 'end_date' in df.columns:
                # Handle NaN values in end_date
                df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.strftime('%Y-%m-%d')
                df['end_date'].fillna('', inplace=True)
        
        # Convert dataframe to CSV string (in-memory)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, header=False, na_rep='NULL')
        csv_buffer.seek(0)
        
        # Create a cursor and execute COPY command
        cursor = conn.cursor()
        
        # Get column names for COPY command
        columns_str = ', '.join(df.columns)
        
        # Copy data from buffer to table
        cursor.copy_expert(f"COPY {table_name} ({columns_str}) FROM STDIN WITH CSV NULL 'NULL'", csv_buffer)
        
        conn.commit()
        print(f"Successfully uploaded data to {table_name} table!")
        return True
        
    except Exception as e:
        print(f"Error uploading data to {table_name}: {e}")
        conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()

def main():
    """Main function to execute the database operations"""
    
    # Define CSV file paths with hardcoded paths
    csv_files = {
        'subjects': "E:/Dizzaroo Project/Analytic_Project/foramted_data/Subjects.csv",
        'aes': "E:/Dizzaroo Project/Analytic_Project/foramted_data/AEs.csv",
        'labs': "E:/Dizzaroo Project/Analytic_Project/foramted_data/Labs.csv",
        'tumor_response': "E:/Dizzaroo Project/Analytic_Project/foramted_data/tumer_response.csv"  # Note the spelling in original SQL
    }
    
    # Validate that files exist
    for table, file_path in csv_files.items():
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            sys.exit(1)
    
    # Connect to the default database
    conn = create_connection()
    
    # Create clinical_study_db database
    conn = create_database(conn)
    
    # Create tables
    create_tables(conn)
    
    # Upload data from CSV files to tables
    # Note: Order matters due to foreign key constraints
    
    # 1. First upload subjects table (as other tables reference it)
    upload_csv_to_table(
        conn, 
        csv_files['subjects'], 
        'subjects', 
        ['subject_id', 'site_id', 'arm', 'dob', 'gender', 'enroll_date']
    )
    
    # 2. Upload AEs table
    upload_csv_to_table(
        conn, 
        csv_files['aes'], 
        'aes', 
        ['subject_id', 'ae_term', 'severity', 'start_date', 'end_date', 'related']
    )
    
    # 3. Upload Labs table
    upload_csv_to_table(
        conn, 
        csv_files['labs'], 
        'labs', 
        ['subject_id', 'visit', 'lab_test', 'value', 'units', 'normal_range']
    )
    
    # 4. Upload Tumor Response table
    upload_csv_to_table(
        conn, 
        csv_files['tumor_response'], 
        'tumor_response', 
        ['subject_id', 'visit', 'response', 'assessed_by']
    )
    
    # Close connection
    conn.close()
    print("Database operations completed. Connection closed.")

if __name__ == "__main__":
    main()