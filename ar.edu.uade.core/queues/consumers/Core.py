import json

from queues.Publisher import check_valid_publisher, publish_message


def initialize_core_queue(channel):
    """
    Inicializa la cola en la que el Core recibirá y consumirá mensajes de los demás módulos.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :return:
    """
    try:
        #Declara el exchange
        channel.exchange_declare(exchange='core', exchange_type='direct')

        #Declara la cola
        channel.queue_declare(queue='core', exclusive=False, durable=True)

        #Enlaza la cola al exchange
        channel.queue_bind(exchange='core', queue='core', routing_key='core')
    except Exception as e:
        print(f'\nError in queues.consumers.Core.initialize_core_queue(): \n{str(e)}')


def consume_messages_from_core_queue(channel):
    """
    Define un algoritmo que se ejecutará con cada mensaje consumido y bloqueará un hilo para permanecer a la escucha de
    nuevos mensajes.
    :param channel:
    :return:
    """
    print('Hilo del Core iniciado.')

    def callback(ch, method, properties, body):
        forward_message(channel, body)

    try:
        #Define como se hará el consumo
        channel.basic_consume(
            queue='core',
            on_message_callback=callback,
            auto_ack=True
            )

        #Comienza a consumir
        channel.start_consuming()

    except Exception as e:
        print(f'\nError in queues.consumers.Core.consume_messages_from_core_queue(): \n{str(e)}')


def forward_message(channel, body):
    """
    Reenvia un mensaje consumido hacia su respectivo módulo de destino.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param body: Requiere un mensaje que transmitir.
    :return:
    """
    try:
        #Decodifica el mensaje y convierte a obj
        message = json.loads(body.decode('utf-8'))

        #Obtiene el destino del mensaje
        destination = message.get('destination').lower()

        if check_valid_publisher(destination):
            publish_message(channel, destination, body)
        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.get_publisher_configuration')
    except Exception as e:
        print(f'\nError in queues.consumers.Core.forward_message(): \n{str(e)}')
