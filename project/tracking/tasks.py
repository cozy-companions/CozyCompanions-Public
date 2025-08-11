# your_app/tasks.py

from django.contrib.auth.models import User
from user.models import Profile
from .utils import calculate_final_score

# function called by scheduler
def schedule_all_user_scores(scheduler):
    """
    Schedules a recurring daily job for each user to calculate their final score
    at their specified morning_time.
    """
    
    for user in User.objects.all():
        try:
            profile = user.profile
            if profile.morning_time:
                scheduler.add_job(
                    calculate_final_score,
                    "cron",
                    hour=profile.morning_time.hour,
                    minute=profile.morning_time.minute,
                    timezone= profile.timezone,
                    args=[user],
                    id=f"calculate_score_{user.id}",
                    replace_existing=True
                )
        except Profile.DoesNotExist:
            continue