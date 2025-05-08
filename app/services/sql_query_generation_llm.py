import replicate
from dotenv import load_dotenv
import os
load_dotenv()

# TABLE_METADATA = """"
#     I have a database designed for managing clinical trial data. Please use the following schema details and descriptions to generate accurate SQL queries.

#     **Overall Database Context:**
#     This database tracks subjects participating in a clinical trial. It includes their demographic information, assigned treatment arm, adverse events experienced, laboratory results over time, and tumor response assessments (likely for an oncology study).

#     **Table Descriptions and Key Columns:**

#     1.  **`subjects` Table:**
#         *   **Purpose:** Stores primary information about each study participant. This is the central table.
#         *   **Key Columns:**
#             *   `subject_id` (INT, PK): Unique identifier for the subject.
#             *   `site_id` (VARCHAR): Identifier for the clinical site where the subject is enrolled.
#             *   `arm` (VARCHAR): The treatment group the subject is assigned to (e.g., 'Drug X', 'Placebo', 'Standard of Care').
#             *   `dob` (DATE): Subject's date of birth.
#             *   `gender` (CHAR): Subject's gender ('F' or 'M').
#             *   `enroll_date` (DATE): Date the subject was enrolled in the study.

#     2.  **`aes` (Adverse Events) Table:**
#         *   **Purpose:** Records adverse events experienced by subjects during the trial.
#         *   **Relationship:** Linked to `subjects` via `subject_id` (Many-to-One: one subject can have many AEs).
#         *   **Key Columns:**
#             *   `ae_id` (SERIAL, PK): Unique identifier for the specific adverse event record.
#             *   `subject_id` (INT, FK): Links to the `subjects` table.
#             *   `ae_term` (VARCHAR): The name or description of the adverse event (e.g., 'Headache', 'Nausea').
#             *   `severity` (VARCHAR): The severity grade of the AE (e.g., 'Mild', 'Moderate', 'Severe', 'Life-threatening').
#             *   `start_date` (DATE): When the AE began.
#             *   `end_date` (DATE): When the AE resolved (NULL if ongoing).
#             *   `related` (BOOLEAN): Indicates if the AE is considered related to the study treatment (TRUE/FALSE).

#     3.  **`labs` Table:**
#         *   **Purpose:** Stores results from laboratory tests performed on subjects at various visits.
#         *   **Relationship:** Linked to `subjects` via `subject_id` (Many-to-One: one subject can have many lab results).
#         *   **Key Columns:**
#             *   `lab_id` (SERIAL, PK): Unique identifier for the lab result record.
#             *   `subject_id` (INT, FK): Links to the `subjects` table.
#             *   `visit` (VARCHAR): Identifier for the study visit when the lab test was done (e.g., 'Baseline', 'Week 4', 'End of Study').
#             *   `lab_test` (VARCHAR): Name of the lab test performed (e.g., 'ALT', 'Hemoglobin', 'Creatinine').
#             *   `value` (FLOAT): The numerical result of the test.
#             *   `units` (VARCHAR): The units for the measured value (e.g., 'U/L', 'g/dL', 'mg/dL').
#             *   `normal_range` (VARCHAR): The reference range for the test (e.g., '0-40', '12.0-16.0').

#     4.  **`tumor_response` Table:**
#         *   **Purpose:** Records assessments of tumor response, often using standard criteria like RECIST, at specific study visits.
#         *   **Relationship:** Linked to `subjects` via `subject_id` (Many-to-One: one subject can have many response assessments).
#         *   **Key Columns:**
#             *   `response_id` (SERIAL, PK): Unique identifier for the response assessment record.
#             *   `subject_id` (INT, FK): Links to the `subjects` table.
#             *   `visit` (VARCHAR): Identifier for the study visit when the assessment was done (e.g., 'Week 8', 'Week 16').
#             *   `response` (VARCHAR): The assessed tumor response category based on criteria like RECIST. Possible values include:
#                 *   'CR': Complete Response
#                 *   'PR': Partial Response
#                 *   'SD': Stable Disease
#                 *   'PD': Progressive Disease
#                 *   'NE': Not Evaluable
#             *   `assessed_by` (VARCHAR): Indicates who performed the assessment (e.g., 'Investigator', 'Independent Review Committee').

