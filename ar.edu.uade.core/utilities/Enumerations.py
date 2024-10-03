from enum import Enum


class PossiblePublishers(Enum):
    """

    """
    E_COMMERCE = 'e_commerce'
    GESTION_FINANCIERA = 'gestion_financiera'
    GESTION_INTERNA = 'gestion_interna'
    USUARIO = 'usuario'


class PossibleKeysForEnvironmentVariables(Enum):
    """

    """
    HOST = 'host'
    PORT = 'port'
    SECRET_KEY = 'secret_key'


class PossibleKeysForPublisherConfiguration(Enum):
    """

    """
    MAX_RETRIES = 'max_retries'
    MIN_TTL = 'min_ttl'
