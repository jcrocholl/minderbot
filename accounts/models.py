from google.appengine.ext import db
from ragendja.auth.models import EmailUser


class User(EmailUser):

    def __unicode__(self):
        email = self.email
        at = email.find('@')
        if at > 0:
            email = email[:at]
        return email
