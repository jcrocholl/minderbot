from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    list_display = ('email',
                    'is_staff', 'is_active', 'is_superuser', 'is_banned',
                    'last_login', 'date_joined')
    fields = ('email', 'password',
              'is_active', 'is_staff', 'is_superuser', 'is_banned')
