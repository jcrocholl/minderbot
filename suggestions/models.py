from google.appengine.ext import db

from django.contrib.auth.models import User


class Suggestion(db.Model):
    title = db.StringProperty(required=True)
    tags = db.StringListProperty()
    author = db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.message[:50]
