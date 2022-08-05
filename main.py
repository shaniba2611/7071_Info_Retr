
import schedule
import time
import datetime
from Crawling import crawling
def run_crawler():
    date = datetime.datetime.now()
    print(f"\t\tRunning Crawler at: {date.day}/{date.month}/{date.year} ({date.hour}:{date.minute})\n")
    crawling()

schedule.every().sunday.at("7:00").do(run_crawler)


while True:
    schedule.run_pending()
    time.sleep(1)
