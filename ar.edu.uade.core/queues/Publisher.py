import json

import pika

from utilities.Configuration import read_configuration_attribute, get_int_attribute
from utilities.Enumerations import PossiblePublishers, PossibleKeysForPublisherConfiguration
from utilities.Logger import log_messaging_error
from utilities.Utilities import check_void_parameter

MAX_RETRIES = 3
MIN_TTL = 3000


def initialize_publisher(channel, reader, module):
    """
    Inicializa las colas necesarias para un módulo.
    :param reader: Requiere al lector del archivo de configuración obtenido de configuration.initialize_configuration_reader
    :param module: Requiere el nombre del módulo para el que se crearán las colas y debe ser un módulo válido.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :return:
    """
    try:
        if check_valid_publisher(module):
            configuration = get_publisher_configuration(reader, module)
            max_retries = get_value_from_publisher_configuration(
                configuration,
                PossibleKeysForPublisherConfiguration.MAX_RETRIES.value)
            initialize_publisher_main_queue(channel, module)
            initialize_publisher_trapping_queue(channel, module)
            initialize_publisher_retry_queues(
                channel,
                module,
                max_retries,
                get_value_from_publisher_configuration(
                    configuration,
                    PossibleKeysForPublisherConfiguration.MIN_TTL.value))
            initialize_publisher_dead_letter_queue(channel, module, max_retries)
        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.initialize_publisher')
    except Exception as e:
        print(f'\nError in queues.Publisher.initialize_publisher(): \n{str(e)}')


def get_publisher_configuration(reader, module):
    """
    Obtiene la matriz de atributos de configuración del publisher.
    :param reader: Requiere un objeto reader que se obtiene con initialize_configuration_reader().
    :param module: Requiere el nombre del módulo para el que se obtendrá la matriz y debe ser un módulo válido.
    :return: Una matriz de atributos de configuración cuyo elemento cero es la key y el siguiente es el value o None
    si ocurre una excepción.
    """
    try:
        if check_valid_publisher(module):
            configuration = (
                (PossibleKeysForPublisherConfiguration.MAX_RETRIES.value,
                 get_int_attribute(
                     reader,
                     module,
                     PossibleKeysForPublisherConfiguration.MAX_RETRIES.value)),
                (PossibleKeysForPublisherConfiguration.MIN_TTL.value,
                 get_int_attribute(
                     reader,
                     module,
                     PossibleKeysForPublisherConfiguration.MIN_TTL.value)))
            return configuration
        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.get_publisher_configuration')
            return None
    except Exception as e:
        print(f'\nError in queues.Publisher.get_publisher_configuration(): \n{str(e)}')
        return None


def check_valid_publisher(module):
    """
    Verifica que el módulo sea un publisher válido encontrándose en el enumeration PossiblePublishers.
    :param module: Requiere el nombre del módulo que se validará.
    :return: Devuelve un boolean indicando si es un módulo válido o no.
    """
    return module in PossiblePublishers


def get_value_from_publisher_configuration(configuration, attribute):
    """
    Obtiene el valor de un atributo de la configuración de un publisher.
    :param configuration: Requiere la configuración obtenida de get_publisher_configuration().
    :param attribute: Requiere la key del valor que se desea obtener.
    :return: Devuelve el valor del atributo o None si ocurre una excepción.
    """
    try:
        for t in configuration:
            if t[0] == attribute:
                return t[1]
    except Exception as e:
        print(f'\nError in queues.Publisher.get_value_from_publisher_configuration(): \n{str(e)}')
        return None


def initialize_publisher_main_queue(channel, module):
    """
    Inicializa la cola principal del publisher, a donde los mensajes se van a dirigir tras haber sido recibidos en la
    cola principal del core.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se creará la cola y debe ser un módulo válido.
    :return:
    """
    try:
        if check_valid_publisher(module):
            #Declara el exchange
            channel.exchange_declare(exchange=module, exchange_type='direct', durable=True)

            #Declara la cola
            channel.queue_declare(queue=module, exclusive=False, durable=True, arguments={
                'x-dead-letter-exchange': f'{module}.trapping',
                'x-dead-letter-routing-key': f'{module}.trapping'
            })

            #Enlaza el exchange con la cola
            channel.queue_bind(
                exchange=module, queue=module, routing_key=module)

        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.initialize_publisher_main_queue')
    except Exception as e:
        print(f'\nError in queues.Publisher.initialize_publisher_main_queue(): \n{str(e)}')


