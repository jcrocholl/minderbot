from django.contrib import admin

from suggestions.models import Suggestion


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'interval', 'author', 'created')
    fieldsets = (
        (None, {
            'fields': ('title', 
                       ('days', 'months', 'years', 'miles', 'kilometers'),
                       'author', 'created', 'tags')
            }),
        )


admin.site.register(Suggestion, SuggestionAdmin)
