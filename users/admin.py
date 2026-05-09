from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "name",
        "surname",
        "phone",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = (
        "email",
        "name",
        "surname",
        "phone",
    )
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
        "favorites",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "������������ ����������",
            {
                "fields": (
                    "name",
                    "surname",
                    "phone",
                    "github_url",
                    "about",
                    "avatar",
                )
            },
        ),
        (
            "����� �������",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "���������",
            {
                "fields": (
                    "favorites",
                )
            },
        ),
        (
            "������ ����",
            {
                "fields": (
                    "last_login",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
