from django.core.exceptions import ObjectDoesNotExist

# used in index.html for correctly displaying navbar during profile creation
def has_profile_context(request):
  has_profile = False
  if request.user.is_authenticated:
    try:
      request.user.profile
      has_profile = True
    except ObjectDoesNotExist:
      has_profile = False
  return {"has_profile": has_profile}