import json

import requests
from flask import request


def delete_queue_binding_with_exchange(exchange, queue, key, host, port, user, password):
    try:
        url = f'http://{host}:{port}/api/bindings/%2F/e/{exchange}/q/{queue}/{key}'
        credentials = (user, password)
        response = requests.delete(url, auth=credentials)
        if response.status_code == 204:
            print(f"Binding entre el exchange '{exchange}' y la cola '{queue}' con routing key '{key}' eliminado.")
        else:
            print(f"Error al eliminar el binding: {response.text}")
    except Exception as e:
        print(f'\nError in utilities.management.delete_queue_binding_with_exchange(): \n{str(e)}')


def delete_queue(queue, host, port, user, password):
    try:
        url = f'http://{host}:{port}/api/queues/%2F/{queue}'
        credentials = (user, password)
        response = requests.delete(url, auth=credentials)
        if response.status_code == 204:
            print(f"Cola '{queue}' eliminada exitosamente.")
        else:
            print(f"Error al eliminar la cola: {response.text}")
    except Exception as e:
        print(f'\nError in utilities.management.delete_queue(): \n{str(e)}')


def transfer_messages(module, source, target, host, port, user, password):
    try:
        base_url = f'http://{host}:{port}/api'
        url_to_get = f'{base_url}/queues/%2F/{source}/get'
        credentials = (user, password)
        headers = {'content-type': 'application/json'}
        payload = {
            "count": 0,
            "ackmode": "ack_requeue_false",
            "encoding": "auto",
            "truncate": 50000
        }
        response = requests.post(url_to_get, auth=credentials, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            print(f"Error al obtener mensajes: {response.text}")
            return
        messages = response.json()
        url_to_post = f'{base_url}/exchanges/%2F/amq.default/publish'
        for message in messages:
            publish_payload = {
                "properties": message["properties"],
                "routing_key": target,
                "payload": message["payload"],
                "payload_encoding": "string"
            }
            response = requests.post(url_to_post, auth=credentials, headers=headers, data=json.dumps(publish_payload))
            if response.status_code != 200:
                print(f"Error al publicar mensaje: {response.text}")
        print(f"Transferidos {len(messages)} mensajes de {module}.dead-letter a {module}.")
    except Exception as e:
        print(f'\nError in utilities.management.transfer_messages(): \n{str(e)}')


def create_auxiliary_queue(channel, module, offset):
    channel.queue_declare(queue=f'{module}.auxiliary{offset}', exclusive=False, durable=True)
