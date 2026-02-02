import schedule
import time
from collector import collect_data

schedule.every(6).hours.do(collect_data)

print("Scheduler started. Will run data collection every 6 hours.")
print("Running initial collection...")
collect_data()

print("Waiting for next scheduled run...")
while True:
    schedule.run_pending()
    time.sleep(60)
