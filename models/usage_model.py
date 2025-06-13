from utils.database import db
from datetime import datetime


class UsageRecord(db.Model):
    __tablename__ = 'usage_records'

    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('activation_keys.id'), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    software_version = db.Column(db.String(20), nullable=False)
    access_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    location = db.Column(db.String(100))

    def __init__(self, key_id, ip_address, software_version, location=None):
        self.key_id = key_id
        self.ip_address = ip_address
        self.software_version = software_version
        self.location = location

    def to_dict(self):
        return {
            'id': self.id,
            'key_id': self.key_id,
            'ip_address': self.ip_address,
            'software_version': self.software_version,
            'access_time': self.access_time.isoformat(),
            'location': self.location
        }