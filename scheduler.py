import schedule
import time
from script import run_stock_job

from datetime import datetime

def basic_job():
    print("Job started at:", datetime.now())


def scheduled_stock_job():
    print(f" Stock data sync started at {datetime.now()}")
    try:
        run_stock_job()
        print(f"Stock data sync completed at {datetime.now()}")
    except Exception as e:
        print(f" Stock data sync failed at {datetime.now()}: {e}")


# Schedule stock job to run every day at 9:00 AM
schedule.every().day.at("09:00").do(scheduled_stock_job)

print(" Scheduler started. Stock data will be synced daily at 09:00 AM")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every 60 seconds