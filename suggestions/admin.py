from django.contrib import admin

from suggestions.models import Suggestion


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'interval', 'owner', 'created')
    fieldsets = (
        (None, {
            'fields': ('title', 'tags',
                       ('days', 'months', 'years', 'miles', 'kilometers'),
                       'owner', 'created')
            }),
        )


admin.site.register(Suggestion, SuggestionAdmin)
