from google.appengine.ext import db

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Reminder(db.Model):
    """
    If owner is None, a public suggestion:
        Replace smoke alarm batteries every year.
    The key name for suggestions is a slug that appears in the URL.

    If owner is set, an actual instance of a reminder:
        Joe wants to replace smoke alarm batteries every year,
        next time on Feb 6, 2010.
    The key name for reminders is a unique random hex string.
    """
    owner = db.ReferenceProperty(User)
    title = db.StringProperty(required=True)
    tags = db.StringListProperty()
    days = db.IntegerProperty()
    months = db.IntegerProperty()
    years = db.IntegerProperty()
    miles = db.IntegerProperty()
    kilometers = db.IntegerProperty()
    previous = db.DateTimeProperty()
    next = db.DateTimeProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.owner:
            return reverse('reminder_detail',
                           kwargs={'object_id': self.key().id()})
        else:
            return reverse('suggestion_detail',
                           kwargs={'object_id': self.key().name()})

    def interval(self):
        weeks = None
        days = self.days
        if days and days % 7 == 0:
            weeks = days / 7
            days = None
        parts = []
        # Singular.
        if days == 1: parts.append('day')
        if weeks == 1: parts.append('week')
        if self.months == 1: parts.append('month')
        if self.years == 1: parts.append('year')
        if self.miles == 1: parts.append('mile')
        if self.kilometers == 1: parts.append('kilometer')
        # Plural.
        if days > 1: parts.append('%d days' % days)
        if weeks > 1: parts.append('%d weeks' % weeks)
        if self.months > 1: parts.append('%d months' % self.months)
        if self.years > 1: parts.append('%d years' % self.years)
        if self.miles > 1: parts.append('%d miles' % self.miles)
        if self.kilometers > 1:
            parts.append('%d kilometers' % self.kilometers)
        return ' or '.join(parts)
