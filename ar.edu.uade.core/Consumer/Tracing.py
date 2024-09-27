from datetime import datetime
from os import times

from pika.exceptions import UnroutableError, ConsumerCancelled
import json as js

from Model.Log import save_log


def inicializar_tracing(channel):
    channel.exchange_declare(exchange='amq.rabbitmq.trace', exchange_type='direct',durable=True, internal=True)
    channel.queue_declare(queue='core.trace', exclusive=True, durable=True)
    channel.queue_bind(
        exchange='amq.rabbitmq.trace', queue='core.trace', routing_key='#')


def consume_tracing(channel):
    try:
        channel.basic_consume(queue='core.trace', on_message_callback=callback, auto_ack=False)
        channel.start_consuming()
    except ConsumerCancelled:
        pass

def callback(channel,method, properties, body):
    print(f"Recibido mensaje de tracing: {body}")
    json_msg = js.loads(body.decode())
    status = json_msg.get('status')
    timestamp = json_msg.get('timestamp')
    ttl = json_msg.get('ttl')
    payload = json_msg.get('payload')
    origin = json_msg.get('origin')
    destination = json_msg.get('destination')
    save_log(status, timestamp, ttl, payload, origin, destination)