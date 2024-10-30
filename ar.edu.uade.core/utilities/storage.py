from utilities.Configuration import initialize_configuration_reader
from utilities.Enumerations import PossibleKeysForEnvironmentVariables
from utilities.Environment import get_environment_variables, get_value_from_environment_variable

environment_variables = get_environment_variables()

rabbitmq_host = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.RABBITMQ_HOST.value
)

rabbitmq_port = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.RABBITMQ_PORT.value
)

rabbitmq_user_username = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.RABBITMQ_USERNAME.value
)

rabbitmq_user_password = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.RABBITMQ_PASSWORD.value
)

rabbitmq_management_port = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.RABBITMQ_MANAGEMENT_PORT.value
)

environment = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.ENVIRONMENT.value
)

reader = initialize_configuration_reader(
    get_value_from_environment_variable(
        environment_variables,
        PossibleKeysForEnvironmentVariables.CONFIGURATION_PATH.value)
)

