from flask import Blueprint, request

from utilities import storage
from utilities.Environment import get_value_from_environment_variable
from utilities.Logger import filtrar_lineas

logs = Blueprint('logs', __name__)


@logs.route('/logs', methods=['GET'])
def get_logs():
    filtro = request.args.get('filtro')
    campo = request.args.get('campo')
    offset = request.args.get('offset')
    return filtrar_lineas(
        get_value_from_environment_variable(storage.environment_variables, 'LOGS_PATH'),
        filtro,
        campo,
        offset
    )
