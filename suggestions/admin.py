from django.contrib import admin

from suggestions.models import Suggestion


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'author', 'created')


admin.site.register(Suggestion, SuggestionAdmin)
