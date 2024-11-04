import json

from brokers.RabbitMQ import start_rabbitmq_connection, end_rabbitmq_connection
from queues.Publisher import check_valid_publisher, publish_message
from utilities import storage
from utilities.authenticator import Authenticator


def initialize_core_queue(channel):
    """
    Inicializa la cola en la que el Core recibirá y consumirá mensajes de los demás módulos.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :return:
    """
    try:
        #Declara el exchange
        channel.exchange_declare(exchange='core', exchange_type='direct', durable=True)

        #Declara la cola
        channel.queue_declare(queue='core', exclusive=False, durable=True)

        #Enlaza la cola al exchange
        channel.queue_bind(exchange='core', queue='core', routing_key='core')
    except Exception as e:
        print(f'\nError in queues.consumers.Core.initialize_core_queue(): \n{str(e)}')


def consume_messages_from_core_queue(channel):
    """
    Define un algoritmo que se ejecutará con cada mensaje consumido y bloqueará un hilo para permanecer a la escucha de
    nuevos mensajes.
    :param channel:
    :return:
    """
    print('Hilo del Core iniciado.')

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode('utf-8'))
            if check_valid_message(payload):
                if payload.get('case') not in ('login', 'register'):
                    authenticator_connection, authenticator_channel = start_rabbitmq_connection(
                        storage.rabbitmq_user_username,
                        storage.rabbitmq_user_password,
                        storage.rabbitmq_host,
                        storage.rabbitmq_port
                    )
                    authenticator = Authenticator(
                        authenticator_connection,
                        authenticator_channel,
                    )
                    token = payload.get('token')
                    user = payload.get('user')
                    origin = payload.get('origin')
                    authentication_body = {
                        'token': token,
                        'user': user,
                        'origin': origin
                    }
                    encode = json.dumps(authentication_body).encode('utf-8')
                    response = authenticator.authenticate(encode)
                    end_rabbitmq_connection(authenticator_connection)
                    if response == 'True':
                        publish_message(channel, payload.get('destination').lower(), payload)
                    elif not response:
                        if storage.environment == 'test' and payload.get('status') == '600':
                            publish_message(channel, payload.get('destination').lower(), payload)
                        else:
                            print('Un mensaje no se pudo enviar por un fallo en la autenticación.')
                else:
                    publish_message(channel, payload.get('destination').lower(), payload)
            else:
                print('Un mensaje no se pudo enviar por un fallo en los headers.')
        except Exception as f:
            print(f'\nError in queues.consumers.Core.consume_messages_from_core_queue.callback(): \n{str(f)}')

    try:
        #Define como se hará el consumo
        channel.basic_consume(
            queue='core',
            on_message_callback=callback,
            auto_ack=True
        )

        #Comienza a consumir
        channel.start_consuming()

    except Exception as e:
        print(f'\nError in queues.consumers.Core.consume_messages_from_core_queue(): \n{str(e)}')


@DeprecationWarning
def forward_message(channel, payload):
    """
    Reenvia un mensaje consumido hacia su respectivo módulo de destino.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param payload: Requiere un mensaje que transmitir.
    :return:
    """
    try:
        #Obtiene el destino del mensaje
        destination = payload.get('destination').lower()

        if check_valid_publisher(destination):
            publish_message(channel, destination, payload)
        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.get_publisher_configuration')
    except Exception as e:
        print(f'\nError in queues.consumers.Core.forward_message(): \n{str(e)}')


def check_valid_message(message):
    """

    :param message:
    :return:
    """
    try:
        checkouts = [
            check_valid_publisher(message.get('origin').lower()),
            check_valid_publisher(message.get('destination').lower()),
            message.get('case') != '',
            message.get('payload') != '',
            message.get('status') != '',
            message.get('type') != '',
            message.get('user') != ''
        ]
        return False not in checkouts
    except Exception as e:
        raise Exception(f'\nError in queues.consumers.check_valid_message(): \n{str(e)}')
