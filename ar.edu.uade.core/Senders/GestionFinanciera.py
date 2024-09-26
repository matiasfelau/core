import pika

def init():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='GestionFinanciera', exchange_type='direct')

    result = channel.queue_declare(queue='GestionFinanciera', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange='GestionFinanciera', queue=queue_name, routing_key=queue_name)

    # Definir la función que se ejecutará cuando se reciba un mensaje
    def callback(ch, method, properties, body):
        print(f" [x] Recibido: {body.decode()}")

    def publish(message):
        # Decirle a RabbitMQ que queremos recibir mensajes de 'GestionFinanciera'
        channel.basic_publish(exchange='GestionFinanciera', routing_key=queue_name, body=message)
        print(f" [x] Sent {message}")
        return publish