#     **Relationships Summary:**
#     *   The `subjects` table is the parent table.
#     *   `aes`, `labs`, and `tumor_response` are child tables, each linked back to `subjects` using the `subject_id` column. Joins between `subjects` and these tables should use `subjects.subject_id = [child_table].subject_id`.

#     **SQL Dialect:** Assume standard SQL or specify if you're using a particular dialect (e.g., PostgreSQL, MySQL, SQL Server). PostgreSQL is likely given the `SERIAL` type, but standard SQL is usually safe.

#     **Provided Schema (for reference):**
#     [Include the `CREATE TABLE` statements here as in Option 1]

#     Now, please generate an SQL query for 
# """


TABLE_METADATA = '''
    # Clinical Trial Database Schema Metadata for PostgreSQL

    ## Table: subjects
        Purpose:
        Contains demographic and enrollment information for each study participant (subject).
        Primary Key(s):
        - subject_id (INT): unique subject identifier.
        Foreign Keys:
        - None (no external references).
        Columns:
        - subject_id (INT): unique subject identifier (Primary Key).
        - site_id (VARCHAR(10)): code of clinical site where the subject is enrolled (e.g. 'US-001', 'IN-003').
        - arm (VARCHAR(45)): treatment group assignment, values include 'Standard of Care' or 'Drug X'.
        - dob (DATE): date of birth of the subject (YYYY-MM-DD).
        - gender (CHAR(1)): subject gender, values 'M' or 'F'.
        - enroll_date (DATE): date the subject was enrolled in the study (YYYY-MM-DD).
        Constraints:
        - subject_id is unique and not null (Primary Key).
        - All fields may contain NULL values except subject_id; gender in {'M','F'}; arm typically in {'Standard of Care','Drug X'}.
        Sample Data:
        - (1001, 'IN-003', 'Standard of Care', '1987-10-11', 'F', '2024-01-28')
        - (1008, 'US-002', 'Drug X', '1982-07-01', 'F', '2024-03-11')
        - (1009, 'US-001', 'Drug X', '1989-08-22', 'M', '2024-03-05')

    ## Table: aes
        Purpose:
        Records adverse events (AEs) experienced by subjects during the study, including event type, severity, dates, and relation to treatment.
        Primary Key(s):
        - ae_id (SERIAL): auto-incrementing unique identifier for each adverse event record.
        Foreign Keys:
        - subject_id references subjects(subject_id).
        Columns:
        - ae_id (SERIAL): unique identifier for each adverse event (Primary Key).
        - subject_id (INT): unique subject identifier (Foreign Key to subjects).
        - ae_term (VARCHAR(255)): description of the adverse event (e.g. 'Fatigue', 'Nausea', 'Rash', 'Neutropenia', 'Vomiting').
        - severity (VARCHAR(45)): severity of the event, values include 'Mild', 'Moderate', 'Severe', 'Life-threatening'.
        - start_date (DATE): date the adverse event started (YYYY-MM-DD).
        - end_date (DATE): date the adverse event ended or resolved (YYYY-MM-DD). NULL if ongoing.
        - related (BOOLEAN): indicator if AE is related to treatment; TRUE = related, FALSE = not related.
        Constraints:
        - Foreign key constraint ensures subject_id exists in subjects table.
        - Index created on subject_id for faster joins.
        Sample Data:
        - (1, 1001, 'Neutropenia', 'Mild', '2024-02-12', '2024-02-16', TRUE)
        - (2, 1004, 'Rash', 'Severe', '2024-02-23', '2024-03-01', TRUE)
        - (3, 1006, 'Nausea', 'Moderate', '2024-02-11', '2024-02-20', FALSE)

    ## Table: labs
        Purpose:
        Stores laboratory test results for subjects at various visits, including test name, measured value, and reference range.
        Primary Key(s):
        - lab_id (SERIAL): auto-incrementing unique identifier for each lab result.
        Foreign Keys:
        - subject_id references subjects(subject_id).
        Columns:
        - lab_id (SERIAL): unique identifier for each lab result (Primary Key).
        - subject_id (INT): unique subject identifier (Foreign Key to subjects).
        - visit (VARCHAR(45)): visit identifier during treatment, e.g. 'Baseline', 'Week 1', 'Cycle 1 Day 1', 'Cycle 4 Day 15'.
        - lab_test (VARCHAR(45)): name of laboratory test, values include 'ALT', 'AST', 'WBC', 'Hemoglobin', 'CA 15-3'.
        - value (FLOAT): numeric result of the laboratory test.
        - units (VARCHAR(45)): measurement units for the test, values include 'U/L' or 'g/dL'.
        - normal_range (VARCHAR(45)): normal reference range for the test value (e.g. '0-40' for ALT/AST/WBC/CA 15-3; '12-16' for Hemoglobin).
        Constraints:
        - Foreign key constraint ensures subject_id exists in subjects table.
        - Index created on subject_id for faster joins.
        Sample Data:
        - (1, 1001, 'Cycle 4 Day 15', 'ALT', 11.75, 'U/L', '0-40')
        - (2, 1002, 'Cycle 3 Day 15', 'Hemoglobin', 14.86, 'g/dL', '12-16')
        - (3, 1003, 'Cycle 1 Day 15', 'CA 15-3', 5.22, 'U/L', '0-40')

    ## Table: tumor_response
        Purpose:
        Contains tumor response evaluations for subjects at scheduled assessment visits, capturing response category and assessor.
        Primary Key(s):
        - response_id (SERIAL): auto-incrementing unique identifier for each response assessment.
        Foreign Keys:
        - subject_id references subjects(subject_id).
        Columns:
        - response_id (SERIAL): unique identifier for each response assessment (Primary Key).
        - subject_id (INT): unique subject identifier (Foreign Key to subjects).
        - visit (VARCHAR(45)): scheduled visit identifier, values include 'Week 6', 'Week 12', 'Week 18'.
        - response (VARCHAR(10)): tumor response outcome at visit, values include 'PD' (progressive disease), 'CR' (complete response), 'SD' (stable disease), 'PR' (partial response), 'NE' (not evaluable).
        - assessed_by (VARCHAR(45)): who assessed the response, values 'Investigator' or 'Independent'.
        Constraints:
        - Foreign key constraint ensures subject_id exists in subjects table.
        - Index created on subject_id for faster joins.
        Sample Data:
        - (1, 1001, 'Week 6', 'PD', 'Investigator')
        - (2, 1002, 'Week 12', 'PR', 'Independent')
        - (3, 1003, 'Week 18', 'CR', 'Independent')

    ## PostgreSQL Implementation Notes:
    - Database uses PostgreSQL syntax and data types
    - SERIAL type is used for auto-incrementing primary keys
    - Boolean values are represented as TRUE/FALSE (not 1/0)
    - Text comparisons are case-sensitive by default (use ILIKE for case-insensitive)
    - Date format follows ISO standard: 'YYYY-MM-DD'
    - Indexing is implemented on foreign keys for query optimization
    - NULL values are allowed in most fields except primary keys

    ## Common Relationships:
    - One subject can have multiple adverse events (1:Many relationship between subjects and aes)
    - One subject can have multiple lab results (1:Many relationship between subjects and labs)
    - One subject can have multiple tumor response assessments (1:Many relationship between subjects and tumor_response)

    ## Important Join Conditions:
    - subjects.subject_id = aes.subject_id
    - subjects.subject_id = labs.subject_id
    - subjects.subject_id = tumor_response.subject_id

    ## PostgreSQL-Specific Query Considerations:
    - Use double quotes for identifiers only when necessary (e.g., mixed case or reserved words)
    - Use single quotes for string literals
    - Date literals should be formatted as 'YYYY-MM-DD'
    - For text pattern matching, use LIKE or ILIKE (case insensitive)
    - For advanced date operations, use PostgreSQL's date functions (e.g., AGE(), EXTRACT())
    - For aggregations, consider using GROUP BY with HAVING clauses
    - PostgreSQL supports DISTINCT ON for getting unique rows based on specific columns
    - When ordering results, NULL values appear last by default in ascending order

    ## Response Code Meanings:
    - CR: Complete Response (complete disappearance of all target lesions)
    - PR: Partial Response (at least 30% decrease in the sum of diameters of target lesions)
    - SD: Stable Disease (neither sufficient shrinkage to qualify for PR nor sufficient increase to qualify for PD)
    - PD: Progressive Disease (at least 20% increase in the sum of diameters of target lesions)
    - NE: Not Evaluable (assessment could not be performed)
'''

