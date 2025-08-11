from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import random

# list of rarities
RARITIES = (
    ('Common', 'Common'),
    ('Rare', 'Rare'),
    ('Elite', 'Elite'),
    ('Epic', 'Epic'),
    ('Legendary', 'Legendary'),
  )

# constant values
LEVEL_DROP_INTERVAL = 21
HIBERNATE_AFTER = 72
MAX_EGGS = 3
WAKE_UP_COST = 500

# Create your models here.
class Creature(models.Model):
  name = models.CharField(max_length=100)
  rarity = models.CharField(max_length=20, choices=RARITIES)
  sprite = models.CharField(max_length=200, default="creatures/")
  icon = models.CharField(max_length=200, default="creatures/")

  # autofill sprites
  def save(self, *args, **kwargs):
    if not self.sprite.endswith(".png"):
      self.sprite = f"creatures/{self.rarity.lower()}/sprites/{self.name.lower()}.webp"

    if not self.icon.endswith(".png"):
      self.icon = f"creatures/{self.rarity.lower()}/icons/{self.name.lower()}.webp"
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.name} - {self.rarity}"
  

# model for creatures owned by users
class UserCreature(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
  level = models.PositiveBigIntegerField(default=1)
  selected = models.BooleanField(default=False)
  last_fed_time = models.DateTimeField(default=timezone.now)
  hunger_delay_hours = models.PositiveBigIntegerField(default=24)

  hungry_since = models.DateTimeField(null=True, blank=True)
  last_level_drop_time = models.DateTimeField(null=True, blank=True)
  is_hibernating = models.BooleanField(default=False)
  hibernating_since = models.DateTimeField(null=True, blank=True)



  class Meta:
    unique_together = ('user', 'creature')
  
  def __str__(self):
    return f"{self.user.username}'s {self.creature.name} (Lvl: {self.level})"
  
  #functions to return times
  def _current_hunger_delay_hours(self):
    capped_level = min(self.level, 10)
    return 21 + capped_level * 3
  
  @property 
  def hours_until_hungry(self):
    return self ._current_hunger_delay_hours()

  def _hungry_start_time(self):
    return self.last_fed_time + timedelta(hours=self.hunger_delay_hours)
  
  @property
  def is_hungry(self):
      if self.is_hibernating:
        return False
      return timezone.now() >= self._hungry_start_time()
  
  
  def level_up(self, amount=1):
    self.level += amount
    self.save(update_fields=['level'])

  def level_down(self, amount=1):
    old_level = self.level
    self.level = max(1, self.level - amount)
    self.save(update_fields=['level'])
    return old_level - self.level

  # to feed creature
  def feed(self):
    if self.is_hibernating:
      raise ValidationError("This companion is hibernating, Wake it before feeding.")
    
    now = timezone.now()
    self.last_fed_time = now
    self.hunger_delay_hours = self._current_hunger_delay_hours()
    self.hungry_since = None
    self.last_level_drop_time = None
    self.save(update_fields=[
        'last_fed_time', 'hunger_delay_hours',
        'hungry_since', 'last_level_drop_time'
    ])
    return True
  

  def _auto_hibernate(self, now=None):
    if now is None:
      now = timezone.now()
    if not self.is_hibernating:
      self.is_hibernating = True
      self.hibernating_since = now
      self.save(update_fields=['is_hibernating', 'hibernating_since'])

  def wake_from_hibernation(self, cost=None):
    if not self.is_hibernating:
      return True
    
    profile = self.user.profile
    if cost is None:
      cost = WAKE_UP_COST
    if profile.points < cost:
      raise ValidationError("Not enough points to wake this companion up.")
    
    profile.points -= cost
    profile.save()

    now = timezone.now()
    self.is_hibernating = False
    self.hibernating_since = None
    self.last_fed_time = now
    self.hunger_delay_hours = self._current_hunger_delay_hours()
    self.hungry_since = None
    self.last_level_drop_time = None
    self.save(update_fields=[
        'is_hibernating', 'hibernating_since',
        'last_fed_time', 'hunger_delay_hours',
        'hungry_since', 'last_level_drop_time'
    ])
    return True
  

  def apply_hunger_delay(self, now=None):
    if now is None:
      now = timezone.now()

    changes = {'became_hungry': False, 'dropped': 0, 'hibernated': False}

    if self.is_hibernating:
      return changes
    
    if not self.is_hungry:
      if self.hungry_since or self.last_level_drop_time:
        self.hungry_since = None
        self.last_level_drop_time = None
        self.save(update_fields=['hungry_since', 'last_level_drop_time'])
      return changes
    
    if self.hungry_since is None:
      self.hungry_since = self._hungry_start_time()
      self.last_level_drop_time = self.hungry_since
      self.save(update_fields=["hungry_since", "last_level_drop_time"])
      changes["became_hungry"] = True

    if self.level > 1:
      anchor = self.last_level_drop_time or self.hungry_since
      elapsed = now - anchor
      interval_seconds = LEVEL_DROP_INTERVAL * 3600
      full_intervals = int(elapsed.total_seconds()/interval_seconds)

      if full_intervals > 0:
        dropped = self.level_down(full_intervals)
        changes["dropped"] = dropped
        self.last_level_drop_time += timedelta(hours=full_intervals * LEVEL_DROP_INTERVAL)
        self.save(update_fields=["last_level_drop_time"])

    if self.level == 1:
      hungry_duration = now - self.hungry_since
      if hungry_duration >= timedelta(hours=HIBERNATE_AFTER):
        self._auto_hibernate(now)
        changes["hibernated"] = True
    
    return changes
  
  def check_hunger(self):
    if self.is_hibernating:
      return
    time_hungry = timezone.now() - self.last_fed_time
    drops = time_hungry.days
    if drops > 0:
      self.level = max(1, self.level - drops)
      if self.level == 1 and drops >= 3:
        self.is_hibernating = True

      self.save()

  

class Egg(models.Model):
  rarity = models.CharField(max_length=20, choices=RARITIES, unique=True)
  price = models.PositiveIntegerField(default=0)
  hatch_requirement = models.PositiveBigIntegerField(default=3)
  sprite = models.CharField(max_length=200, help_text="eggs/")
  hatch_sprites = models.JSONField(
    default=list,
    help_text="list of hatching sprites"
  )

  def __str__(self):
      return f"{self.rarity} Egg"
  
class UserEgg(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="eggs")
  egg = models.ForeignKey(Egg, on_delete=models.CASCADE)
  progress = models.PositiveIntegerField(default=0)

  def save(self, *args, **kwargs):
    if self._state.adding:
      current_egg_count = UserEgg.objects.filter(user=self.user).count()
      if current_egg_count >= 3:
        raise ValidationError(f"You can only hold upto {MAX_EGGS} eggs at a time")

    super().save(*args, **kwargs)

  # to add tickets
  def add_tickets(self, tickets):
    if self.user.profile.tickets < tickets:
      raise ValidationError("Not enough hatching tickets.")
    self.user.profile.tickets -= tickets
    self.user.profile.save()

    self.progress = min(self.progress + tickets, self.egg.hatch_requirement)
    self.save()
      
  def hatch(self):
    if self.progress < self.egg.hatch_requirement:
      raise ValidationError("Egg is not ready to hatch yet.")
    
    creature = random.choice(Creature.objects.filter(rarity=self.egg.rarity).all())
    user_creature, created = UserCreature.objects.get_or_create(user=self.user, creature= creature)

    if not created:
      user_creature.level_up()

    self.delete()
    return user_creature

  def __str__(self):
    return f"{self.user.username}'s {self.egg.rarity} Egg"


