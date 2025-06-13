from flask import Blueprint, request, jsonify
from managers.announcement_manager import AnnouncementManager

announcement_bp = Blueprint('announcements', __name__)


@announcement_bp.route('/announcements', methods=['POST'])
def create_announcement():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    is_active = data.get('is_active', True)

    announcement = AnnouncementManager.create_announcement(title, content, is_active)
    return jsonify(announcement.to_dict()), 201


@announcement_bp.route('/announcements', methods=['GET'])
def get_announcements():
    announcements = AnnouncementManager.get_all_announcements()
    return jsonify([ann.to_dict() for ann in announcements])


@announcement_bp.route('/announcements/active', methods=['GET'])
def get_active_announcements():
    announcements = AnnouncementManager.get_active_announcements()
    return jsonify([ann.to_dict() for ann in announcements])


@announcement_bp.route('/announcements/<int:announcement_id>', methods=['GET'])
def get_announcement(announcement_id):
    announcement = AnnouncementManager.get_announcement_by_id(announcement_id)
    if announcement:
        return jsonify(announcement.to_dict())
    return jsonify({'error': '公告未找到'}), 404


@announcement_bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
def update_announcement(announcement_id):
    data = request.json
    announcement = AnnouncementManager.update_announcement(announcement_id, **data)
    if announcement:
        return jsonify(announcement.to_dict())
    return jsonify({'error': '公告未找到'}), 404


@announcement_bp.route('/announcements/<int:announcement_id>/toggle', methods=['PUT'])
def toggle_announcement(announcement_id):
    if AnnouncementManager.toggle_announcement(announcement_id):
        return jsonify({'message': '公告状态已切换'})
    return jsonify({'error': '公告未找到'}), 404


@announcement_bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
def delete_announcement(announcement_id):
    if AnnouncementManager.delete_announcement(announcement_id):
        return jsonify({'message': '公告已删除'})
    return jsonify({'error': '公告未找到'}), 404