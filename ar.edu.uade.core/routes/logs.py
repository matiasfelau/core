from flask import Blueprint

logs = Blueprint('logs', __name__)

@logs.route('/logs', methods=['GET'])
def get_logs():
    pass