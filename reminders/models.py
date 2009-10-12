from google.appengine.ext import db

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from suggestions.models import Suggestion


class Reminder(Suggestion):
    """
    Actual instance of a reminder, created by a user.

    The key name is a unique random hex string for generating a URL.
    """
    suggestion = db.ReferenceProperty(Suggestion, required=False)
    next = db.DateTimeProperty(required=True)
    previous = db.DateTimeProperty()

    def get_absolute_url(self):
        return reverse('reminder_detail',
                       kwargs={'object_id': self.key().name()})
