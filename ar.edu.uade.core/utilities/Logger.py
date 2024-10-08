import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from utilities.Files import check_create_path
from utilities.Utilities import check_void_parameter

PATH = '/core_data/logs'


def initialize_logging_for_messaging_errors(path='/core_data/logs'):
    """
    Inicializa el sistema de logeo para los errores de mensajería, los cuales se almacenarán en archivos.
    :return: Devuelve un manejador que requiere la aplicación para poder realizar los logs o None si ocurrió una excepción.
    """
    try:
        path = check_void_parameter(path, PATH)
        check_create_path(path)

        #Inicializa un handler que crea un nuevo archivo con el cambio de fecha
        handler = TimedRotatingFileHandler(path + f'/{datetime.now().date()}.log', when='midnight', interval=1)

        #Define el tipo de logs que manejará este handler
        handler.setLevel(logging.ERROR)

        #Define el formato en el que se harán los logs
        formatter = logging.Formatter('[%(asctime)s] %(message)s')

        #Fija el formato al handler
        handler.setFormatter(formatter)

        return handler
    except Exception as e:
        print(f'\nError in utilities.logger.initialize_logging_for_messaging_errors(): \n{str(e)}')
        return None


def log_messaging_error(app, reason, origin, destination, case):
    """
    Realiza un log de un error de mensajería.
    :param app: Requiere una instancia de la aplicación para hacer logs.
    :param reason: Requiere la razón de descarte que se obtiene con get_death_reason().
    :param origin: Requiere el origen del que proviene el mensaje, obtenido de su cuerpo.
    :param destination: Requiere el destino al que se dirigía el mensaje, obtenido de su cuerpo.
    :param case: Requiere el caso de uso por el que existe el mensaje, obtenido de su cuerpo.
    :return:
    """
    try:
        #Integra todas las variables en el mensaje de log
        mensaje = f'{reason}: {origin} -> {destination} ({case})'

        #Realiza el log
        app.logger.warning(mensaje)

    except Exception as e:
        print(f'\nError in utilities.logger.log_messaging_error(): \n{str(e)}')
