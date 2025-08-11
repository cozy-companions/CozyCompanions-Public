from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
import json
from datetime import datetime, timedelta
from django.forms.widgets import TimeInput
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator

# inheritting UserCreationForm and adding email and name
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

# profile form
class ProfileCreationForm(forms.ModelForm):
    # using regex to allow alphanumeric and some special chars
    hobby_validator = RegexValidator(
    r'^[a-zA-Z0-9 ,.()\[\]{}!?_$&-]+$',
    message="Only alphanumeric, commas, periods, brackets, ?!$-_& are allowed" 
    )

    hobbies_json = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id" : "hobbies-json-input"}), max_length=1000,)

    class Meta:
        model = Profile
        fields = ["profile_pic", "morning_time", "day_time", "bed_time", "timezone"]
        widgets = {
            "timezone" : forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["profile_pic"].widget = forms.FileInput(attrs={"accept": "image/*"})
        self.fields["morning_time"].widget = forms.TimeInput(attrs={"type": "time"})
        self.fields["day_time"].widget = forms.TimeInput(attrs={"type": "time"})
        self.fields["bed_time"].widget = forms.TimeInput(attrs={"type": "time"})

    def clean_hobbies_json(self):
        print("\n--- RUNNING clean_hobbies_json ---")
        hobbies_raw = self.cleaned_data.get("hobbies_json", "[]")
        try:
            hobbies_list = json.loads(hobbies_raw)
            if not isinstance(hobbies_list, list):
                raise forms.ValidationError("Invalid hobby format")
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid hobby format")
        print(f"VALIDATING THIS LIST: {hobbies_list}")
        for hobby in hobbies_list:
            self.hobby_validator(hobby)
        print("--- VALIDATION SUCCEEDED ---")
        if len(hobbies_list) > 5:
            raise forms.ValidationError("You can choose only up to 5 hobbies.")

        return {str(hobby): True for hobby in hobbies_list}
        

    def clean(self):
        cleaned_data = super().clean()

        morning = cleaned_data.get("morning_time")
        day = cleaned_data.get("day_time")
        bed = cleaned_data.get("bed_time")

        if all([morning, day, bed]):
            today = datetime.today().date()
            morning_dt = datetime.combine(today, morning)
            day_dt = datetime.combine(today, day)
            bed_dt = datetime.combine(today, bed)

            if bed <= morning:
                bed_dt += timedelta(days=1)

            if not (morning_dt < day_dt < bed_dt):
                raise forms.ValidationError(
                    "Time order must be morning → day → bedtime"
                )

            if (day_dt - morning_dt < timedelta(hours=3)) or (
                bed_dt - day_dt < timedelta(hours=3)
            ):
                raise forms.ValidationError("All times must be at least 3 hours apart")
            

        

    def clean_image (self):
        image = self.cleaned_data.get("profile_pic")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Profile Picture must be under 5 MB")
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.hobbies = self.cleaned_data.get("hobbies_json", {})

        if commit:
            instance.save()
        return instance


class AccountDeletionForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
        label="Password",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect Password")
        return password
