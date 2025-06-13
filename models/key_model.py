from datetime import datetime, timedelta
from utils.database import db


class ActivationKey(db.Model):
    __tablename__ = 'activation_keys'

    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(50), unique=True, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    use_time = db.Column(db.DateTime)
    expire_time = db.Column(db.DateTime)
    machine_code = db.Column(db.String(100))
    status = db.Column(db.Enum('未使用', '已激活', '已禁用'), default='未使用', nullable=False)
    remarks = db.Column(db.Text)
    creator = db.Column(db.String(50))

    def __init__(self, key_value, duration, remarks=None, creator=None):
        self.key_value = key_value
        self.duration = duration
        self.remarks = remarks
        self.creator = creator

    def set_used(self, machine_code):
        self.use_time = datetime.utcnow()
        self.expire_time = self.use_time + timedelta(days=self.duration)
        self.machine_code = machine_code
        self.status = '已激活'

    def disable(self):
        self.status = '已禁用'

    def enable(self):
        if self.use_time:
            self.status = '已激活'
        else:
            self.status = '未使用'

    def to_dict(self):
        return {
            'id': self.id,
            'key_value': self.key_value,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'duration': self.duration,
            'use_time': self.use_time.isoformat() if self.use_time else None,
            'expire_time': self.expire_time.isoformat() if self.expire_time else None,
            'machine_code': self.machine_code,
            'status': self.status,
            'remarks': self.remarks,
            'creator': self.creator
        }