def initialize_publisher_trapping_queue(channel, module):
    """
    Inicializa una cola que atrapará a los mensajes que estén por ser enviados a una cola de retry, para hacer posible
    analizar o refinar su comportamiento en el callback de consume_messages_from_publisher_trapping_queue().
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se crearán las colas y debe ser un módulo válido.
    :return:
    """
    try:
        if check_valid_publisher(module):
            #Declara el exchange
            channel.exchange_declare(exchange=f'{module}.trapping', exchange_type='direct', durable=True)

            #Declara la cola
            channel.queue_declare(queue=f'{module}.trapping', exclusive=False, durable=True)

            #Enlaza el exchange con la cola
            channel.queue_bind(
                exchange=f'{module}.trapping', queue=f'{module}.trapping', routing_key=f'{module}.trapping')

        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.initialize_publisher_trapping_queue')
    except Exception as e:
        print(f'\nError in queues.Publisher.initialize_publisher_trapping_queue(): \n{str(e)}')


def consume_messages_from_publisher_trapping_queue(app, channel, module):
    """
    Define un algoritmo que se ejecutará con cada mensaje consumido y bloqueará un hilo para permanecer a la escucha de
    nuevos mensajes
    :param channel:
    :param app: Requiere una instancia de la aplicación para hacer logs.
    :param module: Requiere el nombre del módulo para el que se definirá el algoritmo y debe ser un módulo válido.
    :return:
    """
    print(f'\nHilo {module} iniciado.')

    def callback(ch, method, properties, body):
        try:
            #Obtiene los headers del mensaje
            headers = properties.headers or {}

            #Decodifica el mensaje y lo convierte en un obj
            message = json.loads(body.decode('utf-8'))

            log_messaging_error(
                app,
                get_death_reason(headers),
                message['origin'],
                message['destination'],
                message['case']
            )
            edited_headers = add_death_count(headers)
            kill_message(channel, module, body, edited_headers)
        except Exception as e:
            print(f'\nError in queues.Publisher.callback(): \n{str(e)}')

    try:
        #Define como sera el consumo
        channel.basic_consume(
            queue=f'{module}.trapping',
            on_message_callback=callback,
            auto_ack=True
        )

        #Comienza a consumir
        channel.start_consuming()
    except Exception as f:
        print(f'\nError in queues.Publisher.consume_messages_from_publisher_trapping_queue(): \n{str(f)}')


def get_death_reason(headers):
    """
    Obtiene la razón del descarte de un mensaje.
    :param headers: Requiere los headers del mensaje.
    :return: Devuelve la razón por la que se descartó el mensaje o None si ocurrió una excepción.
    """
    try:
        return headers['x-death'][0]['reason']
    except Exception as e:
        print(f'\nError in utilities.logger.get_death_reason(): \n{str(e)}')
        return None


def add_death_count(headers):
    """
    Añade a un mensaje un contador de veces que fue rechazado o le adiciona si ya lo tiene.
    :param headers: Requiere los headers del mensaje.
    :return: Devuelve los headers modificados del mensaje.
    """
    try:
        headers['death-count']
    except KeyError:
        headers['death-count'] = 1
    else:
        headers['death-count'] += 1
    return headers


def kill_message(channel, exchange, message, headers):
    """
    Descarta un mensaje hacia un exhange de retry que se encargue de su distribución.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param exchange: Requiere el nombre del módulo con el que se está trabajando y debe ser un módulo válido.
    :param message: Requiere el cuerpo del mensaje que va a ser descartado.
    :param headers: Requiere los headers del mensaje modificados por add_death_count().
    :return:
    """
    try:
        #Publica al exchange de retry
        channel.basic_publish(exchange=f'{exchange}.retry', routing_key='', body=message, mandatory=True,
                              properties=pika.BasicProperties(
                                  headers=headers,
                                  delivery_mode=pika.DeliveryMode.Persistent))

    except Exception as e:
        print(f'\nError in queues.Publisher.kill_message(): \n{str(e)}')


