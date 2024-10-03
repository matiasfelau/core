import os

from utilities.Logs.Application import log_application_error


def get_environment_variables(app):
    """
    Obtiene una matriz que contiene a los pares key-value del entorno.
    :param app: Requiere a la aplicación para realizar logs por consola.
    :return: Devuelve a la matriz que contenga las variables de entorno o None si ocurrió una excepción.
    """
    try:
        environment_variables = (
            ('host', os.getenv('FLASK_HOST', '127.0.0.1')),
            ('port', int(os.getenv('FLASK_PORT', 5000))),
            ('secret_key', os.getenv('SECRET_KEY'))
        )
        return environment_variables
    except Exception:
        log_application_error(app, 'Unknown error happened in utilities.System.get_environment_variables')
        return None


def check_void_environment_variables(app, environment_variables):
    """
    Indica por terminal que variables de entorno no fueron definidas.
    :param app: Requiere a la aplicación para realizar logs por consola.
    :param environment_variables: Requiere la matriz de variables de entorno obtenida con get_environment_variables()
    :return:
    """
    try:
        for t in environment_variables:
            if t[1] is None:
                print(f'\nEnvironment variable {t[0]} is not set')
    except IndexError:
        log_application_error(app, 'Invalid evaluated position in utilities.System.check_void_environment_variables')
    except Exception:
        log_application_error(app, 'Unknown error happened in utilities.System.check_void_environment_variables')


def get_value_from_environment_variable(app, environment_variables, key):
    """
    Obtiene el valor asignado a una variable de entorno.
    :param app: Requiere a la aplicación para realizar logs por consola.
    :param environment_variables: Requiere la matriz de variables de entorno obtenida con get_environment_variables().
    :param key: Requiere la key de la variable de entorno de la que se quiere obtener el valor.
    :return: Devuelve el valor asignado a la key o None si ocurrió una excepción.
    """
    try:
        for t in environment_variables:
            if t[0] == key:
                return t[1]
    except IndexError:
        log_application_error(app, 'Invalid evaluated position in utilities.System.get_value_from_environment_variable')
        return None
    except Exception:
        log_application_error(app, 'Unknown error happened in utilities.System.get_value_from_environment_variable')
        return None
