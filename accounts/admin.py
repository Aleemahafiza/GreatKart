from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from django.utils.html import format_html


admin.site.register(UserProfile)
admin.site.register(Account)


class AccountAdmin(UserAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "username",
        "last_login",
        "date_joined",
        "is_active",
    ]


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html(
            '<img scr="{}" width="30" style="border-radius:50%>'.format(
                object.profile_picture_url
            )
        )

    thumbnail.short_description = "Profile Picture"
    list_display = ["thumbnail", "user", "city", "state", "country"]
