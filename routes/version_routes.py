from flask import Blueprint, request, jsonify
from managers.version_manager import VersionManager
from models.version_model import SoftwareVersion
from datetime import datetime

version_bp = Blueprint('versions', __name__)


@version_bp.route('/versions', methods=['POST'])
def create_version():
    data = request.json
    version_number = data.get('version_number')
    release_date = datetime.fromisoformat(data.get('release_date'))
    download_url = data.get('download_url')
    changelog = data.get('changelog')
    force_update = data.get('force_update', False)
    set_active = data.get('set_active', False)

    version, message = VersionManager.create_version(
        version_number,
        release_date,
        download_url,
        changelog,
        force_update,
        set_active
    )

    if version:
        return jsonify({
            'message': message,
            'version': version.to_dict()
        }), 201
    return jsonify({'error': message}), 400


@version_bp.route('/versions', methods=['GET'])
def get_versions():
    versions = VersionManager.get_all_versions()
    return jsonify([version.to_dict() for version in versions])


@version_bp.route('/versions/active', methods=['GET'])
def get_active_version():
    version = VersionManager.get_active_version()
    if version:
        return jsonify(version.to_dict())
    return jsonify({'error': '未找到激活版本'}), 404


@version_bp.route('/versions/latest', methods=['GET'])
def get_latest_version():
    version = VersionManager.get_latest_version()
    if version:
        return jsonify(version.to_dict())
    return jsonify({'error': '未找到版本'}), 404


@version_bp.route('/versions/<int:version_id>', methods=['GET'])
def get_version(version_id):
    version = VersionManager.get_version_by_id(version_id)
    if version:
        return jsonify(version.to_dict())
    return jsonify({'error': '版本未找到'}), 404


@version_bp.route('/versions/<int:version_id>', methods=['PUT'])
def update_version(version_id):
    data = request.json
    version = VersionManager.update_version(version_id, **data)
    if version:
        return jsonify(version.to_dict())
    return jsonify({'error': '版本未找到'}), 404


@version_bp.route('/versions/<int:version_id>/set-active', methods=['PUT'])
def set_active_version(version_id):
    if VersionManager.set_active_version(version_id):
        return jsonify({'message': '版本已设置为激活'})
    return jsonify({'error': '版本未找到'}), 404


@version_bp.route('/versions/<int:version_id>', methods=['DELETE'])
def delete_version(version_id):
    if VersionManager.delete_version(version_id):
        return jsonify({'message': '版本已删除'})
    return jsonify({'error': '版本未找到'}), 404