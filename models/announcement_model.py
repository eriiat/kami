from utils.database import db
from datetime import datetime


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, title, content, is_active=True):
        self.title = title
        self.content = content
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_time': self.publish_time.isoformat(),
            'is_active': self.is_active
        }