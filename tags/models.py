from google.appengine.ext import db


class Tag(db.Model):
    """
    Each tag has a list of matching suggestions. For performance, the
    tag name is the key_name, not a StringProperty.
    """
    suggestions = db.ListProperty(db.Key)
    count = db.IntegerProperty(required=True)
