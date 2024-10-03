import threading

from flask import Flask, render_template
from flask_socketio import SocketIO

from brokers.RabbitMQ import start_rabbitmq_connection
from queues.Publisher import initialize_publisher, get_publisher_configuration, \
    consume_messages_from_publisher_trapping_queue
from queues.consumers.Core import consume_messages_from_core_queue, initialize_core_queue
from utilities.Configuration import initialize_configuration_reader
from utilities.Enumerations import PossiblePublishers, PossibleKeysForEnvironmentVariables
from utilities.Environment import *
from utilities.Logs.Application import initialize_logging_for_application_errors
from utilities.Logs.Messaging import initialize_logging_for_messaging_errors, check_path

app = Flask(__name__)

check_path('/core_disk')
check_path('/core_disk/data')
check_path('/core_disk/data/logs')
check_path('/core_disk/resources')

#Logging
application_logs_handler = initialize_logging_for_application_errors()
messaging_logs_handler = initialize_logging_for_messaging_errors()

app.logger.addHandler(application_logs_handler)
app.logger.addHandler(messaging_logs_handler)

#Environment Variables
environment_variables = get_environment_variables(app)

check_void_environment_variables(app, environment_variables)

host = get_value_from_environment_variable(app, environment_variables, PossibleKeysForEnvironmentVariables.HOST.value)

#Configuration
reader = initialize_configuration_reader()

#Websocket
app.config['SECRET_KEY'] = get_value_from_environment_variable(
    app,
    environment_variables,
    PossibleKeysForEnvironmentVariables.SECRET_KEY.value)

socketio = SocketIO(app)

#Connections
connection, channel = start_rabbitmq_connection(
    app,
    host)

#Queues
#Consumers
initialize_core_queue(app, channel)

#Publishers
e_commerce_configuration = get_publisher_configuration(app, reader, PossiblePublishers.E_COMMERCE.value)
gestion_financiera_configuration = get_publisher_configuration(app, reader, PossiblePublishers.GESTION_FINANCIERA.value)
gestion_interna_configuration = get_publisher_configuration(app, reader, PossiblePublishers.GESTION_INTERNA.value)
usuario_configuration = get_publisher_configuration(app, reader, PossiblePublishers.USUARIO.value)

initialize_publisher(app, channel, PossiblePublishers.E_COMMERCE.value, e_commerce_configuration)
initialize_publisher(app, channel, PossiblePublishers.GESTION_FINANCIERA.value, gestion_financiera_configuration)
initialize_publisher(app, channel, PossiblePublishers.GESTION_INTERNA.value, gestion_interna_configuration)
initialize_publisher(app, channel, PossiblePublishers.USUARIO.value, usuario_configuration)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    socketio.emit('response', 'Server received your message: ' + data)


if __name__ == 'app':
    port = get_value_from_environment_variable(
        app,
        environment_variables,
        PossibleKeysForEnvironmentVariables.PORT.value
    )

    # Hilo para ejecutar la aplicación SocketIO
    t1 = threading.Thread(
        target=socketio.run,
        args=(app,),
        kwargs={'host': host, 'port': port, 'debug': True},
        name='runningApp',
        daemon=False
    )

    # Hilo para consumir mensajes de la cola core
    t2 = threading.Thread(
        target=consume_messages_from_core_queue,
        args=(app, ),
        name='consumingCore',
        daemon=True
    )

    # Hilo para consumir mensajes de eCommerce
    t3 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue,
        args=(app, PossiblePublishers.E_COMMERCE.value),
        name='consumingECommerce',
        daemon=True
    )

    # Hilo para consumir mensajes de Gestión Financiera
    t4 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue,
        args=(app, PossiblePublishers.GESTION_FINANCIERA.value),
        name='consumingGestionFinanciera',
        daemon=True
    )

    # Hilo para consumir mensajes de Gestión Interna
    t5 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue,
        args=(app, PossiblePublishers.GESTION_INTERNA.value),
        name='consumingGestionInterna',
        daemon=True
    )

    # Hilo para consumir mensajes de Usuario
    t6 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue,
        args=(app, PossiblePublishers.USUARIO.value),
        name='consumingUsuario',
        daemon=True
    )

    # Iniciar todos los hilos
    for thread in [t1, t2, t3, t4, t5, t6]:
        thread.start()
