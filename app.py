from dataclasses import dataclass

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import secrets
import config
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config.from_object(config.Config)
app.secret_key = app.config['SECRET_KEY']
db = SQLAlchemy(app)
# 初始化 Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='admin', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 用户加载器
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 数据库模型定义
@dataclass
class ActivationKey(db.Model):
    __tablename__ = 'activation_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(50), unique=True, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    use_time = db.Column(db.DateTime)
    expire_time = db.Column(db.DateTime)
    machine_code = db.Column(db.String(100))
    status = db.Column(db.String(20), default='未使用', nullable=False)
    remarks = db.Column(db.Text)
    creator = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'key_value': self.key_value,
            'create_time': self.create_time,
            'duration': self.duration,
            'use_time': self.use_time,
            'expire_time': self.expire_time,
            'machine_code': self.machine_code,
            'status': self.status,
            'remarks': self.remarks,
            'creator': self.creator
        }


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

    def to_dict(self):
        return {
            'id': self.id,
            'version_number': self.version_number,
            'release_date': self.release_date.strftime('%Y-%m-%d'),
            'download_url': self.download_url,
            'changelog': self.changelog,
            'force_update': self.force_update,
            'is_active': self.is_active,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_time': self.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': self.is_active
        }


class UsageRecord(db.Model):
    __tablename__ = 'usage_records'
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('activation_keys.id'), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    software_version = db.Column(db.String(20), nullable=False)
    access_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    location = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'key_id': self.key_id,
            'ip_address': self.ip_address,
            'software_version': self.software_version,
            'access_time': self.access_time.strftime('%Y-%m-%d %H:%M:%S'),
            'location': self.location
        }

# 辅助函数
def generate_key():
    """生成随机的卡密"""
    parts = [secrets.token_hex(2).upper() for _ in range(4)]
    return '-'.join(parts)


# 视图路由
@app.route('/')
@login_required
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    # 获取统计数据
    total_keys = ActivationKey.query.count()
    activated_keys = ActivationKey.query.filter_by(status='已激活').count()
    unused_keys = ActivationKey.query.filter_by(status='未使用').count()
    versions_count = SoftwareVersion.query.count()

    # 获取最近5条使用记录
    recent_usage = UsageRecord.query.order_by(UsageRecord.access_time.desc()).limit(5).all()

    # 获取激活的公告
    active_announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.publish_time.desc()).limit(3).all()

    return render_template('index.html',
                           today=today,
                           total_keys=total_keys,
                           activated_keys=activated_keys,
                           unused_keys=unused_keys,
                           versions_count=versions_count,
                           recent_usage=recent_usage,
                           active_announcements=active_announcements,
                           active_page='dashboard')


@app.route('/keys', methods=['GET', 'POST'])
@login_required
def keys_page():
    if request.method == 'POST':
        # 生成卡密
        data = request.get_json()
        count = int(data['count'])
        duration = data['duration']
        remarks = data['remarks']
        creator = 'admin'  # 实际应用中应从会话获取

        keys = []
        for _ in range(count):
            key_value = generate_key()
            key = ActivationKey(
                key_value=key_value,
                duration=duration,
                remarks=remarks,
                creator=creator
            )
            db.session.add(key)
            keys.append(key)
        db.session.commit()
        flash(f'成功生成 {count} 个卡密', 'success')
        return redirect(url_for('keys_page'))

    # 获取筛选参数
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 构建查询
    query = ActivationKey.query

    if status and status != 'all':
        query = query.filter_by(status=status)

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(ActivationKey.create_time >= start_date)
        except ValueError:
            flash('开始日期格式无效', 'warning')

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # 结束日期包括一整天
            end_date = end_date + timedelta(days=1)
            query = query.filter(ActivationKey.create_time < end_date)
        except ValueError:
            flash('结束日期格式无效', 'warning')

    keys = query.order_by(ActivationKey.create_time.desc()).all()

    return render_template('keys.html', keys=keys, active_page='keys')


@app.route('/keys/<int:key_id>/toggle', methods=['POST'])
@login_required
def toggle_key(key_id):
    key = ActivationKey.query.get(key_id)
    if not key:
        flash('卡密未找到', 'danger')
        return redirect(url_for('keys_page'))

    if key.status == '已禁用':
        key.status = '未使用' if not key.use_time else '已激活'
        action = '启用'
    else:
        key.status = '已禁用'
        action = '禁用'

    db.session.commit()
    flash(f'卡密已{action}', 'success')
    return redirect(url_for('keys_page'))


@app.route('/keys/<int:key_id>/delete', methods=['POST'])
@login_required
def delete_key(key_id):
    key = ActivationKey.query.get(key_id)
    if not key:
        flash('卡密未找到', 'danger')
        return redirect(url_for('keys_page'))

    db.session.delete(key)
    db.session.commit()
    flash('卡密已删除', 'success')
    return redirect(url_for('keys_page'))


