from flask import Blueprint, jsonify, request

from brokers.RabbitMQ import start_rabbitmq_connection, end_rabbitmq_connection
from queues.Publisher import initialize_publisher, initialize_publisher_retry_queues
from utilities import storage
from utilities.Configuration import initialize_configuration_reader, read_configuration_attribute, \
    write_in_configuration_file
from utilities.Environment import get_value_from_environment_variable, get_environment_variables
from utilities.Management import create_auxiliary_queue, delete_queue_binding_with_exchange, delete_queue, \
    transfer_messages

retry_queues = Blueprint('retry_queues', __name__)


#TODO confirmar que el reader no necesita volver a inicializarse
@retry_queues.route('/retry_queues', methods=['GET'])
def change_retrying_configuration():
    """

    :return:
    """
    try:
        module = request.args.get('module')
        attribute = request.args.get('attribute')
        value = request.args.get('value')
        old_value = read_configuration_attribute(storage.reader, module, attribute)
        write_in_configuration_file(storage.reader, module, attribute, value)
        if read_configuration_attribute(storage.reader, module, attribute) == value:
            connection, channel = start_rabbitmq_connection(
                storage.rabbitmq_user_username,
                storage.rabbitmq_user_password,
                storage.rabbitmq_host,
                storage.rabbitmq_port
            )
            if attribute == 'TTL':
                queues_quantity = read_configuration_attribute(storage.reader, module, 'QTY')
                for i in range(queues_quantity):
                    delete_retry_queue(channel, i, module)
                initialize_publisher_retry_queues(
                    channel,
                    module,
                    queues_quantity,
                    value
                )
                for i in range(queues_quantity):
                    source = f'{module}.auxiliary{i}'
                    target = f'{module}.retry{i}'
                    transfer_messages(
                        module,
                        source,
                        target,
                        storage.rabbitmq_host,
                        storage.rabbitmq_port,
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password
                    )
                    delete_queue(
                        source,
                        storage.rabbitmq_host,
                        storage.rabbitmq_port,
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password
                    )
            else:
                if value > old_value:
                    initialize_publisher_retry_queues(
                        channel,
                        module,
                        max_retries=value,
                        min_ttl=read_configuration_attribute(storage.reader, module, 'TTL'),
                        offset=old_value + 1
                    )
                else:  #TODO avisarle a toms que avise antes de cambiar la cantidad que los mensajes iran a dlx
                    queues_quantity = old_value
                    for i in range(queues_quantity - value):
                        source = f'{module}.retry{old_value}'
                        target = f'{module}.dead-letter'
                        transfer_messages(
                            module,
                            source,
                            target,
                            storage.rabbitmq_host,
                            storage.rabbitmq_port,
                            storage.rabbitmq_user_username,
                            storage.rabbitmq_user_password
                        )
                        delete_retry_queue(channel, old_value, module)
                        old_value -= 1
            end_rabbitmq_connection(connection)
            return True
        else:
            return False
    except Exception as e:
        print(f'\nError in routes.retry_queues(): \n{str(e)}')


def delete_retry_queue(channel, i, module):
    create_auxiliary_queue(channel, module, i)
    target = f'{module}.retry{i}'
    delete_queue_binding_with_exchange(
        module,
        target,
        target,
        storage.rabbitmq_host,
        storage.rabbitmq_port,
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password
    )  # TODO ver el tema de los nombres de target
    source = f'{module}.auxiliary{i}'
    transfer_messages(
        module,
        target,
        source,
        storage.rabbitmq_host,
        storage.rabbitmq_port,
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password
    )
    delete_queue(
        target,
        storage.rabbitmq_host,
        storage.rabbitmq_port,
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password
    )
