from models.key_model import ActivationKey
from utils.database import db
import secrets


class KeyManager:
    @staticmethod
    def generate_key():
        """生成随机的卡密"""
        parts = [secrets.token_hex(2).upper() for _ in range(4)]
        return '-'.join(parts)

    @staticmethod
    def create_key(duration, count=1, remarks=None, creator=None):
        """批量创建卡密"""
        keys = []
        for _ in range(count):
            key_value = KeyManager.generate_key()
            key = ActivationKey(
                key_value=key_value,
                duration=duration,
                remarks=remarks,
                creator=creator
            )
            db.session.add(key)
            keys.append(key)
        db.session.commit()
        return keys

    @staticmethod
    def get_key_by_id(key_id):
        """通过ID获取卡密"""
        return ActivationKey.query.get(key_id)

    @staticmethod
    def get_key_by_value(key_value):
        """通过卡密值获取卡密"""

        return ActivationKey.query.filter_by(key_value=key_value).first()

    @staticmethod
    def update_key(key_id, **kwargs):
        """更新卡密信息"""
        key = ActivationKey.query.get(key_id)
        if not key:
            return None

        for attr, value in kwargs.items():
            if hasattr(key, attr):
                setattr(key, attr, value)

        db.session.commit()
        return key

    @staticmethod
    def activate_key(key_value, machine_code):
        """激活卡密"""
        key = ActivationKey.query.filter_by(key_value=key_value).first()
        if not key:
            return False, "卡密不存在"

        if key.status == '已激活':
            return False, "卡密已被激活"

        if key.status == '已禁用':
            return False, "卡密已被禁用"

        key.set_used(machine_code)
        db.session.commit()
        return True, "激活成功"

    @staticmethod
    def disable_key(key_id):
        """禁用卡密"""
        key = ActivationKey.query.get(key_id)
        if key:
            key.disable()
            db.session.commit()
            return True
        return False

    @staticmethod
    def enable_key(key_id):
        """启用卡密"""
        key = ActivationKey.query.get(key_id)
        if key:
            key.enable()
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_key(key_id):
        """删除卡密"""
        key = ActivationKey.query.get(key_id)
        if key:
            db.session.delete(key)
            db.session.commit()
            return True
        return False

    @staticmethod
    def search_keys(status=None, start_date=None, end_date=None, creator=None):
        """搜索卡密"""
        query = ActivationKey.query
        if status:
            query = query.filter_by(status=status)

        if creator:
            query = query.filter_by(creator=creator)

        if start_date and end_date:
            query = query.filter(ActivationKey.create_time.between(start_date, end_date))
        elif start_date:
            query = query.filter(ActivationKey.create_time >= start_date)
        elif end_date:
            query = query.filter(ActivationKey.create_time <= end_date)

        return query.all()