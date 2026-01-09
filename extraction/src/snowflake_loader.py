import os
import json
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
from typing import List, Dict, Any

class SnowflakeLoader:
    def __init__(self):
        # Retrieve credentials from environment variables
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")

        if not all([self.user, self.password, self.account]):
            raise ValueError("Missing Snowflake credentials in .env file.")

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
        """
        Loads a list of issues into Snowflake using the write_pandas method for performance.
        Strategy:
        1. Convert list of dicts to a Pandas DataFrame.
        2. Upload DataFrame to a temporary staging table in Snowflake.
        3. Execute a MERGE command to upsert data from stage to the final table.
        """
        if not issues:
            print("No issues to load.")
            return

        print(f"Preparing bulk load for {len(issues)} records...")
        
        # 1. Convert to Pandas DataFrame (In-Memory)
        # Prepare data to match the target table structure
        data_for_df = []
        for issue in issues:
            data_for_df.append({
                'ISSUE_ID': str(issue.get('id')),
                'REPO_NAME': issue.get('repository_url', '').split('/')[-1],
                'PAYLOAD': json.dumps(issue) # Serialize dict to JSON string
            })
            
        df = pd.DataFrame(data_for_df)
        
        # Snowflake expects uppercase column names for automatic mapping
        df.columns = ['ISSUE_ID', 'REPO_NAME', 'PAYLOAD']

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # 2. Create Temporary Staging Table
            # A temporary table exists only for the duration of the session
            print("   -> Creating temporary staging table...")
            cursor.execute("CREATE TEMPORARY TABLE IF NOT EXISTS raw.temp_issues_staging LIKE raw.github_issues")
            cursor.execute("TRUNCATE TABLE raw.temp_issues_staging") 
            
            # 3. Bulk Upload
            # write_pandas uses Parquet format under the hood, offering high performance
            print("   -> Uploading data to Snowflake (Bulk Load)...")
            write_pandas(
                conn, 
                df, 
                table_name='TEMP_ISSUES_STAGING', 
                database=self.database, 
                schema=self.schema,
                quote_identifiers=False # Essential for matching uppercase column names
            )
            
            # 4. Execute Merge (Upsert)
            # Move data from temporary table to final table, handling duplicates
            print("   -> Executing final MERGE operation...")
            query_merge = """
            MERGE INTO raw.github_issues AS target
            USING raw.temp_issues_staging AS source
            ON target.issue_id = source.issue_id
            WHEN MATCHED THEN
                UPDATE SET payload = source.payload, ingested_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (issue_id, repo_name, payload) VALUES (source.issue_id, source.repo_name, source.payload)
            """
            cursor.execute(query_merge)
            
            conn.commit()
            print(f"Load completed successfully: {len(issues)} records processed via bulk load.")
            
        except Exception as e:
            print(f"Error loading data to Snowflake: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Local integration test
    loader = SnowflakeLoader()
    print("Loader initialized successfully.")