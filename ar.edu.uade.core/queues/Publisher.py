import pika
from pika.exceptions import UnroutableError, ConsumerCancelled

from utilities.Configuration import read_configuration_attribute
from utilities.Enumerations import PossiblePublishers, PossibleKeysForPublisherConfiguration
from utilities.Logs.Application import log_application_error
from utilities.Logs.Messaging import log_messaging_error, get_death_timestamp, get_death_reason

MAX_RETRIES = 3
MIN_TTL = 30000


def initialize_publisher(app, channel, module, configuration):
    """
    Inicializa las colas necesarias para un módulo.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param configuration: Requiere la matriz de atributos de configuración del publisher que se obtiene con
    get_publisher_configuration().
    :param module: Requiere el nombre del módulo para el que se crearán las colas y debe ser un módulo válido.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :return:
    """
    if check_valid_publisher(module):
        max_retries = get_value_from_publisher_configuration(
            app,
            configuration,
            PossibleKeysForPublisherConfiguration.MAX_RETRIES)
        initialize_publisher_main_queue(app, channel, module)
        initialize_publisher_trapping_queue(app, channel, module)
        initialize_publisher_retry_queues(
            app,
            channel,
            module,
            max_retries,
            get_value_from_publisher_configuration(app, configuration, PossibleKeysForPublisherConfiguration.MIN_TTL))
        initialize_publisher_dead_letter_queue(app, channel, module, max_retries)
    else:
        log_application_error(app, 'Given module is not a valid publisher for queues.Publisher.initialize_publisher')


def get_publisher_configuration(app, reader, module):
    """
    Obtiene la matriz de atributos de configuración del publisher.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param reader: Requiere un objeto reader que se obtiene con initialize_configuration_reader().
    :param module: Requiere el nombre del módulo para el que se obtendrá la matriz y debe ser un módulo válido.
    :return: Una matriz de atributos de configuración cuyo elemento cero es la key y el siguiente es el value o None
    si ocurre una excepción.
    """
    if check_valid_publisher(module):
        configuration = (
            (PossibleKeysForPublisherConfiguration.MAX_RETRIES,
             int(read_configuration_attribute(reader, module, PossibleKeysForPublisherConfiguration.MAX_RETRIES))),
            (PossibleKeysForPublisherConfiguration.MIN_TTL,
             int(read_configuration_attribute(reader, module, PossibleKeysForPublisherConfiguration.MIN_TTL))))
        return configuration
    else:
        log_application_error(
            app,
            'Given module is not a valid publisher for queues.Publisher.get_publisher_configuration')
        return None


def check_valid_publisher(module):
    """
    Verifica que el módulo sea un publisher válido encontrándose en el enumeration PossiblePublishers.
    :param module: Requiere el nombre del módulo que se validará.
    :return: Devuelve un boolean indicando si es un módulo válido o no.
    """
    return module in PossiblePublishers


def get_value_from_publisher_configuration(app, configuration, attribute):
    """
    Obtiene el valor de un atributo de la configuración de un publisher.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param configuration: Requiere la configuración obtenida de get_publisher_configuration().
    :param attribute: Requiere la key del valor que se desea obtener.
    :return: Devuelve el valor del atributo o None si ocurre una excepción.
    """
    try:
        for t in configuration:
            if t[0] == attribute:
                return t[1]
    except IndexError:
        log_application_error(
            app,
            'Invalid evaluated position in queues.Publisher.get_value_from_publisher_configuration')
        return None
    except Exception:
        log_application_error(app, 'Unknown error happened in queues.Publisher.get_value_from_publisher_configuration')
        return None


