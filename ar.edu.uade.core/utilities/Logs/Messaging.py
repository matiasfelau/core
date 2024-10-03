import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def initialize_logging_for_messaging_errors():
    """
    Inicializa el sistema de logeo para los errores de mensajería, los cuales se almacenarán en archivos.
    :return: Devuelve un manejador que requiere la aplicación para poder realizar los logs.
    """
    check_path('resources/logs/messaging/')
    handler = TimedRotatingFileHandler(f'resources/logs/messaging/{get_date()}.log', when='midnight', interval=1)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('[%(timestamp)s] %(reason.upper)s: %(origin)s - %(destination)s - %(case)s')
    handler.setFormatter(formatter)
    return handler


def check_path(path):
    """
    Revisa que una ruta exista y si no la crea.
    :param path: Requiere la ruta a evaluar.
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_date():
    """
    Obtiene la fecha actual del sistema.
    :return: Devuelve la fecha actual del sistema.
    """
    return datetime.now().date()


def log_messaging_error(app, timestamp, reason, origin, destination, case):
    """
    Realiza un log de un error de mensajería.
    :param app: Requiere a la aplicación.
    :param timestamp: Requiere la marca temporal del mensaje que se obtiene con get_death_timestamp().
    :param reason: Requiere la razón de descarte que se obtiene con get_death_reason().
    :param origin: Requiere el origen del que proviene el mensaje, obtenido de su cuerpo.
    :param destination: Requiere el destino al que se dirigía el mensaje, obtenido de su cuerpo.
    :param case: Requiere el caso de uso por el que existe el mensaje, obtenido de su cuerpo.
    :return:
    """
    app.logger.warning('', extra={
        'timestamp': timestamp,
        'reason': reason,
        'origin': origin,
        'destination': destination,
        'case': case})


def get_death_reason(headers):
    """
    Obtiene el contador de muertes de un mensaje.
    :param headers: Requiere los headers del mensaje.
    :return: Devuelve el contador de muertes del mensaje.
    """
    return headers['x-death'][0]['reason']


def get_death_timestamp(headers):
    """
    Obtiene el momento en el que un mensaje fue descartado de alguna cola principal.
    :param headers: Requiere los headers del mensaje.
    :return: Devuelve la marca temporal del momento en el que se descartó el mensaje.
    """
    return headers['x-death'][0]['last-time']
