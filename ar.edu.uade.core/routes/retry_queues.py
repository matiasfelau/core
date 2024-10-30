from flask import Blueprint, jsonify, request

from brokers.RabbitMQ import start_rabbitmq_connection, end_rabbitmq_connection
from queues.Publisher import initialize_publisher, initialize_publisher_retry_queues
from utilities import storage
from utilities.Configuration import initialize_configuration_reader, read_configuration_attribute, \
    write_in_configuration_file, get_int_attribute
from utilities.Environment import get_value_from_environment_variable, get_environment_variables
from utilities.Management import create_auxiliary_queue, delete_queue_binding_with_exchange, delete_queue, \
    transfer_messages

retry_queues = Blueprint('retry_queues', __name__)


@retry_queues.route('/retry_queues', methods=['GET'])
def change_retrying_configuration():
    """

    :return:
    """
    try:
        module = request.args.get('module')
        attribute = request.args.get('attribute')
        value = request.args.get('value')
        actual_ttl = get_int_attribute(storage.reader, module, 'ttl')
        actual_qty = get_int_attribute(storage.reader, module, 'qty')
        if actual_ttl is None:
            write_in_configuration_file(storage.reader, module, 'ttl', '3000')
        if actual_qty is None:
            write_in_configuration_file(storage.reader, module, 'qty', '3')
        old_value = get_int_attribute(storage.reader, module, attribute)
        write_in_configuration_file(storage.reader, module, attribute, value)
        if get_int_attribute(storage.reader, module, attribute) == int(value):
            connection, channel = start_rabbitmq_connection(
                storage.rabbitmq_user_username,
                storage.rabbitmq_user_password,
                storage.rabbitmq_host,
                storage.rabbitmq_port
            )
            if attribute == 'ttl':
                queues_quantity = get_int_attribute(storage.reader, module, 'qty')
                for i in range(1, queues_quantity + 1):
                    source = f'{module}.retry{i}'
                    target = f'{module}.auxiliary{i}'
                    create_auxiliary_queue(channel, module, i)

                    transfer_messages(
                        module,
                        source,
                        target,
                        storage.rabbitmq_host,
                        storage.rabbitmq_management_port,
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password
                    )
                    delete_queue(
                        source,
                        storage.rabbitmq_host,
                        storage.rabbitmq_management_port,
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password
                    )
                initialize_publisher_retry_queues(
                    channel,
                    module,
                    queues_quantity,
                    int(value)
                )
                for i in range(1, queues_quantity + 1):
                    source = f'{module}.auxiliary{i}'
                    target = f'{module}.retry{i}'
                    transfer_messages(
                        module,
                        source,
                        target,
                        storage.rabbitmq_host,
                        storage.rabbitmq_management_port,
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password
                    )
                    delete_queue(
                        source,
                        storage.rabbitmq_host,
                        storage.rabbitmq_management_port,
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password
                    )
            else:
                if int(value) > old_value:
                    initialize_publisher_retry_queues(
                        channel,
                        module,
                        max_retries=int(value),
                        min_ttl=get_int_attribute(storage.reader, module, 'ttl'),
                        offset=old_value + 1
                    )
                else:  #TODO avisarle a toms que avise antes de cambiar la cantidad que los mensajes iran a dlx y que se podrian perder algunos msj
                    queues_quantity = old_value
                    actual_value = queues_quantity
                    for i in range(queues_quantity - int(value)):
                        source = f'{module}.retry{actual_value}'
                        target = f'{module}.dead-letter'
                        transfer_messages(
                            module,
                            source,
                            target,
                            storage.rabbitmq_host,
                            storage.rabbitmq_management_port,
                            storage.rabbitmq_user_username,
                            storage.rabbitmq_user_password
                        )
                        delete_queue(
                            source,
                            storage.rabbitmq_host,
                            storage.rabbitmq_management_port,
                            storage.rabbitmq_user_username,
                            storage.rabbitmq_user_password
                        )
                        actual_value -= 1
            end_rabbitmq_connection(connection)
            return '200'
        else:
            return '500'
    except Exception as e:
        print(f'\nError in routes.retry_queues(): \n{str(e)}')