def initialize_publisher_main_queue(app, channel, module):
    """
    Inicializa la cola principal del publisher, a donde los mensajes se van a dirigir tras haber sido recibidos en la
    cola principal del core.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se creará la cola y debe ser un módulo válido.
    :return:
    """
    if check_valid_publisher(module):
        channel.exchange_declare(exchange=module, exchange_type='direct', durable=True)
        channel.queue_declare(queue=module, exclusive=False, durable=True, arguments={
            'x-dead-letter-exchange': f'{module}.trapping',
            'x-dead-letter-routing-key': f'{module}.trapping'
        })
        channel.queue_bind(
            exchange=module, queue=module, routing_key=module)
    else:
        log_application_error(
            app,
            'Given module is not a valid publisher for queues.Publisher.initialize_publisher_main_queue')


def initialize_publisher_trapping_queue(app, channel, module):
    """
    Inicializa una cola que atrapará a los mensajes que estén por ser enviados a una cola de retry, para hacer posible
    analizar o refinar su comportamiento en el callback de consume_messages_from_publisher_trapping_queue().
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se crearán las colas y debe ser un módulo válido.
    :return:
    """
    if check_valid_publisher(module):
        channel.exchange_declare(exchange=f'{module}.trapping', exchange_type='direct', durable=True)
        channel.queue_declare(queue=f'{module}.trapping', exclusive=False, durable=True)
        channel.queue_bind(
            exchange=f'{module}.trapping', queue=f'{module}.trapping', routing_key=f'{module}.trapping')
    else:
        log_application_error(
            app,
            'Given module is not a valid publisher for queues.Publisher.initialize_publisher_trapping_queue')


