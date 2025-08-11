from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
import json
# Create your models here.
# to prevent large file sizes
MAX_JSON_CHAR_LENGTH = 1000

def default_hobbies():
    return {}

      
class Profile(models.Model):
  user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    primary_key=True,
  )

  profile_pic = models.ImageField(default='default.jpg', upload_to='profile_pics')
  morning_time = models.TimeField(null=True)
  day_time = models.TimeField(null=True)
  bed_time = models.TimeField(null=True)
  # timezone is detected with javascript
  timezone = models.CharField(max_length=100, default="UTC")
  hobbies = models.JSONField(default=default_hobbies)

  streak = models.PositiveIntegerField(default=0)
  points = models.PositiveIntegerField(default=250)
  tickets = models.PositiveIntegerField(default=1)
  score = models.FloatField(default=0.0)

  # this field is hidden and only used for calculations
  prev_scores = models.JSONField(default=dict)

  def __str__(self):
    return self.user.username
  