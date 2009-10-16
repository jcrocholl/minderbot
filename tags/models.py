from google.appengine.ext import db

from django.core.urlresolvers import reverse


class Tag(db.Model):
    """
    Each tag has a list of matching reminders. For performance, the
    tag name is the datastore key name, not a StringProperty.
    """
    suggestions = db.StringListProperty()
    count = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.key().name()

    def get_absolute_url(self):
        return reverse('tags.views.detail',
                       kwargs={'key_name': self.key().name()})

    def get_font_size(self):
        pixels = 14 + min(20, self.count)
        return '%dpx' % pixels

    def get_suggestions(self):
        keys = [db.Key.from_path('reminders_reminder', key_name)
                for key_name in self.suggestions]
        return db.get(keys)