@app.route('/versions', methods=['GET', 'POST'])
@login_required
def versions_page():
    if request.method == 'POST':
        # 添加新版本
        data = request.get_json()
        version_number = data['version_number']
        release_date = data['release_date']
        download_url = data['download_url']
        changelog = data['changelog']
        force_update = data['force_update']
        set_active = data['set_active']
        # 检查版本号是否已存在
        if SoftwareVersion.query.filter_by(version_number=version_number).first():
            flash('版本号已存在', 'danger')
            return redirect(url_for('versions_page'))

        try:
            # 转换日期格式
            release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
        except ValueError:
            flash('发布日期格式无效，请使用 YYYY-MM-DD 格式', 'danger')
            return redirect(url_for('versions_page'))

        version = SoftwareVersion(
            version_number=version_number,
            release_date=release_date,
            download_url=download_url,
            changelog=changelog,
            force_update=force_update
        )

        db.session.add(version)

        if set_active:
            # 将所有其他版本设为非激活
            SoftwareVersion.query.update({SoftwareVersion.is_active: False})
            version.is_active = True

        db.session.commit()
        flash('版本添加成功', 'success')
        return redirect(url_for('versions_page'))

    # 获取当前激活版本
    active_version = SoftwareVersion.query.filter_by(is_active=True).first()

    # 获取所有版本
    versions = SoftwareVersion.query.order_by(SoftwareVersion.create_time.desc()).all()

    return render_template('versions.html',
                           active_version=active_version,
                           versions=versions,
                           active_page='versions')


@app.route('/versions/<int:version_id>/set_active', methods=['POST'])
@login_required
def set_active_version(version_id):
    version = SoftwareVersion.query.get(version_id)
    if not version:
        flash('版本未找到', 'danger')
        return redirect(url_for('versions_page'))

    # 将所有版本设为非激活
    SoftwareVersion.query.update({SoftwareVersion.is_active: False})

    # 设置当前版本为激活
    version.is_active = True
    db.session.commit()

    flash(f'已设置 {version.version_number} 为激活版本', 'success')
    return redirect(url_for('versions_page'))


@app.route('/versions/<int:version_id>/delete', methods=['POST'])
@login_required
def delete_version(version_id):
    version = SoftwareVersion.query.get(version_id)
    if not version:
        flash('版本未找到', 'danger')
        return redirect(url_for('versions_page'))

    # 如果删除的是激活版本，需要设置另一个版本为激活
    if version.is_active:
        # 设置最新版本为激活
        latest = SoftwareVersion.query.order_by(SoftwareVersion.create_time.desc()).first()
        if latest and latest.id != version_id:
            latest.is_active = True

    db.session.delete(version)
    db.session.commit()
    flash('版本已删除', 'success')
    return redirect(url_for('versions_page'))


@app.route('/announcements', methods=['GET', 'POST'])
@login_required
def announcements_page():
    if request.method == 'POST':
        # 添加新公告

        data = request.get_json()
        title = data['title']
        content = data['content']
        is_active = data['isActive']

        announcement = Announcement(
            title=title,
            content=content,
            is_active=is_active
        )

        db.session.add(announcement)
        db.session.commit()
        flash('公告添加成功', 'success')
        return redirect(url_for('announcements_page'))

    # 获取所有公告
    announcements = Announcement.query.order_by(Announcement.publish_time.desc()).all()

    # 统计信息
    total_announcements = Announcement.query.count()
    active_announcements = Announcement.query.filter_by(is_active=True).count()
    inactive_announcements = total_announcements - active_announcements

    return render_template('announcements.html',
                           announcements=announcements,
                           total_announcements=total_announcements,
                           active_announcements=active_announcements,
                           inactive_announcements=inactive_announcements,
                           active_page='announcements')


@app.route('/announcements/<int:announcement_id>/toggle', methods=['POST'])
@login_required
def toggle_announcement(announcement_id):
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        flash('公告未找到', 'danger')
        return redirect(url_for('announcements_page'))

    announcement.is_active = not announcement.is_active
    db.session.commit()

    status = "激活" if announcement.is_active else "停用"
    flash(f'公告已{status}', 'success')
    return redirect(url_for('announcements_page'))


@app.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        flash('公告未找到', 'danger')
        return redirect(url_for('announcements_page'))

    db.session.delete(announcement)
    db.session.commit()
    flash('公告已删除', 'success')
    return redirect(url_for('announcements_page'))