SYSTEM_INTRUCTION = """
    **System Instructions for SQL Generation:**

    1.  **Role:** Act as an expert SQL developer specialized in querying clinical trial databases.
    2.  **Primary Goal:** Generate **one single line** of accurate, efficient, and syntactically correct SQL query based on the provided database schema and the user's natural language request.
    3.  **Schema Adherence:**
        *   You MUST strictly adhere to the table and column names provided in the schema definition. Do not invent or assume table/column names. Case sensitivity might matter depending on the database; use the exact casing from the schema.
        *   Pay close attention to data types (INT, VARCHAR, DATE, BOOLEAN, FLOAT, SERIAL) for correct syntax in WHERE clauses and operations.
    4.  **Relationships:**
        *   Recognize standard joins between `subjects` and `aes`, `labs`, `tumor_response` using `subject_id`. Use correct JOIN conditions: `subjects.subject_id = [other_table].subject_id`.
    5.  **Data Interpretation:**
        *   Understand column meanings from names/comments (e.g., `arm`=treatment, `response` codes='CR','PR', etc.).
        *   Interpret boolean `related` column in `aes` as 1=TRUE, 0=FALSE (use `WHERE related = 1` or `WHERE related = 0`).
        *   Handle dates in 'YYYY-MM-DD' format.
        *   Recognize specific codes: `gender` ('F', 'M'), `response` ('CR', 'PR', 'SD', 'PD', 'NE').
    6.  **Query Construction:**
        *   Select only requested columns. Avoid `*` unless necessary.
        *   Apply WHERE clauses accurately. Use `=` for exact matches on strings unless the request implies pattern matching (like "contains" or "starts with", in which case use `LIKE` or `ILIKE` appropriately).
        *   Use aggregation (COUNT, AVG, etc.) with GROUP BY correctly when requested.
        *   Generate standard SQL syntax, assuming PostgreSQL dialect due to `SERIAL` type unless specified otherwise.
    7.  **Ambiguity Handling:** If the user's query is ambiguous, ask for clarification. Do NOT guess if critical details are missing.
    8.  **CRITICAL OUTPUT FORMAT:**
        *   **You MUST output ONLY the raw SQL query string.**
        *   **The entire SQL query MUST be on a single line.**
        *   **There should be NO markdown formatting (like `SELECT ... `).**
        *   **There should be NO introductory text, explanations, or comments before or after the SQL query.**
        *   **There should be NO newline characters within the generated SQL string.**

    **Example Interaction:**

    *   **User Provides:** Schema + Natural Language Query: "Show me all subjects enrolled in the Drug X treatment arm."
    *   **Your REQUIRED Output:** `SELECT subject_id FROM subjects WHERE arm = 'Drug X';`

        *(Note: The output above is exactly what you should return - just the SQL text on one line, nothing else.)*

    **Context to be Provided by User:**
    *   The database schema (`CREATE TABLE` statements).
    *   The natural language query.

    By following these instructions precisely, especially rule #8, you will generate SQL suitable for direct execution.
"""




