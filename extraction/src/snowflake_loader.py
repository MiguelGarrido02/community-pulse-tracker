import os
import json
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
from typing import List, Dict, Any

class SnowflakeLoader:
    def __init__(self):
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")

        if not all([self.user, self.password, self.account]):
            raise ValueError("Snowflake credentials are not fully set in environment variables.")
        
    def get_connection(self):
        return snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema
        )
    
    def load_data(self, issues: List[Dict[str, Any]]):
        """"
        Load a list of issues (dicts) in the table RAW.GITHUB_ISSUES
        """
        if not issues:
            print("No issues to load.")
            return
        
        print("Getting ready to load "+ str(len(issues)) + " issues into Snowflake...")

        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            # Transform list of dicts into list of tuples
            # Insert the full JSON in the column "payload"
            data_to_insert = []
            for issue in issues:
                issue_id = str(issue.get("id"))
                repo_name = issue.get('repository_url', '').split('/')[-1]
                json_str = json.dumps(issue) #dict to json string

                data_to_insert.append((issue_id, repo_name, json_str))

            # Execute inset --> we use PARSE_JSON so string is natively converted to VARIANT
            query = """
            MERGE INTO raw.github_issues AS target
            USING (SELECT %s AS id, %s AS repo, PARSE_JSON(%s) AS payload) AS source
            ON target.issue_id = source.id
            WHEN MATCHED THEN 
                UPDATE SET payload = source.payload, ingested_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (issue_id, repo_name, payload) VALUES (source.id, source.repo, source.payload)
            """
            cursor.executemany(query, data_to_insert)
            conn.commit()
            print(f"Successfully loaded {cursor.rowcount} records into Snowflake.")
        except Exception as e:
            print("Error loading data into Snowflake:", e)
            raise e
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Datos falsos de prueba
    mock_issues = [
        {"id": 12345, "title": "Test Issue", "repository_url": "api/pandas", "body": "This is a test"}
    ]
    
    loader = SnowflakeLoader()
    loader.load_data(mock_issues)