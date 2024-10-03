import pika

from utilities.Logs.Application import log_application_error


def start_rabbitmq_connection(app, host):
    """
    Abre una conexión con el servidor de RabbitMQ y crea un canal.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param host: Requiere la dirección de host que verá RabbitMQ.
    :return: Devuelve la conexión y el canal o None en caso de una excepción.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.confirm_delivery()
        return connection, channel
    except Exception:
        log_application_error(app, 'Unknown error happened in brokers.brokers.RabbitMQ.start_rabbitmq_connection')
        return None, None


def end_rabbitmq_connection(connection):
    """
    Cierra una conexión de RabbitMQ.
    :param connection: Requiere una conexión.
    :return:
    """
    connection.close()
