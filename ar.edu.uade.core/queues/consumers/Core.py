import json
import uuid

from pika.exceptions import ConsumerCancelled

from brokers.RabbitMQ import start_rabbitmq_connection
from queues.Publisher import check_valid_publisher, publish_message
from utilities.Logs.Application import log_application_error


def initialize_core_queue(app, channel):
    """
    Inicializa la cola en la que el Core recibirá y consumirá mensajes de los demás módulos.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :return:
    """
    try:
        channel.exchange_declare(exchange='core', exchange_type='direct')
        channel.queue_declare(queue='core', exclusive=False, durable=True)
        channel.queue_bind(exchange='core', queue='core', routing_key='core')
    except Exception:
        log_application_error(app, 'Unknown error happened in queues.consumers.Core.initialize_core_queue')


def consume_messages_from_core_queue(app):
    """
    Define un algoritmo que se ejecutará con cada mensaje consumido y bloqueará un hilo para permanecer a la escucha de
    nuevos mensajes.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :return:
    """

    def callback(ch, method, properties, body):
        forward_message(app, channel, body)

    try:
        connection, channel = start_rabbitmq_connection(app, 'localhost')
        #unique_consumer_tag = f'consumer-{uuid.uuid4()}'
        channel.basic_consume(
            queue='core',
            on_message_callback=callback,
            auto_ack=True
            #consumer_tag=unique_consumer_tag
            )
        channel.start_consuming()
    except ConsumerCancelled:
        log_application_error(app, 'Consuming has stopped in queues.consumers.Core.consume_messages_from_core_queue')
    except Exception as e:
        print('el error es:', e)
        log_application_error(app, 'Unknown error happened in queues.consumers.Core.consume_messages_from_core_queue')


def forward_message(app, channel, body):
    """
    Reenvia un mensaje consumido hacia su respectivo módulo de destino.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param body: Requiere un mensaje que transmitir.
    :return:
    """
    message = json.loads(body.decode('utf-8'))
    destination = message['destination'].lower()
    if check_valid_publisher(destination):
        publish_message(app, channel, destination, body)
    else:
        log_application_error(app, 'Invalid destination in consumers.Core.forward_message')
