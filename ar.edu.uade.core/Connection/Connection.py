import pika

from Senders.Usuario import callback


def start_rabbitmq_connection():
    """
    Inicia y devuelve una conexión y su respectivo canal.
    :return pika.BlockingConnection, BlockingConnection.Channel:
    """
    connection = None
    channel = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

    except Exception as e:
        print("\n"+"No se pudo realizar la conexión con el servidor de RabbitMQ.")
    return connection, channel


def end_connection(connection):
    """
    Cierra una conexión.
    :param connection:
    :param pika.BlockingConnection:
    """
    connection.close()