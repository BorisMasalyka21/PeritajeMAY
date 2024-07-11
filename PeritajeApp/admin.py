from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Branch
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('branch',)}), 
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'branch', 'group'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'branch')  
    search_fields = ('username', 'email', 'first_name', 'last_name', 'branch__name') 
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Branch)
