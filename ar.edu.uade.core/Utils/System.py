import os
from os import environ


def get_environment_variables():
    """
    obtiene las variables de entorno
    :return: tupla con las variables host, port, secretKey
    """
    try:
        environment_variables = (
            ('HOST', os.getenv('FLASK_HOST', '127.0.0.1')),
            ('PORT', int(os.getenv('FLASK_PORT', 5000))),
            ('SECRET_KEY', os.getenv('SECRET_KEY'))
        )
        if environment_variables[2] is None:
            raise ReferenceError('Environment variable SECRET_KEY is not set')
        return environment_variables
    except IndexError as i:
        print('Invalid evaluated position in Utils.System.get_environment_variables')
        return None
    except ReferenceError as r:
        return None
    except Exception as e:
        print('Unknown error happened in Utils.System.get_environment_variables')
        return None