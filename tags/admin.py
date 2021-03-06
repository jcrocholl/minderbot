from django.contrib import admin

from tags.models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'count', 'created')


admin.site.register(Tag, TagAdmin)
