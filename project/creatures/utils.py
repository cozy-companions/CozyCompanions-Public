from django.utils import timezone
from .models import UserCreature, HIBERNATE_AFTER, WAKE_UP_COST

def get_companion_notification(user, generate_notifs = True):
  now = timezone.now()
  hungry = []
  dropped = []
  hibernating = []

  creatures = UserCreature.objects.filter(user=user).select_related('creature')
  for uc in creatures:
    before_level = uc.level
    changes = uc.apply_hunger_delay(now=now)
    if not generate_notifs:
      continue
    uc.refresh_from_db()

    if uc.is_hibernating:
      dur = now - (uc.hibernating_since or now)
      hibernating.append({
        "name": uc.creature.name,
        "level": uc.level,
        "hours_hibernating": round(dur.total_seconds()/3600, 1),
        'wake_cost': WAKE_UP_COST,
        "id": uc.id,
      })
      continue

    if changes.get('dropped') > 0:
      dropped.append({
        "name": uc.creature.name,
        "old_level": before_level,
        "new_level": uc.level,
        "dropped": changes['dropped'],
        "id": uc.id,
      })

    elif uc.is_hungry:
      hungry_start = uc.hungry_since or uc._hungry_start_time()
      hungry_hours = (now - hungry_start).total_seconds() / 3600
      hungry.append({
        "name": uc.creature.name,
        "level": uc.level,
        "hungry_hours": round(hungry_hours, 1),
        "id": uc.id,
      })

    

  return {
    "hungry": hungry,
    "dropped": dropped,
    "hibernating": hibernating,
  }