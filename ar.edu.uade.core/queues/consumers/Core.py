from pika.exceptions import ConsumerCancelled

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


def consume_messages_from_core_queue(app, channel):
    """
    Define un algoritmo que se ejecutará con cada mensaje consumido y bloqueará un hilo para permanecer a la escucha de
    nuevos mensajes.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :return:
    """

    def callback(ch, method, properties, body):
        forward_message(app, channel, body)

    try:
        channel.basic_consume(queue='core', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except ConsumerCancelled:
        log_application_error(app, 'Consuming has stopped in queues.consumers.Core.consume_messages_from_core_queue')
    except Exception:
        log_application_error(app, 'Unknown error happened in queues.consumers.Core.consume_messages_from_core_queue')


def forward_message(app, channel, message):
    """
    Reenvia un mensaje consumido hacia su respectivo módulo de destino.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param message: Requiere un mensaje que transmitir.
    :return:
    """
    destination = message['destination'].lower()
    if check_valid_publisher(destination):
        publish_message(channel, destination, message)
    else:
        log_application_error(app, 'Invalid destination in consumers.Core.forward_message')
