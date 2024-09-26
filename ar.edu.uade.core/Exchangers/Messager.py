import pika


def prueba():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='mi_cola')

    # Definir la función que se ejecutará cuando se reciba un mensaje
    def callback(ch, method, properties, body):
        print(f" [x] Recibido: {body.decode()}")

    # Decirle a RabbitMQ que queremos recibir mensajes de 'mi_cola'
    channel.basic_consume(queue='mi_cola', on_message_callback=callback, auto_ack=True)

    print(' [*] Esperando mensajes. Para salir presiona CTRL+C')
    channel.start_consuming()
