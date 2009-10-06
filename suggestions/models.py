from google.appengine.ext import db

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Suggestion(db.Model):
    title = db.StringProperty(required=True)
    tags = db.StringListProperty()
    author = db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.title[:50]

    def get_absolute_url(self):
        return reverse('suggestion_detail',
                       kwargs={'object_id': self.key().id_or_name()})
