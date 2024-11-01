from enum import Enum


class PossiblePublishers(Enum):
    """

    """
    E_COMMERCE = 'e_commerce'
    GESTION_FINANCIERA = 'gestion_financiera'
    GESTION_INTERNA = 'gestion_interna'
    USUARIO = 'usuario'
    AUTENTICACION = 'autenticacion'


class PossibleKeysForEnvironmentVariables(Enum):
    """

    """
    FLASK_HOST = 'flask_host'
    FLASK_PORT = 'flask_port'
    WEBSOCKET_SECRET_KEY = 'websocket_secret_key'
    RABBITMQ_HOST = 'rabbitmq_host'
    RABBITMQ_PORT = 'rabbitmq_port'
    RABBITMQ_USERNAME = 'rabbitmq_username'
    RABBITMQ_PASSWORD = 'rabbitmq_password'
    CONFIGURATION_PATH = 'configuration_path'
    LOGS_PATH = 'logs_path'
    ENVIRONMENT = 'environment'
    RABBITMQ_MANAGEMENT_PORT = 'rabbitmq_management_port'


class PossibleKeysForPublisherConfiguration(Enum):
    """

    """
    MAX_RETRIES = 'max_retries'
    MIN_TTL = 'min_ttl'
