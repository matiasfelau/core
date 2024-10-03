import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def initialize_logging_for_messaging_errors():
    """
    Inicializa el sistema de logeo para los errores de mensajería, los cuales se almacenarán en archivos.
    :return: Devuelve un manejador que requiere la aplicación para poder realizar los logs.
    """
    #path = './ar.edu.uade.core/resources/logs/'
    #path = '/app/data/logs'
    path = '/core_disk/data/logs'
    #check_path(path)
    handler = TimedRotatingFileHandler(path + f'/{get_date()}.log', when='midnight', interval=1)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('[%(asctime)s] %(message)s')
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


def log_messaging_error(app, reason, origin, destination, case):
    """
    Realiza un log de un error de mensajería.
    :param app: Requiere a la aplicación.
    :param reason: Requiere la razón de descarte que se obtiene con get_death_reason().
    :param origin: Requiere el origen del que proviene el mensaje, obtenido de su cuerpo.
    :param destination: Requiere el destino al que se dirigía el mensaje, obtenido de su cuerpo.
    :param case: Requiere el caso de uso por el que existe el mensaje, obtenido de su cuerpo.
    :return:
    """
    mensaje = f'{reason}: {origin} -> {destination} ({case})'
    app.logger.warning(mensaje)


def get_death_reason(headers):
    """
    Obtiene el contador de muertes de un mensaje.
    :param headers: Requiere los headers del mensaje.
    :return: Devuelve el contador de muertes del mensaje.
    """
    return headers['x-death'][0]['reason']

