import pika

def inicializar_core(connection):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='Core', exchange_type='direct')

    result = channel.queue_declare(queue='Core', exclusive=False,durable=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange='Core', queue=queue_name, routing_key=queue_name)

    # Definir la función que se ejecutará cuando se reciba un mensaje
    def callback(ch, method, properties, body):
        print(f" [x] Recibido: {body.decode()}")

    # Decirle a RabbitMQ que queremos recibir mensajes de 'Core'
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Esperando mensajes. Para salir presiona CTRL+C')
    channel.start_consuming()