from flask import Blueprint, request, jsonify
from managers.usage_manager import UsageManager
from datetime import datetime

usage_bp = Blueprint('usage', __name__)


@usage_bp.route('/usage', methods=['POST'])
def create_record():
    data = request.json
    key_id = data.get('key_id')
    ip_address = data.get('ip_address')
    software_version = data.get('software_version')
    location = data.get('location')

    record = UsageManager.create_record(key_id, ip_address, software_version, location)
    return jsonify(record.to_dict()), 201


@usage_bp.route('/usage', methods=['GET'])
def get_records():
    key_value = request.args.get('key')
    ip_address = request.args.get('ip')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 转换日期参数
    start_date = datetime.fromisoformat(start_date) if start_date else None
    end_date = datetime.fromisoformat(end_date) if end_date else None

    records = UsageManager.search_records(key_value, ip_address, start_date, end_date)
    return jsonify([record.to_dict() for record in records])


@usage_bp.route('/usage/export', methods=['GET'])
def export_records():
    records = UsageManager.export_records()
    # 在实际应用中，这里应该生成CSV文件并返回下载
    return jsonify(records)


@usage_bp.route('/usage/key/<int:key_id>', methods=['GET'])
def get_records_by_key(key_id):
    records = UsageManager.get_records_by_key(key_id)
    return jsonify([record.to_dict() for record in records])