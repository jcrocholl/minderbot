from google.appengine.ext import db

from django.core.urlresolvers import reverse


class Tag(db.Model):
    """
    Each tag has a list of matching suggestions. For performance, the
    tag name is the key_name, not a StringProperty.
    """
    suggestions = db.ListProperty(db.Key)
    count = db.IntegerProperty(required=True)

    def __unicode__(self):
        return self.key().name()

    def get_absolute_url(self):
        return reverse('tags.views.detail',
                       kwargs={'key_name': self.key().name()})

    def get_font_size(self):
        pixels = 12 + min(20, self.count)
        return '%dpx' % pixels
