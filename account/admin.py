from django.contrib import admin
from .models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_verified', 'is_active']
    list_editable = ['is_verified', 'is_active']
    search_fields = ['username', 'email']
    fieldsets = (
        ('User Details', {
            "fields": ('username','email','img'),
        }),
        ('User Status', {
            'classes': ('collapse',),
            'fields': ('is_verified','is_active','is_staff','is_superuser')
        }),
        ('Django Stuffs',{
            'classes': ('collapse',),
            'fields': ('password','last_login','groups','user_permissions')
        }),
    )
    


admin.site.register(User, UserAdmin)