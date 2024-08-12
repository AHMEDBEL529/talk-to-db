import mysql.connector
from mysql.connector import Error
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
import os

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
# Initialize Azure OpenAI client
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",  # Your deployment name
    api_version="2023-06-01-preview",  # Your API version
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# Get the database host from user input
db_host = os.getenv("DB_HOST")
db_port = 3306
db_user = 'admin'
db_password = 'your-custom-password'  # Replace with your actual password
db_name = 'testdb'  # Replace with your actual database name

# Connect to the database
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# Get the schema of all tables in the database
def get_schema(connection):
    schema_info = {}
    cursor = connection.cursor()
    # Query to get all tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"DESCRIBE {table_name}")
        schema_info[table_name] = cursor.fetchall()

    return schema_info

# Generate SQL query from natural language using LangChain
def generate_sql_query(natural_language_query, schema):
    # Convert schema information to a human-readable format
    schema_description = "\n".join(
        [f"Table '{table}':\n" + "\n".join([f"- {col[0]} {col[1]}" for col in columns])
         for table, columns in schema.items()]
    )

    prompt = PromptTemplate(
        input_variables=["schema", "query"],
        template=f"{schema_description}\n\nConvert the following natural language query to an SQL query with appropriate names for the output columns. Provide only the SQL query without any explanation:\n{{query}}"
    )
    response = (prompt | llm).invoke({"schema": schema_description, "query": natural_language_query})
    sql_query = response.content.replace('```sql', '').replace('```', '').strip()
    return sql_query

# Execute SQL query and retrieve results
def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)

        # Handle SELECT queries
        if query.strip().lower().startswith('select'):
            columns = [desc[0] for desc in cursor.description]  # Get column names
            rows = cursor.fetchall()
            return columns, rows
        else:
            connection.commit()  # Commit changes for non-SELECT queries
            cursor.close()  # Close the cursor for non-SELECT queries
            return [], []  # No columns or rows to return for non-SELECT queries
    except Error as e:
        print("Error executing query:", e)
        return [], []

# Main function to handle the workflow
def query_database(natural_language_query):
    connection = connect_to_db()
    if connection:
        schema = get_schema(connection)
        sql_query = generate_sql_query(natural_language_query, schema)
        print(f"Generated SQL Query:\n {sql_query}")  # Debug print to check the generated SQL query
        columns, results = execute_query(connection, sql_query)
        connection.close()
        return columns, results
    else:
        return [], []

# Example usage
natural_language_query = """Find the total amount spent by each user.
                            Only include users who have spent more than $200.
                            List users with their total spending and the count of orders they made."""

columns, results = query_database(natural_language_query)

# Convert to pandas DataFrame
if results:
    df = pd.DataFrame(results, columns=columns)
    print(df)
else:
    print("No results returned or query execution failed.")
