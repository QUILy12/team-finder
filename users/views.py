from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.constants import PROJECTS_PAGE_SIZE
from team_finder.services import get_page_obj

from .forms import UserEditForm, UserLoginForm, UserRegistrationForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = UserRegistrationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = UserLoginForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("projects:list")

        messages.error(request, "Неверный email или пароль")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id, is_active=True)
    return render(request, "users/user-details.html", {"user": user_obj})


def participants_list_view(request):
    users = User.objects.filter(is_active=True).order_by("id")
    page_obj = get_page_obj(request, users, PROJECTS_PAGE_SIZE)
    return render(request, "users/participants.html", {"participants": page_obj})


@login_required
def edit_profile_view(request):
    form = UserEditForm(request.POST or None, request.FILES or None, instance=request.user)

    if form.is_valid():
        form.save()
        messages.success(request, "Профиль успешно обновлён")
        return redirect("users:detail", user_id=request.user.id)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль успешно изменён")
        return redirect("users:detail", user_id=request.user.id)

    return render(request, "users/change_password.html", {"form": form})
