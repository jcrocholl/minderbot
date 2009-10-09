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
        # Singular.
        if self.days == 1: parts.append('day')
        if self.months == 1: parts.append('month')
        if self.years == 1: parts.append('year')
        if self.miles == 1: parts.append('mile')
        if self.kilometers == 1:
            parts.append('kilometer')
        # Plural.
        if self.days > 1: parts.append('%d days' % self.days)
        if self.months > 1: parts.append('%d months' % self.months)
        if self.years > 1: parts.append('%d years' % self.years)
        if self.miles > 1: parts.append('%d miles' % self.miles)
        if self.kilometers > 1:
            parts.append('%d kilometers' % self.kilometers)
        return ' or '.join(parts)
