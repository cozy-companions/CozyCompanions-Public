# your_app/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import schedule_all_user_scores

scheduler = BackgroundScheduler()

def start():
    scheduler.start()
    # schedule tasks to calculate scores
    print("Scheduler started... Scheduling jobs.")
    schedule_all_user_scores(scheduler)
    
    print("--- Scheduled Jobs ---")
    for job in scheduler.get_jobs():
        print(f"Job ID: {job.id}, Next Run: {job.next_run_time}")
    print("----------------------")