def initialize_publisher_retry_queues(channel, module, max_retries=3, min_ttl=3000, offset=1):
    """
    Inicializa tantas colas de retry como sean indicadas por el administrador de la red en config.ini, con default en
    MAX_RETRIES = 3.
    Cada cola tendrá un TTL igual al doble del TTL de la cola de retry antecesora y el mínimo será el indicado por el
    administrador de la red en config.ini, con default en MIN_TTL = 30000 (milisegundos).
    :param offset:
    :param min_ttl: Requiere especificar cual será el ttl mínimo asignado a la primer cola de retry, con default en 30000
    :param max_retries: Requiere especificar cual será la cantidad máxima de colas de retry, con default en 3
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se inicializarán las colas de retry y debe ser un módulo válido.
    :return:
    """
    if check_valid_publisher(module):
        max_retries = check_void_parameter(max_retries, MAX_RETRIES)
        min_ttl = check_void_parameter(min_ttl, MIN_TTL)

        #Define el exchange de retry
        channel.exchange_declare(exchange=f'{module}.retry', exchange_type='headers', durable=True)

        for i in range(offset, max_retries + 1):
            #Define cada cola de retry
            channel.queue_declare(queue=f'{module}.retry{i}', exclusive=False, durable=True, arguments={
                'x-message-ttl': calculate_queue_ttl(i, min_ttl),
                'x-dead-letter-exchange': module,
                'x-dead-letter-routing-key': module
            })

            #Enlaza cada cola de retry a su exchange
            channel.queue_bind(
                exchange=f'{module}.retry', queue=f'{module}.retry{i}', arguments={
                    'x-match': 'all',
                    'death-count': i})
    else:
        print('\nGiven module is not a valid publisher for queues.Publisher.initialize_publisher_retry_queues')


def calculate_queue_ttl(i, min_ttl=30000):
    """
    Calcula el ttl que le corresponde a una cola de retry a partir del mínimo ttl definido por el administrador de la red
    y el órden de la cola de retry a la que se le asignará el valor.
    :param min_ttl: Requiere el mínimo ttl definido por el administrador de la red.
    :param i: Requiere el órden de la cola de retry.
    :return: Devuelve el ttl que le corresponde a la cola de retry con órden i.
    """
    min_ttl = check_void_parameter(min_ttl, MIN_TTL)
    return min_ttl * (2 ** i) if i != 1 else min_ttl


def initialize_publisher_dead_letter_queue(channel, module, max_retries=3):
    """
    Inicializa una cola a donde irán los mensajes que superaron la cantidad de reintentos definida por el administrador
    de la red y esperarán a una revisión manual del mismo.
    :param max_retries: Requiere especificar cual será la cantidad máxima de colas de retry, con default en 3
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se inicializarán las colas de retry y debe ser un módulo válido.
    :return:
    """
    try:
        if check_valid_publisher(module):
            max_retries = check_void_parameter(max_retries, MAX_RETRIES)

            #Declara la cola de dead letter
            channel.queue_declare(queue=f'{module}.dead-letter', exclusive=False, durable=True)

            #Enlaza la cola con su exchange
            channel.queue_bind(
                exchange=f'{module}.retry', queue=f'{module}.dead-letter', arguments={
                    'x-match': 'all',
                    'death-count': max_retries + 1})

        else:
            print('\nGiven module is not a valid publisher for queues.Publisher.initialize_publisher_dead_letter_queue')
    except Exception as e:
        print(f'\nError in queues.Publisher.initialize_publisher_dead_letter_queue(): \n{str(e)}')


def publish_message(channel, module, message):
    """
    Publica un mensaje en la cola principal del módulo que se le indica.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se inicializarán las colas de retry y debe ser un módulo válido.
    :param message: Requiere al mensaje que se enviará.
    :return:
    """
    if check_valid_publisher(module):
        try:
            message = json.dumps(message).encode('utf-8')
            #Publica en la cola del módulo especificado
            channel.basic_publish(exchange=module, routing_key=module, body=message, mandatory=True,
                                  properties=pika.BasicProperties(
                                      delivery_mode=pika.DeliveryMode.Persistent))

        except Exception as e:
            print(f'\nError in queues.Publisher.publish_message(): \n{str(e)}')
    else:
        print('\nGiven module is not a valid publisher for queues.Publisher.publish_message')
