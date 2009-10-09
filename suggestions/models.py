from google.appengine.ext import db

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Suggestion(db.Model):
    title = db.StringProperty(required=True)
    days = db.IntegerProperty()
    months = db.IntegerProperty()
    years = db.IntegerProperty()
    miles = db.IntegerProperty()
    kilometers = db.IntegerProperty()
    tags = db.StringListProperty()
    author = db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.title[:50]

    def get_absolute_url(self):
        return reverse('suggestion_detail',
                       kwargs={'object_id': self.key().id_or_name()})

    def interval(self):
        parts = []
        if self.days:
            parts.append('%d days' % self.days)
        if self.months:
            parts.append('%d months' % self.months)
        if self.years:
            parts.append('%d years' % self.years)
        if self.miles:
            parts.append('%d miles' % self.miles)
        if self.kilometers:
            parts.append('%d km' % self.kilometers)
        return ' or '.join(parts)
