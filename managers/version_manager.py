from models.version_model import SoftwareVersion
from utils.database import db

class VersionManager:
    @staticmethod
    def create_version(version_number, release_date, download_url, changelog=None, force_update=False,
                       set_active=False):
        """创建新版本"""
        # 检查版本号是否已存在
        if SoftwareVersion.query.filter_by(version_number=version_number).first():
            return None, "版本号已存在"

        version = SoftwareVersion(
            version_number=version_number,
            release_date=release_date,
            download_url=download_url,
            changelog=changelog,
            force_update=force_update
        )

        db.session.add(version)

        if set_active:
            version.set_active()

        db.session.commit()
        return version, "创建成功"

    @staticmethod
    def get_version_by_id(version_id):
        """通过ID获取版本"""
        return SoftwareVersion.query.get(version_id)

    @staticmethod
    def get_version_by_number(version_number):
        """通过版本号获取版本"""
        return SoftwareVersion.query.filter_by(version_number=version_number).first()

    @staticmethod
    def get_active_version():
        """获取当前激活版本"""
        return SoftwareVersion.query.filter_by(is_active=True).first()

    @staticmethod
    def get_latest_version():
        """获取最新版本（按创建时间）"""
        return SoftwareVersion.query.order_by(SoftwareVersion.create_time.desc()).first()

    @staticmethod
    def set_active_version(version_id):
        """设置激活版本"""
        version = SoftwareVersion.query.get(version_id)
        if version:
            version.set_active()
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_version(version_id, **kwargs):
        """更新版本信息"""
        version = SoftwareVersion.query.get(version_id)
        if not version:
            return None

        # 不允许修改版本号
        if 'version_number' in kwargs:
            del kwargs['version_number']

        for attr, value in kwargs.items():
            if hasattr(version, attr):
                setattr(version, attr, value)

        db.session.commit()
        return version

    @staticmethod
    def delete_version(version_id):
        """删除版本"""
        version = SoftwareVersion.query.get(version_id)
        if version:
            # 如果删除的是激活版本，需要设置另一个版本为激活
            if version.is_active:
                # 设置最新版本为激活
                latest = SoftwareVersion.query.order_by(SoftwareVersion.create_time.desc()).first()
                if latest and latest.id != version_id:
                    latest.is_active = True

            db.session.delete(version)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_versions():
        """获取所有版本"""
        return SoftwareVersion.query.order_by(SoftwareVersion.create_time.desc()).all()