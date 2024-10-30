from flask import Blueprint, request

from utilities import storage
from utilities.Management import transfer_messages

dead_letter_queue = Blueprint('dead_letter_queue', __name__)


@dead_letter_queue.route('/dead-letter/release', methods=['GET'])
def release_dead_messages():
    module = request.args.get('module')
    source = f'{module}.dead-letter'
    target = module
    transfer_messages(
        module,
        source,
        target,
        storage.rabbitmq_host,
        storage.rabbitmq_management_port,
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password
    )
    return '200' #TODO verificar cuantos mensajes quedan en la cola, puede ser una diff
