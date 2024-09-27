import pika

def start_connection():
    connection = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    except Exception as e:
        print("\n"+"No se pudo realizar la conexión con el servidor de RabbitMQ.")
    return connection


def end_connection(connection):
    connection.close()