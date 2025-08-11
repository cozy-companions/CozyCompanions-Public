from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserRegisterForm, ProfileCreationForm, AccountDeletionForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from tracking.utils import get_active_questionaire
from django.utils.timezone import make_aware
from .models import Profile
from creatures.utils import get_companion_notification
from creatures.models import Creature, UserCreature
from collections import defaultdict
from decouple import config

# Create your views here.

# project mail
project_email = config("EMAIL")

# view for root url
def index(request):
    if request.user.is_authenticated:
          try:
              request.user.profile
              current, next_info, _ = get_active_questionaire(request.user)
              profile = request.user.profile
              companion_notifications = get_companion_notification(request.user)
              
              # Get selected creatures for the preview
              user_creatures = UserCreature.objects.filter(user=request.user)
              selected_creatures = user_creatures.filter(selected=True)
              
              context = {
                  "title": "homepage",
                  "current_questionnaire": current,
                  "next_questionnaire": next_info[0] if next_info else None,
                  "seconds_until_next": next_info[1] if next_info else None,
                  "profile_pic": profile.profile_pic,
                  "points": profile.points,
                  "tickets": profile.tickets,
                  "companion_notifications": companion_notifications,
                  "selected_creatures": selected_creatures,
              }
              # if logged in and has a profile
              return render(request, "homepage.html", context)
          except ObjectDoesNotExist:
              # redirect to profile creation if no profile
              return redirect("profile-creation")

    else:
        # use landing page if not logged in
        return render(request, "landing.html", {"title": "landing"})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")

            # send a mail to user after registration
            htmly = get_template("email.html")
            d = {"username": username}
            subject, from_email, to = "Welcome to CozyCompanions", project_email, email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, f"You have been registered. Please log in")
            # redirect to login after successful registration
            return redirect("Login")

        else:
            print("Form errors:", form.errors)
    else:
        # on GET request
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form, "title": "register here"})


def Login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            form = login(request, user)
            messages.success(request, f"Successfully logged in")

            if not hasattr(user, "profile"):
                # first login, redirect to profile creation
                return redirect("profile-creation")
            # else redirect index, which loads homepage
            return redirect("index")
        else:
            messages.error(request, f"Invalid username or password, please try again")
    form = AuthenticationForm()
    return render(request, "login.html", {"form": form, "title": "Log In"})


@login_required
def profile_creation(request):
    if hasattr(request.user, "profile"):
        # if profile exists, redirect to homepage
        return redirect("index")

    if request.method == "POST":
        form = ProfileCreationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("index")

    else:
        form = ProfileCreationForm()
    return render(
        request,
        "profile-creation.html",
        {
            "form": form,
        },
    )

# simple function to render user's profile
@login_required
def view_profile(request):
    profile = request.user.profile
    return render(request, "profile.html", {"profile": profile})


@login_required
def delete_account(request):
    # prevent admins from deleting their accounts
    if request.user.is_superuser:
        messages.error(request, "Superuser accounts cannot be deleted through this feature.")
        return redirect('index')
    
    if request.method == "POST":
        form = AccountDeletionForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            # logout and delete user
            logout(request)
            user.delete()
            return redirect("index")
    else:
        form = AccountDeletionForm(request.user)
    return render(request, "delete-account.html", {"form": form})


@login_required
def profile_update(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = ProfileCreationForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save(commit=True)
            return redirect("profile")

    else:
        form = ProfileCreationForm(instance=profile)

    # this is to load existing hobbies
    active_hobbies = [
        hobby for hobby, is_active in profile.hobbies.items() if is_active
    ]
    context = {
        "form": form,
        "hobbies_list": active_hobbies,
    }
    return render(
        request,
        "profile-update.html",
        context,
    )

def wiki(request):
    return render(request, "wiki.html", {})

def all_creatures(request):
    RARITY_ORDER = ['Common', 'Rare', 'Elite', 'Epic', 'Legendary']
    creatures = Creature.objects.all()
    grouped = defaultdict(list)

    for c in creatures:
        grouped[c.rarity].append(c)

    # Optional: sort each group alphabetically
    for rarity in grouped:
        grouped[rarity] = sorted(grouped[rarity], key=lambda x: x.name)

    # Sort rarities according to defined order
    sorted_grouped = [(rarity, grouped[rarity]) for rarity in RARITY_ORDER if rarity in grouped]

    return render(request, 'all-companions.html', {
        'creatures_by_rarity': sorted_grouped
    })