import pika
from pika.exceptions import UnroutableError, ConsumerCancelled
import json as js
from app import connection

def inicializar_usuario():
    channel = connection.channel()

    channel.confirm_delivery()

    channel.exchange_declare(exchange='usuario', exchange_type='direct',durable=True)

    channel.queue_declare(queue='usuario', exclusive=False,durable=True,arguments={
        'x-message-ttl':60000,
        'x-dead-letter-exchange': 'usuario',  # Enviar mensajes fallidos aquí
        'x-dead-letter-routing-key': 'usuario.retry'     # Routing key para los mensajes fallidos
    })

    channel.queue_declare(queue='usuario.retry', exclusive=False,durable=True)

    channel.queue_declare(queue='usuario.dead-letter', exclusive=False,durable=True,arguments={
        'x-message-ttl':1000 * 60 * 60,
        'x-dead-letter-exchange': 'usuario',  # Enviar mensajes fallidos aquí
        'x-dead-letter-routing-key': 'usuario.retry'     # Routing key para los mensajes fallidos
    })

    channel.queue_bind(
        exchange='usuario', queue='usuario', routing_key='usuario')

    channel.queue_bind(
        exchange='usuario', queue='usuario.retry', routing_key='usuario.retry')

    channel.queue_bind(
        exchange='usuario', queue='usuario.dead-letter', routing_key='usuario.dead-letter')

def callback(method, properties, body):
    #EL CANAL
    channel = connection.channel()
    # Decodificar el mensaje como JSON
    json_msg = js.loads(body.decode())
    print(" [x] Received %r" % json_msg)
    # ttl del json es el retry
    ttl = int(json_msg.get("ttl", 0))
    if 0 < ttl <= 3:
        # Reducir el TTL
        json_msg["ttl"] = ttl - 1

        # Reenviar el mensaje modificado a la cola 'usuario'
        nuevo_mensaje = js.dumps(json_msg)
        channel.basic_publish(exchange='usuario', routing_key='usuario', body=nuevo_mensaje, mandatory=True)
        print(f" [x] Reenviado a 'usuario' con TTL actualizado: {nuevo_mensaje}")
    else:
        nuevo_mensaje = js.dumps(json_msg)
        channel.basic_publish(exchange='usuario', routing_key='usuario.deadletter', body=nuevo_mensaje, mandatory=True)
    # Acknowledge el mensaje para eliminarlo de la cola de retry
    channel.basic_ack(delivery_tag=method.delivery_tag)


    # Definir la función que se ejecutará cuando se reciba un mensaje

def publish_usuario(message):
    channel = connection.channel()
#Decirle a RabbitMQ que queremos recibir mensajes de 'Usuario'
    try:
        channel.basic_publish(exchange='usuario', routing_key='usuario', body=message,mandatory=True)
        print(f" [x] Sent {message}")
    except UnroutableError:
        print("El mensaje no pudo ser confirmado o enrutado desde Usuario")

def consume_usuario():
    channel = connection.channel()
    try:
        channel.basic_consume(queue='usuario.retry', on_message_callback=callback, auto_ack=False)
        channel.start_consuming()
    except ConsumerCancelled:
        pass

