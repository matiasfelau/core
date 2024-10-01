import pika

def inicializar_core(channel):

    channel.exchange_declare(exchange='core', exchange_type='direct')

    result = channel.queue_declare(queue='core', exclusive=False,durable=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange='Core', queue=queue_name, routing_key=queue_name)


def consume_core(channel):

    # Definir la función que se ejecutará cuando se reciba un mensaje
    def callback(ch, method, properties, body):
        print(f" [x] Recibido: {body.decode()}")
        receiver = body["receiver"]
        channel.basic_publish(exchange=receiver, routing_key=receiver, body=body,properties=pika.BasicProperties(
            delivery_mode = pika.DeliveryMode.Persistent))

    # Decirle a RabbitMQ que queremos recibir mensajes de 'Core'
    channel.basic_consume(queue='core', on_message_callback=callback, auto_ack=True)

    print(' [*] Esperando mensajes. Para salir presiona CTRL+C')
    channel.start_consuming()