import pika
from pika.exceptions import UnroutableError, ConsumerCancelled





class Usuario:
    def __init__(self):

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()

        self.channel.confirm_delivery()

        self.channel.exchange_declare(exchange='usuario', exchange_type='direct',durable=True)

        result = self.channel.queue_declare(queue='usuario', exclusive=False,durable=True,arguments={
            'x-dead-letter-exchange': 'usuario',  # Enviar mensajes fallidos aquí
            'x-dead-letter-routing-key': 'usuario.retry'     # Routing key para los mensajes fallidos
        })

        result = self.channel.queue_declare(queue='usuario.retry', exclusive=False,durable=True)

        result = self.channel.queue_declare(queue='usuario.dead-letter', exclusive=False,durable=True,arguments={
            'x-message-ttl':1000 * 60 * 60
        })

        self.channel.queue_bind(
            exchange='usuario', queue='usuario', routing_key='usuario')

        self.channel.queue_bind(
            exchange='usuario', queue='usuario.retry', routing_key='usuario.retry')

        self.channel.queue_bind(
            exchange='usuario', queue='usuario.dead-letter', routing_key='usuario.dead-letter')


        # Definir la función que se ejecutará cuando se reciba un mensaje

    def publish(self, message):
    #Decirle a RabbitMQ que queremos recibir mensajes de 'Usuario'
        try:
            self.channel.basic_publish(exchange='usuario', routing_key='usuario', body=message,mandatory=True)
            print(f" [x] Sent {message}")
        except UnroutableError:
            print("El mensaje no pudo ser confirmado o enrutado desde Usuario")

    def consumeRetry(self):
        try:
            result = self.channel.basic_consume(queue='usuario.retry', on_message_callback=callback, auto_ack=False)

            self.channel.start_consuming()
        except ConsumerCancelled:
            pass

def callback(method, properties, body):
    print(f" [x] Recibido: {body.decode()}")
    #TODO CONTINUAR CON EL BODY DEL JSON...
