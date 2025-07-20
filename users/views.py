from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Custom registration form
from users.Registration.registration import Registration

# User preference form
from users.Registration.forms import UserPreferenceForm
from news.models import UserPreference


# -----------------------------
# HOME PAGE VIEW
# -----------------------------
def home(request):
    return render(request, 'users/home.html')


# -----------------------------
# USER REGISTRATION VIEW
# -----------------------------
def register(request):
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')  # Assuming login URL name is 'login'
    else:
        form = Registration()
    return render(request, 'users/register.html', {'form': form})


# -----------------------------
# USER PREFERENCES VIEW
# -----------------------------
@login_required
def preferences(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferences updated.")
            return redirect('users:preferences')
    else:
        form = UserPreferenceForm(instance=preference)

    return render(request, 'users/preferences.html', {'form': form})
