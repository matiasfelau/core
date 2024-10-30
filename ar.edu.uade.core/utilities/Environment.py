import os

from utilities.Enumerations import PossibleKeysForEnvironmentVariables


def get_environment_variables():
    """
    Obtiene una matriz que contiene a los pares key-value del entorno.
    :return: Devuelve a la matriz que contenga las variables de entorno o None si ocurrió una excepción.
    """
    try:
        environment_variables = (
            (PossibleKeysForEnvironmentVariables.FLASK_HOST.value,
             os.getenv('FLASK_HOST', '127.0.0.1')),
            (PossibleKeysForEnvironmentVariables.FLASK_PORT.value,
             int(os.getenv('FLASK_PORT', 5000))),
            (PossibleKeysForEnvironmentVariables.WEBSOCKET_SECRET_KEY.value,
             os.getenv('WEBSOCKET_SECRET_KEY')),
            (PossibleKeysForEnvironmentVariables.RABBITMQ_HOST.value,
             os.getenv('RABBITMQ_HOST', 'rabbitmq')),
            (PossibleKeysForEnvironmentVariables.RABBITMQ_PORT.value,
             os.getenv('RABBITMQ_PORT', 5672)),
            (PossibleKeysForEnvironmentVariables.RABBITMQ_USERNAME.value,
             os.getenv('RABBITMQ_USERNAME')),
            (PossibleKeysForEnvironmentVariables.RABBITMQ_PASSWORD.value,
             os.getenv('RABBITMQ_PASSWORD')),
            (PossibleKeysForEnvironmentVariables.CONFIGURATION_FILE_PATH.value,
             os.getenv('CONFIGURATION_PATH', '/core_data/resources/config.ini')),
            (PossibleKeysForEnvironmentVariables.LOGS_PATH.value,
             os.getenv('LOGS_PATH', '/core_data/logs')),
            (PossibleKeysForEnvironmentVariables.ENVIRONMENT.value,
             os.getenv('ENVIRONMENT', 'test'))
        )
        return environment_variables
    except Exception as e:
        print(f'\nError in utilities.Environment.get_environment_variables(): \n{str(e)}')
        return None


def check_void_environment_variables(environment_variables):
    """
    Indica por terminal que variables de entorno no fueron definidas.
    :param environment_variables: Requiere la matriz de variables de entorno obtenida con get_environment_variables()
    :return:
    """
    try:
        for t in environment_variables:
            if t[1] is None:
                print(f'\nEnvironment variable {t[0]} is not set')
    except Exception as e:
        print(f'\nError in utilities.Environment.check_void_environment_variables(): \n{str(e)}')


def get_value_from_environment_variable(environment_variables, key):
    """
    Obtiene el valor asignado a una variable de entorno.
    :param environment_variables: Requiere la matriz de variables de entorno obtenida con get_environment_variables().
    :param key: Requiere la key de la variable de entorno de la que se quiere obtener el valor.
    :return: Devuelve el valor asignado a la key o None si ocurrió una excepción.
    """
    try:
        for t in environment_variables:
            if t[0] == key:
                return t[1]
    except Exception as e:
        print(f'\nError in utilities.Environment.get_value_from_environment_variable(): \n{str(e)}')
        return None
