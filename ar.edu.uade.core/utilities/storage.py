from utilities.Configuration import initialize_configuration_reader
from utilities.Environment import get_environment_variables, get_value_from_environment_variable

environment_variables = get_environment_variables()

rabbitmq_host = get_value_from_environment_variable(environment_variables, 'RABBITMQ_HOST')

rabbitmq_port = get_value_from_environment_variable(environment_variables, 'RABBITMQ_PORT')

rabbitmq_user_username = get_value_from_environment_variable(environment_variables, 'RABBITMQ_USER')

rabbitmq_user_password = get_value_from_environment_variable(environment_variables, 'RABBITMQ_PASSWORD')

reader = initialize_configuration_reader(
    get_value_from_environment_variable(environment_variables, 'CONFIGURATION_PATH'))

