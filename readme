# Stock Trading Python App

A Python application that automatically fetches stock ticker data from the Polygon API and syncs it to Snowflake data warehouse on a daily schedule.

## Overview

This project integrates with the Polygon API to retrieve comprehensive stock ticker information and stores it in Snowflake for data analysis and reporting. The application runs on a scheduled basis, automatically syncing stock data every day at 9:00 AM.

## Features

- **Automated Data Fetching**: Retrieves stock ticker data from Polygon API with pagination support
- **Daily Scheduling**: Uses the `schedule` library to run data sync jobs at specified times
- **Snowflake Integration**: Automatically creates and populates tables in Snowflake data warehouse
- **Environment Configuration**: Uses `.env` files for secure credential management
- **Error Handling**: Robust error handling with logging for failed sync operations
- **Large-Scale Data Processing**: Handles up to 1000 records per API call with pagination support

## Prerequisites

- Python 3.7+
- Polygon API key (get from https://polygon.io)
- Snowflake account with warehouse and database access
- Virtual environment (recommended)

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd stock-trading-python-app
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv pythonenv
   source pythonenv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```
   POLYGON_API_KEY=your_polygon_api_key
   SF_USER=your_snowflake_user
   SF_PASSWORD=your_snowflake_password
   SF_ACCOUNT=your_snowflake_account
   SF_WAREHOUSE=your_warehouse_name
   SF_DATABASE=your_database_name
   SF_SCHEMA=your_schema_name
   SF_TABLE=stock_tickers  # Optional, defaults to 'stock_tickers'
   ```

## Project Structure

```
stock-trading-python-app/
├── script.py              # Main data fetching and Snowflake sync logic
├── scheduler.py           # Daily job scheduler
├── requirements.txt       # Python dependencies
├── tickers.csv            # Local CSV file for ticker data (optional)
├── pythonenv/             # Virtual environment directory
└── readme                 # This file
```

## Usage

### Running the Scheduler

Start the daily scheduler that runs stock data sync at 9:00 AM:
```bash
source pythonenv/bin/activate
python scheduler.py
```

The scheduler will:
- Start and display a confirmation message
- Check for pending jobs every 60 seconds
- Execute `run_stock_job()` at 9:00 AM daily
- Log success/failure messages

### Running the Data Sync Manually

To manually run the stock data sync without waiting for the scheduler:
```bash
source pythonenv/bin/activate
python -c "from script import run_stock_job; run_stock_job()"
```

## Configuration

### Polygon API
- Fetches active stock tickers from the market
- Limit: 1000 records per request
- Handles pagination automatically

### Snowflake Connection
The application automatically:
- Creates the target table if it doesn't exist
- Defines the schema with appropriate column types
- Inserts/updates stock ticker records

**Target Schema**:
- `ticker`: Stock ticker symbol
- `name`: Company name
- `market`: Market type
- `locale`: Locale identifier
- `primary_exchange`: Primary exchange
- `type`: Ticker type
- `active`: Active status (boolean)
- `currency_name`: Currency name
- `cik`: CIK number
- `composite_figi`: Composite FIGI
- `share_class_figi`: Share class FIGI
- `last_updated_utc`: Last update timestamp
- `ds`: Data sync timestamp

## Dependencies

- **requests**: HTTP library for API calls
- **snowflake-connector-python**: Snowflake database connector
- **schedule**: Job scheduling library
- **python-dotenv**: Environment variable management

See `requirements.txt` for specific versions.

## Snowflake Access

Access your Snowflake instance at:
https://app.snowflake.com/us-east-1/mlc85498/#/homepage

## Error Handling

The scheduler includes error handling that:
- Catches exceptions during data sync
- Logs error messages with timestamps
- Continues running to attempt next scheduled sync

Example error log:
```
Stock data sync failed at 2026-01-03 09:00:15: [error message]
```

## Known Issues & Solutions

### 1. Polygon API Rate Limiting
**Error**: `HTTP 429 - Too Many Requests`

**Solution**:
- Polygon API has rate limits based on your subscription plan
- Implement exponential backoff retry logic
- Add delays between API requests:
  ```python
  import time
  time.sleep(1)  # Add 1-second delay between requests
  ```
- Consider caching results locally in `tickers.csv` to reduce API calls

### 2. Snowflake Connection Timeout
**Error**: `snowflake.connector.errors.ProgrammingError: Connection timeout`

**Solution**:
- Verify Snowflake credentials are correct in `.env`
- Check your IP is whitelisted in Snowflake security settings
- Ensure warehouse is active (not suspended)
- Verify network connectivity to Snowflake endpoints
- Increase connection timeout:
  ```python
  conn = snowflake.connector.connect(
      user=SF_USER,
      password=SF_PASSWORD,
      account=SF_ACCOUNT,
      warehouse=SF_WAREHOUSE,
      connect_timeout=30  # Increase timeout
  )
  ```

### 3. Missing Environment Variables
**Error**: `KeyError: 'POLYGON_API_KEY' or similar`

**Solution**:
- Ensure `.env` file exists in the project root
- Verify all required variables are set:
  ```
  POLYGON_API_KEY
  SF_USER
  SF_PASSWORD
  SF_ACCOUNT
  SF_WAREHOUSE
  SF_DATABASE
  SF_SCHEMA
  SF_TABLE (optional)
  ```
- Reload environment after creating `.env`:
  ```bash
  source pythonenv/bin/activate
  ```

### 4. Scheduler Not Running at Expected Time
**Error**: Job doesn't execute at 9:00 AM

**Solution**:
- Ensure system time is correct: `date`
- Scheduler uses local machine time, not UTC
- Verify scheduler process is running:
  ```bash
  ps aux | grep scheduler.py
  ```
- Keep the terminal/process running in background with screen or nohup:
  ```bash
  nohup python scheduler.py > scheduler.log 2>&1 &
  ```

### 5. Duplicate Records in Snowflake
**Error**: Multiple copies of the same ticker in database

**Solution**:
- Add primary key constraint or unique index on ticker column
- Use `INSERT OR REPLACE` or `MERGE` logic instead of pure INSERT
- Clear table before full sync (if acceptable):
  ```sql
  DELETE FROM stock_tickers;
  ```

### 6. CSV File Not Found
**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'tickers.csv'`

**Solution**:
- Ensure `tickers.csv` exists in project root
- Or make CSV optional in code with error handling:
  ```python
  if os.path.exists('tickers.csv'):
      # Process CSV
  ```

### 7. Snowflake Warehouse Suspended
**Error**: `Object does not exist or not authorized`

**Solution**:
- Resume warehouse from Snowflake console
- Or resume programmatically before queries:
  ```sql
  ALTER WAREHOUSE warehouse_name RESUME;
  ```

### 8. Memory Issues with Large Data Sets
**Error**: `MemoryError` when processing large pagination

**Solution**:
- Reduce LIMIT from 1000 to smaller batch size (e.g., 100)
- Process and insert data in batches instead of loading all at once
- Use generator patterns for pagination

### 9. SSL Certificate Verification Error
**Error**: `ssl.SSLError` or certificate verification failed

**Solution**:
- Update certificates:
  ```bash
  pip install --upgrade certifi
  ```
- For development only (not recommended for production):
  ```python
  import urllib3
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  requests.get(url, verify=False)
  ```

### 10. Package Import Errors
**Error**: `ModuleNotFoundError: No module named 'snowflake'`

**Solution**:
- Activate virtual environment: `source pythonenv/bin/activate`
- Reinstall dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Verify installation:
  ```bash
  pip list
  ```

## Troubleshooting

1. **API Key Error**: Verify `POLYGON_API_KEY` is correct and active
2. **Snowflake Connection Failed**: Check all SF_* environment variables
3. **Schedule Not Running**: Ensure the scheduler process is still running
4. **Data Not Syncing**: Check logs for API rate limits or Snowflake quota issues

## License

This project is for internal use.

## Support

For issues or questions, contact your administrator or check the Snowflake console for job history and logs.