import logging


def initialize_logging_for_application_errors():
    """
    Inicializa el sistema de logeo para los errores de aplicación por consola.
    :return: Devuelve un manejador que requiere la aplicación para poder realizar los logs.
    """
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    return handler


def log_application_error(app, message):
    """
    Realiza un log por consola de un error de la aplicación.
    :param app: Requiere a la aplicación.
    :param message: Requiere el cuerpo del mensaje que se imprimirá por consola.
    :return:
    """
    app.logger.error(message)