def consume_messages_from_publisher_trapping_queue(app, channel, module):
    """
    Define un algoritmo que se ejecutará con cada mensaje consumido y bloqueará un hilo para permanecer a la escucha de
    nuevos mensajes.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se definirá el algoritmo y debe ser un módulo válido.
    :return:
    """

    def callback(ch, method, properties, body):
        headers = properties.headers or {}
        log_messaging_error(
            app,
            get_death_timestamp(headers),
            get_death_reason(headers),
            body['origin'],
            body['destination'],
            body['case']
        )
        edited_headers = add_death_count(headers)
        kill_message(app, channel, module, body, edited_headers)

    try:
        channel.basic_consume(queue=f'{module}.trapping', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except ConsumerCancelled:
        log_application_error(
            app,
            'Consuming has stopped in queues.Publisher.consume_messages_from_publisher_trapping_queue')
    except Exception:
        log_application_error(
            app,
            'Unknown error happened in queues.Publisher.consume_messages_from_publisher_trapping_queue')


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


def kill_message(app, channel, exchange, message, headers):
    """
    Descarta un mensaje hacia un exhange de retry que se encargue de su distribución.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param exchange: Requiere el nombre del módulo con el que se está trabajando y debe ser un módulo válido.
    :param message: Requiere el cuerpo del mensaje que va a ser descartado.
    :param headers: Requiere los headers del mensaje modificados por add_death_count().
    :return:
    """
    try:
        channel.basic_publish(exchange=f'{exchange}.retry', routing_key='', body=message, mandatory=True,
                              properties=pika.BasicProperties(
                                  headers=headers,
                                  delivery_mode=pika.DeliveryMode.Persistent))
    except UnroutableError:
        log_application_error(app, f'A message couldn\'t be dead lettered to {exchange}')
    except Exception:
        log_application_error(app, 'Unknown error happened in queues.Publisher.kill_message')


def initialize_publisher_retry_queues(app, channel, module, max_retries=3, min_ttl=30000):
    """
    Inicializa tantas colas de retry como sean indicadas por el administrador de la red en config.ini, con default en
    MAX_RETRIES = 3.
    Cada cola tendrá un TTL igual al doble del TTL de la cola de retry antecesora y el mínimo será el indicado por el
    administrador de la red en config.ini, con default en MIN_TTL = 30000 (milisegundos).
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param min_ttl: Requiere especificar cual será el ttl mínimo asignado a la primer cola de retry, con default en 30000
    :param max_retries: Requiere especificar cual será la cantidad máxima de colas de retry, con default en 3
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se inicializarán las colas de retry y debe ser un módulo válido.
    :return:
    """
    if check_valid_publisher(module):
        check_void_parameter(max_retries, MAX_RETRIES)
        check_void_parameter(min_ttl, MIN_TTL)
        channel.exchange_declare(exchange=f'{module}.retry', exchange_type='headers', durable=True)
        for i in range(1, max_retries + 1):
            channel.queue_declare(queue=f'{module}.retry{i}', exclusive=False, durable=True, arguments={
                'x-message-ttl': calculate_queue_ttl(min_ttl, i),
                'x-dead-letter-exchange': module,
                'x-dead-letter-routing-key': module
            })
            channel.queue_bind(
                exchange=f'{module}.retry', queue=f'{module}.retry{i}', arguments={
                    'x-match': 'all',
                    'death-count': i})
    else:
        log_application_error(
            app,
            'Given module is not a valid publisher for queues.Publisher.initialize_publisher_retry_queues')


def check_void_parameter(variable, default_value):
    """
    Verifica si un parámetro tiene un valor asignado y, en caso contrario, le otorga el valor por defecto.
    :param variable: Requiere el parámetro que será evalaudo.
    :param default_value: Requiere el valor por defecto que se le asignará al parámetro si estuviera vacío.
    :return: Devuelve el parámetro con el valor que ingresó o con el valor por defecto asignado a él.
    """
    return default_value if variable is None else variable


def calculate_queue_ttl(min_ttl, i):
    """
    Calcula el ttl que le corresponde a una cola de retry a partir del mínimo ttl definido por el administrador de la red
    y el órden de la cola de retry a la que se le asignará el valor.
    :param min_ttl: Requiere el mínimo ttl definido por el administrador de la red.
    :param i: Requiere el órden de la cola de retry.
    :return: Devuelve el ttl que le corresponde a la cola de retry con órden i.
    """
    return min_ttl * (2 ** i) if i != 1 else min_ttl


def initialize_publisher_dead_letter_queue(app, channel, module, max_retries=3):
    """
    Inicializa una cola a donde irán los mensajes que superaron la cantidad de reintentos definida por el administrador
    de la red y esperarán a una revisión manual del mismo.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param max_retries: Requiere especificar cual será la cantidad máxima de colas de retry, con default en 3
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se inicializarán las colas de retry y debe ser un módulo válido.
    :return:
    """
    if check_valid_publisher(module):
        check_void_parameter(max_retries, MAX_RETRIES)
        channel.queue_declare(queue=f'{module}.dead-letter', exclusive=False, durable=True)
        channel.queue_bind(
            exchange=f'{module}.retry', queue=f'{module}.dead-letter', arguments={
                'x-match': 'all',
                'death-count': max_retries + 1})
    else:
        log_application_error(
            app,
            'Given module is not a valid publisher for queues.Publisher.initialize_publisher_dead_letter_queue')


def publish_message(app, channel, module, message):
    """
    Publica un mensaje en la cola principal del módulo que se le indica.
    :param app: Requiere la instancia de la aplicación para realizar logs por consola.
    :param channel: Requiere el canal de la conexión con RabbitMQ.
    :param module: Requiere el nombre del módulo para el que se inicializarán las colas de retry y debe ser un módulo válido.
    :param message: Requiere al mensaje que se enviará.
    :return:
    """
    if check_valid_publisher(module):
        try:
            channel.basic_publish(exchange=module, routing_key=module, body=message, mandatory=True,
                                  properties=pika.BasicProperties(
                                      delivery_mode=pika.DeliveryMode.Persistent))
        except UnroutableError:
            log_application_error(app, f'A message couldn\'t be forwarded to {module}')
        except Exception:
            log_application_error(app, 'Unknown error happened in queues.Publisher.publish_message')
    else:
        log_application_error(app, 'Given module is not a valid publisher for queues.Publisher.publish_message')
