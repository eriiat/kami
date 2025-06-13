from flask import Blueprint, request, jsonify
from managers.key_manager import KeyManager
from models.key_model import ActivationKey
from utils.database import db
from datetime import datetime

key_bp = Blueprint('keys', __name__)


@key_bp.route('/keys', methods=['POST'])
def create_keys():
    data = request.json
    count = data.get('count', 1)
    duration = data.get('duration', 365)
    remarks = data.get('remarks')
    creator = data.get('creator', 'admin')

    keys = KeyManager.create_key(duration, count, remarks, creator)
    return jsonify({
        'message': f'成功生成 {count} 个卡密',
        'keys': [key.key_value for key in keys]
    }), 201


@key_bp.route('/keys', methods=['GET'])
def get_keys():
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    creator = request.args.get('creator')

    # 转换日期参数
    start_date = datetime.fromisoformat(start_date) if start_date else None
    end_date = datetime.fromisoformat(end_date) if end_date else None

    keys = KeyManager.search_keys(status, start_date, end_date, creator)
    return jsonify([key.to_dict() for key in keys])


@key_bp.route('/keys/<int:key_id>', methods=['GET'])
def get_key(key_id):
    key = KeyManager.get_key_by_id(key_id)
    if key:
        return jsonify(key.to_dict())
    return jsonify({'error': '卡密未找到'}), 404


@key_bp.route('/keys/<int:key_id>', methods=['PUT'])
def update_key(key_id):
    data = request.json
    key = KeyManager.update_key(key_id, **data)
    if key:
        return jsonify(key.to_dict())
    return jsonify({'error': '卡密未找到'}), 404


@key_bp.route('/keys/<int:key_id>/disable', methods=['PUT'])
def disable_key(key_id):
    if KeyManager.disable_key(key_id):
        return jsonify({'message': '卡密已禁用'})
    return jsonify({'error': '卡密未找到'}), 404


@key_bp.route('/keys/<int:key_id>/enable', methods=['PUT'])
def enable_key(key_id):
    if KeyManager.enable_key(key_id):
        return jsonify({'message': '卡密已启用'})
    return jsonify({'error': '卡密未找到'}), 404


@key_bp.route('/keys/<int:key_id>', methods=['DELETE'])
def delete_key(key_id):
    if KeyManager.delete_key(key_id):
        return jsonify({'message': '卡密已删除'})
    return jsonify({'error': '卡密未找到'}), 404


@key_bp.route('/keys/activate', methods=['POST'])
def activate_key():
    data = request.json
    key_value = data.get('key_value')
    machine_code = data.get('machine_code')

    success, message = KeyManager.activate_key(key_value, machine_code)
    if success:
        key = KeyManager.get_key_by_value(key_value)
        return jsonify({
            'message': message,
            'key': key.to_dict()
        })
    return jsonify({'error': message}), 400