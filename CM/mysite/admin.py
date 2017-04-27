from django.contrib import admin
from .models import UserProfile,Registration_Request,book,others
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class ProfileInline(admin.StackedInline):
    model = UserProfile
    #fk_name = 'user'
    max_num = 1
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline,]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Registration_Request)
admin.site.register(book)
admin.site.register(others)

