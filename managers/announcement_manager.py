from models.announcement_model import Announcement
from utils.database import db


class AnnouncementManager:
    @staticmethod
    def create_announcement(title, content, is_active=True):
        """创建公告"""
        announcement = Announcement(title=title, content=content, is_active=is_active)
        db.session.add(announcement)
        db.session.commit()
        return announcement

    @staticmethod
    def get_announcement_by_id(announcement_id):
        """通过ID获取公告"""
        return Announcement.query.get(announcement_id)

    @staticmethod
    def get_active_announcements():
        """获取所有激活的公告"""
        return Announcement.query.filter_by(is_active=True).order_by(Announcement.publish_time.desc()).all()

    @staticmethod
    def update_announcement(announcement_id, **kwargs):
        """更新公告"""
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return None

        for attr, value in kwargs.items():
            if hasattr(announcement, attr):
                setattr(announcement, attr, value)

        db.session.commit()
        return announcement

    @staticmethod
    def toggle_announcement(announcement_id):
        """切换公告激活状态"""
        announcement = Announcement.query.get(announcement_id)
        if announcement:
            announcement.is_active = not announcement.is_active
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_announcement(announcement_id):
        """删除公告"""
        announcement = Announcement.query.get(announcement_id)
        if announcement:
            db.session.delete(announcement)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_announcements():
        """获取所有公告"""
        return Announcement.query.order_by(Announcement.publish_time.desc()).all()