from utils.database import db
from datetime import datetime


class SoftwareVersion(db.Model):
    __tablename__ = 'software_versions'

    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), unique=True, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    download_url = db.Column(db.String(255), nullable=False)
    changelog = db.Column(db.Text)
    force_update = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, version_number, release_date, download_url, changelog=None, force_update=False, is_active=False):
        self.version_number = version_number
        self.release_date = release_date
        self.download_url = download_url
        self.changelog = changelog
        self.force_update = force_update
        self.is_active = is_active

    def set_active(self):
        # 当设置一个版本为激活时，需要将所有其他版本设置为非激活
        SoftwareVersion.query.update({SoftwareVersion.is_active: False})
        self.is_active = True

    def to_dict(self):
        return {
            'id': self.id,
            'version_number': self.version_number,
            'release_date': self.release_date.isoformat(),
            'download_url': self.download_url,
            'changelog': self.changelog,
            'force_update': self.force_update,
            'is_active': self.is_active,
            'create_time': self.create_time.isoformat()
        }