async def generate_sql_query_by_sqlCoder(prompt):

    try:
        output = replicate.run(
            "nateraw/defog-sqlcoder-7b-2:ced935b577fb52644d933f77e2ff8902744e4c58a2f50023b3a1db80b7a75806",
            input={
                "top_k": 50,
                "top_p": 0.9,
                "question": prompt,
                "temperature": 0,
                "max_new_tokens": 512,
                "table_metadata": TABLE_METADATA,
                # "table_metadata": "-- PostgreSQL Clinical Study Database Schema Metadata\n-- Database: clinical_study_db\n\n/*\nSCHEMA OVERVIEW:\nThis database stores clinical trial data including subject demographics, adverse events,\nlaboratory results, and tumor response assessments using RECIST criteria.\n\nENTITY RELATIONSHIPS:\n1. One-to-Many: A single subject can have multiple adverse events\n   subjects(subject_id) ----< aes(subject_id)\n\n2. One-to-Many: A single subject can have multiple lab results \n   subjects(subject_id) ----< labs(subject_id)\n\n3. One-to-Many: A single subject can have multiple tumor response assessments\n   subjects(subject_id) ----< tumor_response(subject_id)\n\nIMPORTANT NOTE ON POSTGRESQL CASE INSENSITIVITY:\n- This schema uses unquoted identifiers which PostgreSQL converts to lowercase\n- All table and column names will be treated as lowercase during queries\n- This means 'Subject_ID', 'SUBJECT_ID', and 'subject_id' are all equivalent\n- For consistency, it's recommended to use lowercase in all queries\n*/\n\n-- Table: subjects\n-- Stores subject demographic and enrollment information\n-- This is the primary entity table with relationships to all other tables\nCREATE TABLE IF NOT EXISTS subjects (\n  subject_id INT NOT NULL,           -- Unique identifier for each subject\n  site_id VARCHAR(10) NULL,          -- Clinical site identifier\n  arm VARCHAR(45) NULL,              -- Treatment arm (e.g., 'Drug X', 'Standard of Care')\n  dob DATE NULL,                     -- Date of birth\n  gender CHAR(1) NULL,               -- Gender ('F', 'M')\n  enroll_date DATE NULL,             -- Study enrollment date\n  PRIMARY KEY (subject_id)\n);\n\n-- Table: aes\n-- Stores Adverse Event information for subjects\n-- Relationship: Many adverse events can belong to one subject (Many-to-One)\nCREATE TABLE IF NOT EXISTS aes (\n  ae_id SERIAL NOT NULL,             -- Unique identifier for each adverse event\n  subject_id INT NOT NULL,           -- Foreign key to subjects.subject_id\n  ae_term VARCHAR(255) NULL,         -- Description of the adverse event\n  severity VARCHAR(45) NULL,         -- Severity ('Mild', 'Moderate', 'Severe', 'Life-threatening')\n  start_date DATE NULL,              -- Date when adverse event started\n  end_date DATE NULL,                -- Date when adverse event ended (NULL if ongoing)\n  related BOOLEAN NULL,              -- Whether related to treatment (TRUE/FALSE)\n  PRIMARY KEY (ae_id),\n  CONSTRAINT fk_aes_subjects\n    FOREIGN KEY (subject_id)\n    REFERENCES subjects (subject_id)\n);\n\nCREATE INDEX fk_aes_subjects_idx ON aes (subject_id);\n\n-- Table: labs\n-- Stores laboratory test results for subjects\n-- Relationship: Many lab results can belong to one subject (Many-to-One)\nCREATE TABLE IF NOT EXISTS labs (\n  lab_id SERIAL NOT NULL,            -- Unique identifier for each lab result\n  subject_id INT NOT NULL,           -- Foreign key to subjects.subject_id\n  visit VARCHAR(45) NULL,            -- Visit identifier (e.g., 'Baseline', 'Week 1')\n  lab_test VARCHAR(45) NULL,         -- Type of lab test (e.g., 'Hemoglobin', 'WBC', 'ALT')\n  value FLOAT NULL,                  -- Measured value\n  units VARCHAR(45) NULL,            -- Units of measurement (e.g., 'g/dL', 'U/L')\n  normal_range VARCHAR(45) NULL,     -- Reference range (e.g., '12-16', '0-40')\n  PRIMARY KEY (lab_id),\n  CONSTRAINT fk_labs_subjects\n    FOREIGN KEY (subject_id)\n    REFERENCES subjects (subject_id)\n);\n\nCREATE INDEX fk_labs_subjects_idx ON labs (subject_id);\n\n-- Table: tumor_response\n-- Stores tumor response assessments (RECIST) for subjects\n-- Relationship: Many tumor responses can belong to one subject (Many-to-One)\nCREATE TABLE IF NOT EXISTS tumor_response (\n  response_id SERIAL NOT NULL,       -- Unique identifier for each response assessment\n  subject_id INT NOT NULL,           -- Foreign key to subjects.subject_id\n  visit VARCHAR(45) NULL,            -- Visit identifier (e.g., 'Week 8', 'Week 16')\n  response VARCHAR(10) NULL,         -- RECIST response ('CR', 'PR', 'SD', 'PD', 'NE')\n                                     -- CR=Complete Response, PR=Partial Response\n                                     -- SD=Stable Disease, PD=Progressive Disease, NE=Not Evaluable\n  assessed_by VARCHAR(45) NULL,      -- Who assessed ('Investigator', 'Independent')\n  PRIMARY KEY (response_id),\n  CONSTRAINT fk_tumor_response_subjects\n    FOREIGN KEY (subject_id)\n    REFERENCES subjects (subject_id)\n);\n\nCREATE INDEX fk_tumor_response_subjects_idx ON tumor_response (subject_id);\n",
                "prompt_template": "### Task\nGenerate a SQL query to answer [QUESTION]{question}[/QUESTION]\n\n### Instructions\n- If you cannot answer the question with the available database schema, return 'I do not know'\n\n### Database Schema\nThe query will run on a database with the following schema:\n{table_metadata}\n\n### Answer\nGiven the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]\n[SQL]",
                "presence_penalty": 0,
                "frequency_penalty": 0
            }
        )

        # Collect all output from the generator
        sql_query = ""
        for item in output:
            sql_query += item

        return sql_query
            
    except Exception as e:
        print('Error calling the API:')
        raise e








from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=api_key)

async def generate_sql_query_by_gemini(prompt):

    prompt = TABLE_METADATA+ " \n Natural Language Query : " +prompt

    try:
        response = gemini_client.models.generate_content(
            model="models/gemini-2.5-flash-preview-04-17", 
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INTRUCTION,
                temperature=0,
            )
        )
        
        print(response.text)     
        return response.text
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }












from openai import OpenAI
openai_client = OpenAI()


async def generate_sql_query_by_openai(prompt):

    prompt = TABLE_METADATA+ " \n Natural Language Query : " +prompt
    try:
        
        response = openai_client.responses.create(
            model="gpt-4.1",
            instructions=SYSTEM_INTRUCTION,
            input=prompt,
            temperature=0
        )

        print(response.output_text)
        return response.output_text
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }






# # Example usage
# if __name__ == "__main__":
#     try:
#         print('Starting SQL query generation...')
#         sql = generate_sql("Get the top 5 customers by purchase amount in the last 30 days")
        
#         print('\nSuccessfully generated SQL:')
#         print(sql)
#     except Exception as err:
#         print('\nFailed to generate SQL:', str(err))