from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import Profile
from .scheduler import scheduler
from .utils import calculate_final_score

# this is for the case when user changes their morning_time
@receiver(post_save, sender=Profile)
def reschedule_on_profile_change(sender, instance, **kwargs):
  
  profile = instance
  user = profile.user

  # reschele for updated time
  if profile.morning_time and profile.timezone:
    print(f"Profile saved for {user.username}. Rescheduling job...")

    scheduler.add_job(
        calculate_final_score,
        "cron",
        hour=profile.morning_time.hour,
        minute=profile.morning_time.minute,
        timezone=profile.timezone,
        args=[user],
        id=f"calculate_score_{user.id}",
        replace_existing=True
    )