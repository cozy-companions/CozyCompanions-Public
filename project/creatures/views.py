from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Egg, UserEgg, UserCreature, WAKE_UP_COST
from .utils import get_companion_notification
from django.utils import timezone

# Create your views here.
# to render companions page
@login_required
def companions(request):
  get_companion_notification(request.user, generate_notifs=False)
  user_creatures = UserCreature.objects.filter(user=request.user)
  selected_creatures = user_creatures.filter(selected=True)
  now=timezone.now()
  for uc in user_creatures:
        if not uc.is_hibernating and uc.last_fed_time:
          hungry_at = uc.last_fed_time + timezone.timedelta(hours=uc.hours_until_hungry)
          if now >= hungry_at:
            uc.hunger_percent = 100
          else:
            total_duration = (hungry_at - uc.last_fed_time).total_seconds()
            elapsed = (now-uc.last_fed_time).total_seconds()
            if total_duration > 0:
              uc.hunger_percent = min(100, int((elapsed / total_duration) * 100))
            else:
              uc.hunger_percent = 0
        elif uc.is_hibernating:
          uc.hunger_percent = 100
        else:
          uc.hunger_percent = 100
          
  return render(request, "creatures/companions.html", {
    "user_creatures": user_creatures,
    "selected_creatures": selected_creatures,
    "now": now,
    "wake_up_cost": WAKE_UP_COST,
  })

@login_required
def egg_view(request):
  eggs = Egg.objects.all()
  user_eggs = UserEgg.objects.filter(user=request.user)

  context = {
    "eggs": eggs,
    "user_eggs": user_eggs,
  }
  return render(request, "creatures/eggs.html", context)

# to buy eggs - to be used in buttons
@login_required
@require_POST
def buy_egg(request, egg_id):
  egg = get_object_or_404(Egg, pk=egg_id)
  profile = request.user.profile
  egg_count = UserEgg.objects.filter(user=request.user).count()
  if egg_count >= 3:
    return JsonResponse({"error": "You can only hold upto 3 eggs"}, status=400)
  
  if profile.points < egg.price:
    return JsonResponse({"error": "Not enough points."}, status=400)
  
  profile.points -= egg.price
  profile.save()

  UserEgg.objects.create(user=request.user, egg=egg)
  return JsonResponse({"message": f"You bought a {egg.rarity} Egg!"})

# to add tickets - 
@login_required
@require_POST
def add_tickets_view(request, user_egg_id):
  user_egg = get_object_or_404(UserEgg, pk = user_egg_id, user=request.user)

  try:
    user_egg.add_tickets(1)
    ready = user_egg.progress >= user_egg.egg.hatch_requirement
    context = {
      "progress": user_egg.progress,
      "hatch_requirement": user_egg.egg.hatch_requirement,
      "ready": ready
    }
    return JsonResponse(context)
  except ValidationError as e:
    return JsonResponse({"error": str(e)}, status=400)

# hatch button
@login_required
@require_POST
def hatch_egg_view(request, user_egg_id):
  user_egg = get_object_or_404(UserEgg, pk=user_egg_id, user=request.user)
  try:
    creature = user_egg.hatch()
    context = {
      "creature_name": creature.creature.name,
      "creature_rarity": creature.creature.rarity,
      "creature_sprite": creature.creature.sprite,
      "level": creature.level
    }
    return JsonResponse(context)
  except ValidationError as e:
    return JsonResponse({"error": str(e)}, status=400)
  
# button to wake creature
@login_required
@require_POST
def wake_creature(request, creature_id):
  try:
      uc = UserCreature.objects.get(id=creature_id, user=request.user)
      uc.wake_from_hibernation()
      return JsonResponse({
        "success": True,
        "message": f"{uc.creature.name} has woken up!"
      })
  except UserCreature.DoesNotExist:
    return JsonResponse({"error": "Creature not found."}, status=404)
  except ValidationError as e:
    return JsonResponse({"error": str(e)}, status=400)
  
# to select companions
@login_required
@require_POST
def toggle_selected(request):
  uc_id = request.POST.get("uc_id")
  try:
    uc = UserCreature.objects.get(id=uc_id, user=request.user)
  except UserCreature.DoesNotExist:
    return JsonResponse({"error": "Invalid Companion."}, status=404)
  
  if uc.selected:
    uc.selected = False
    uc.save()
    return JsonResponse({"status": "unselected"})
  else:
    selected_count = UserCreature.objects.filter(user=request.user, selected=True).count()
    if selected_count >=4:
      return JsonResponse({"error": "You can only select upto 4 companions for display."})
    uc.selected = True
    uc.save()
    return JsonResponse({"status": "selected"})

# button to feed
@login_required
@require_POST
def feed(request):
  uc_id = request.POST.get("uc_id")
  try:
    uc = UserCreature.objects.get(id=uc_id, user=request.user)
    uc.feed()
    uc.save()
    return JsonResponse({"status": "fed"})
  except UserCreature.DoesNotExist:
    return JsonResponse({"error": "Invalid creature."}, status=404)
  except ValidationError as e:
    return JsonResponse({"error": str(e)}, status=400)