@app.route('/usage')
@login_required
def usage_page():
    # 获取筛选参数
    search = request.args.get('search', '')
    date_filter = request.args.get('date', '')

    # 构建查询
    query = UsageRecord.query

    if search:
        # 关联卡密表查询
        from sqlalchemy import or_
        query = query.join(ActivationKey).filter(
            or_(
                ActivationKey.key_value.contains(search),
                UsageRecord.ip_address.contains(search)
            )
        )

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            start_date = datetime.combine(filter_date, datetime.min.time())
            end_date = datetime.combine(filter_date, datetime.max.time())
            query = query.filter(UsageRecord.access_time.between(start_date, end_date))
        except ValueError:
            flash('日期格式无效，请使用 YYYY-MM-DD 格式', 'warning')

    usage_records = query.order_by(UsageRecord.access_time.desc()).all()

    # 地域分布数据（模拟）
    location_distribution = [
        {'name': '北京市', 'count': 352},
        {'name': '上海市', 'count': 287},
        {'name': '广州市', 'count': 215},
        {'name': '深圳市', 'count': 198},
        {'name': '成都市', 'count': 156}
    ]

    # 时间段分布（模拟）
    time_distribution = [
        {'period': '00:00-06:00', 'percentage': 12},
        {'period': '06:00-12:00', 'percentage': 28},
        {'period': '12:00-18:00', 'percentage': 35},
        {'period': '18:00-24:00', 'percentage': 25}
    ]

    return render_template('usage.html',
                           usage_records=usage_records,
                           location_distribution=location_distribution,
                           time_distribution=time_distribution,
                           active_page='usage')


import platform
import subprocess
def get_system_uuid():
    system = platform.system()
    if system == "Windows":
        import wmi
        c = wmi.WMI()
        return c.Win32_ComputerSystemProduct()[0].UUID
    elif system == "Linux":
        with open("/sys/class/dmi/id/product_uuid", "r") as f:
            return f.read().strip()
    elif system == "Darwin":  # macOS
        cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
        return subprocess.check_output(cmd, shell=True).decode().split('"')[3]
    else:
        return "Unsupported OS"


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    key_value = data.get('key_value')
    print(key_value)
    machine_code = data.get('machine_code')

    if not key_value or not machine_code:
        return jsonify({'status': 'error', 'message': '参数错误'}), 400

    # 查询卡密
    key = ActivationKey.query.filter_by(key_value=key_value).first()
    if not key:
        return jsonify({'status': 'error', 'message': '卡密不存在'}), 404

    key_dict = key.to_dict()

    # 检查机器码是否匹配
    if key_dict['machine_code'] != machine_code:
        return jsonify({'status': 'error', 'message': '机器码不匹配'}), 403

    # 检查卡密状态
    if key_dict['status'] != "已激活":
        return jsonify({'status': 'error', 'message': '卡密状态无效'}), 403

    # 检查有效期
    expire_time = key_dict['expire_time']
    if expire_time < datetime.now():
        return jsonify({'status': 'error', 'message': '卡密已过期'}), 403

    # 更新最后使用时间
    key.use_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.commit()

    return jsonify({'status': 'success', 'message': '验证通过'}), 200
@app.route('/keyvalue/<key_value>', methods=['GET'])
def get_key(key_value):
    key = ActivationKey.query.filter_by(key_value=key_value).first()
    if not key:
        return jsonify({'error': '卡密不存在'}), 404
    new_key = ActivationKey(**key.to_dict())
    print(new_key)
    if key.to_dict()['status']=="未使用":
        new_key.expire_time=(datetime.now()+timedelta(hours=int(key.to_dict()['duration']))).strftime("%Y-%m-%d %H:%M:%S")
        new_key.machine_code =uuid.getnode()
        new_key.status = "已激活"
    if key.to_dict()['status']=="已禁用":
        return jsonify({'error': '卡密禁用'}), 404
    if key.to_dict()['status']=="已激活" and key.to_dict()['expire_time'] < datetime.strptime(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"):
        return jsonify({'error': '卡密过期'}), 404
    if key.to_dict()['machine_code'] and key.to_dict()['machine_code']==uuid.getnode() :
        return jsonify({'error': '已绑定其他机器码'}), 404
    new_key.use_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.merge(new_key)
    db.session.commit()
    print(new_key.to_dict())
    return jsonify({'data':new_key.to_dict()}), 200

@app.route('/message', methods=['GET'])
def get_message():
    try:
        announcements = Announcement.query.filter(
            Announcement.is_active == True
        ).order_by(
            Announcement.id.desc()
        ).all()[0]
    except Exception as e:
        return jsonify({'error': "暂无公告或获取公告出错"}), 404
    return jsonify({'data':announcements.to_dict()}), 200

@app.route('/ver', methods=['GET'])
def get_ver():
    ver = SoftwareVersion.query.filter(
        SoftwareVersion.is_active == 1
    ).order_by(
        SoftwareVersion.id.desc()
    ).all()[0]
    return jsonify({'data':ver.to_dict()}), 200


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')


# 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
def create_admin_user():
    try:
        with app.app_context():
            # 检查管理员账户是否存在
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin')
                admin.set_password('admin123')  # 默认密码
                db.session.add(admin)
                db.session.commit()
                print("创建默认管理员账户: admin/admin123")
            else:
                print("管理员账户已存在")
    except Exception as e:
        print(f"创建管理员账户时出错: {e}")


if __name__ == '__main__':
    create_admin_user()
    app.run(debug=True)