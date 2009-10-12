from django.contrib import admin

from reminders.models import Reminder


class ReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'interval', 'owner', 'created')
    fieldsets = (
        (None, {
            'fields': ('title', 'tags',
                       ('days', 'months', 'years', 'miles', 'kilometers'),
                       'owner', 'created')
            }),
        )


admin.site.register(Reminder, ReminderAdmin)
