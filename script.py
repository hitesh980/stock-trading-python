import requests
import csv
import os
import time
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
LIMIT = 1000


SF_USER = os.getenv("SF_USER")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_ACCOUNT = os.getenv("SF_ACCOUNT")
SF_WAREHOUSE = os.getenv("SF_WAREHOUSE")
SF_DATABASE = os.getenv("SF_DATABASE")
SF_SCHEMA = os.getenv("SF_SCHEMA")
# default to your table name if env var not set
SF_TABLE = os.getenv("SF_TABLE", "stock_tickers")

# Target schema (types used when creating table if missing)
TARGET_SCHEMA = {
    'ticker': 'VARCHAR',
    'name': 'VARCHAR',
    'market': 'VARCHAR',
    'locale': 'VARCHAR',
    'primary_exchange': 'VARCHAR',
    'type': 'VARCHAR',
    'active': 'BOOLEAN',
    'currency_name': 'VARCHAR',
    'cik': 'VARCHAR',
    'composite_figi': 'VARCHAR',
    'share_class_figi': 'VARCHAR',
    'last_updated_utc': 'TIMESTAMP_NTZ',
    'ds': 'VARCHAR'
}


def run_stock_job():
    tickers = []

    url = (
        "https://api.polygon.io/v3/reference/tickers"
        f"?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker"
        f"&apiKey={POLYGON_API_KEY}"
    )

    while url:
        print(f"Requesting: {url}")
        response = requests.get(url)

        try:
            data = response.json()
        except ValueError:
            print("Invalid JSON response:", response.text)
            break

        #
        if data.get("status") != "OK":
            print("Polygon API Error:", data.get("error"))
            break

        results = data.get("results", [])
        if not results:
            print("No results found on this page")
            break

        tickers.extend(results)

        # Pagination
        url = data.get("next_url")
        if url:
            url += f"&apiKey={POLYGON_API_KEY}"
            time.sleep(15)  

    write_to_snowflake(tickers)
    print(f"Wrote {len(tickers)} rows to Snowflake table {SF_TABLE}")


def write_to_snowflake(tickers):
    if not tickers:
        print("No tickers to write")
        return

    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=SF_USER,
            password=SF_PASSWORD,
            account=SF_ACCOUNT,
            warehouse=SF_WAREHOUSE,
            database=SF_DATABASE,
            schema=SF_SCHEMA
        )
        cursor = conn.cursor()
        print("Connected to Snowflake successfully")

        # Ensure table exists with expected schema; create if missing
        cols_order = list(TARGET_SCHEMA.keys())
        # Build CREATE TABLE statement using TARGET_SCHEMA
        columns_sql = ", ".join([f"{col.upper()} {TARGET_SCHEMA[col]}" for col in cols_order])
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {SF_TABLE} ({columns_sql})"
        cursor.execute(create_table_sql)
        print(f"Table {SF_TABLE} created/verified or already exists")

        # Prepare insert statement with placeholders
        insert_cols = ", ".join([c.upper() for c in cols_order])
        placeholders = ", ".join(["%s" for _ in cols_order])
        insert_sql = f"INSERT INTO {SF_TABLE} ({insert_cols}) VALUES ({placeholders})"

        # Build rows respecting column order and add todays date
        from datetime import date
        ds_value = date.today().isoformat()
        rows = []
        for t in tickers:
            row = []
            for col in cols_order:
                if col == 'ds':
                    row.append(ds_value)
                    continue
               
                val = t.get(col)
               
                if isinstance(val, str) and val.lower() in ("true", "false"):
                    val = val.lower() == "true"
                row.append(val)
            rows.append(tuple(row))

        # Execute in batch
        if rows:
            cursor.executemany(insert_sql, rows)
            conn.commit()
            print(f"Successfully inserted {len(rows)} rows into {SF_TABLE}")

        cursor.close()
        conn.close()
        print("Connection closed")

    except Exception as e:
        print(f"Snowflake error: {e}")
        raise


if __name__ == "__main__":
    run_stock_job()
