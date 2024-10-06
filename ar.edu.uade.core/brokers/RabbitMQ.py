import pika

from utilities.Utilities import check_void_parameter

HOST = 'rabbitmq'
PORT = 5672


def start_rabbitmq_connection(username, password, host='rabbitmq', port=5672, virtual_host='/'):
    """
    Abre una conexión con el servidor de RabbitMQ y crea un canal.
    :return: Devuelve la conexión y el canal o None en caso de una excepción.
    """
    try:
        host = check_void_parameter(host, HOST)
        port = check_void_parameter(port, PORT)

        #Pide una conexión a RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                virtual_host=virtual_host,
                credentials=pika.PlainCredentials(
                    username,
                    password)))

        #Abre un canal en la conexión
        channel = connection.channel()
        channel.confirm_delivery()

        return connection, channel
    except Exception as e:
        print(f'\nError in brokers.RabbitMQ.start_rabbitmq_connection(): \n{str(e)}')
        return None, None


def end_rabbitmq_connection(connection):
    """
    Cierra una conexión de RabbitMQ.
    :param connection: Requiere una conexión.
    :return:
    """
    connection.close()
