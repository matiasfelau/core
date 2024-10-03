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
from utilities.Logs.Messaging import initialize_logging_for_messaging_errors

app = Flask(__name__)

#Logging
application_logs_handler = initialize_logging_for_application_errors()
messaging_logs_handler = initialize_logging_for_messaging_errors()

app.logger.addHandler(application_logs_handler)
app.logger.addHandler(messaging_logs_handler)

#Environment Variables
environment_variables = get_environment_variables(app)

check_void_environment_variables(app, environment_variables)

host = get_value_from_environment_variable(app, environment_variables, PossibleKeysForEnvironmentVariables.HOST)

#Configuration
reader = initialize_configuration_reader()

#Websocket
app.config['SECRET_KEY'] = get_value_from_environment_variable(
    app,
    environment_variables,
    PossibleKeysForEnvironmentVariables.SECRET_KEY)

socketio = SocketIO(app)

#Connections
connection, channel = start_rabbitmq_connection(
    app,
    get_value_from_environment_variable(
        app,
        environment_variables,
        host))

#Queues
#Consumers
initialize_core_queue(app, channel)

#Publishers
e_commerce_configuration = get_publisher_configuration(app, reader, PossiblePublishers.E_COMMERCE)
gestion_financiera_configuration = get_publisher_configuration(app, reader, PossiblePublishers.GESTION_FINANCIERA)
gestion_interna_configuration = get_publisher_configuration(app, reader, PossiblePublishers.GESTION_INTERNA)
usuario_configuration = get_publisher_configuration(app, reader, PossiblePublishers.USUARIO)

initialize_publisher(app, channel, PossiblePublishers.E_COMMERCE, e_commerce_configuration)
initialize_publisher(app, channel, PossiblePublishers.GESTION_FINANCIERA, gestion_financiera_configuration)
initialize_publisher(app, channel, PossiblePublishers.GESTION_INTERNA, gestion_interna_configuration)
initialize_publisher(app, channel, PossiblePublishers.USUARIO, usuario_configuration)


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


if __name__ == '__main__':
    t1 = threading.Thread(target=socketio.run(
        app,
        host=host,
        port=get_value_from_environment_variable(
            app,
            environment_variables,
            PossibleKeysForEnvironmentVariables.PORT),
        debug=True
    ), name='runningApp')
    t2 = threading.Thread(target=consume_messages_from_core_queue(app, channel), name='consumingCore')
    t3 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue(
            app,
            channel,
            PossiblePublishers.E_COMMERCE),
        name='consumingECommerce')
    t4 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue(
            app,
            channel,
            PossiblePublishers.GESTION_FINANCIERA),
        name='consumingGestionFinanciera')
    t5 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue(
            app,
            channel,
            PossiblePublishers.GESTION_INTERNA),
        name='consumingGestionInterna')
    t6 = threading.Thread(
        target=consume_messages_from_publisher_trapping_queue(
            app,
            channel,
            PossiblePublishers.USUARIO),
        name='consumingUsuario')

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
