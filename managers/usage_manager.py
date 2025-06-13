from models.usage_model import UsageRecord
from utils.database import db


class UsageManager:
    @staticmethod
    def create_record(key_id, ip_address, software_version, location=None):
        """创建使用记录"""
        record = UsageRecord(
            key_id=key_id,
            ip_address=ip_address,
            software_version=software_version,
            location=location
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def get_records_by_key(key_id):
        """获取指定卡密的使用记录"""
        return UsageRecord.query.filter_by(key_id=key_id).order_by(UsageRecord.access_time.desc()).all()

    @staticmethod
    def search_records(key_value=None, ip_address=None, start_date=None, end_date=None):
        """搜索使用记录"""
        query = UsageRecord.query

        if key_value:
            # 关联卡密表查询
            from models.key_model import ActivationKey
            query = query.join(ActivationKey).filter(ActivationKey.key_value.like(f"%{key_value}%"))

        if ip_address:
            query = query.filter(UsageRecord.ip_address.like(f"%{ip_address}%"))

        if start_date and end_date:
            query = query.filter(UsageRecord.access_time.between(start_date, end_date))
        elif start_date:
            query = query.filter(UsageRecord.access_time >= start_date)
        elif end_date:
            query = query.filter(UsageRecord.access_time <= end_date)

        return query.order_by(UsageRecord.access_time.desc()).all()

    @staticmethod
    def export_records():
        """导出使用记录（返回数据）"""
        records = UsageRecord.query.all()
        return [record.to_dict() for record in records]