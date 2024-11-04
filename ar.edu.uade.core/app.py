import json
import threading


import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from flask_socketio import SocketIO

from brokers.RabbitMQ import start_rabbitmq_connection, end_rabbitmq_connection
from queues.Publisher import initialize_publisher, consume_messages_from_publisher_trapping_queue
from queues.consumers.Core import consume_messages_from_core_queue, initialize_core_queue
from routes.dead_letter_queue import dead_letter_queue
from routes.logs import logs
from routes.retry_queues import retry_queues
from utilities.Configuration import initialize_configuration_reader, check_create_configuration_file, \
    read_configuration_attribute, write_in_configuration_file
from utilities.Enumerations import PossiblePublishers
from utilities.Environment import *
from utilities.Logger import initialize_logging_for_messaging_errors
from utilities.Management import delete_queue_binding_with_exchange, delete_queue, create_auxiliary_queue
from utilities.authenticator import initialize_authenticator_queue

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.register_blueprint(retry_queues)

app.register_blueprint(dead_letter_queue)

app.register_blueprint(logs)

#Environment Variables
environment_variables = get_environment_variables()

check_void_environment_variables(
    environment_variables)

#Websocket
app.config['SECRET_KEY'] = get_value_from_environment_variable(
    environment_variables,
    PossibleKeysForEnvironmentVariables.WEBSOCKET_SECRET_KEY.value)

socketio = SocketIO(
    app)

#Connections
connections = []
channels = []

for i in range(7):
    connection, channel = start_rabbitmq_connection(
        get_value_from_environment_variable(
            environment_variables,
            PossibleKeysForEnvironmentVariables.RABBITMQ_USERNAME.value),
        get_value_from_environment_variable(
            environment_variables,
            PossibleKeysForEnvironmentVariables.RABBITMQ_PASSWORD.value),
        get_value_from_environment_variable(
            environment_variables,
            PossibleKeysForEnvironmentVariables.RABBITMQ_HOST.value),
        get_value_from_environment_variable(
            environment_variables,
            PossibleKeysForEnvironmentVariables.RABBITMQ_PORT.value)
    )
    connections.append(connection)
    channels.append(channel)

#Configuration
reader = initialize_configuration_reader()

#Logging
messaging_logs_handler = initialize_logging_for_messaging_errors(
    get_value_from_environment_variable(
        environment_variables,
        PossibleKeysForEnvironmentVariables.LOGS_PATH.value
    )
)

if messaging_logs_handler is not None:
    app.logger.addHandler(
        messaging_logs_handler)
else:
    print('\nCouldn\'t define a logging handler.')

#Queues
#Consumers
initialize_core_queue(channels[0])

#RPC
#initialize_authenticator_queue(channels[0])

#Publishers
initialize_publisher(channels[0], reader, PossiblePublishers.E_COMMERCE.value)
initialize_publisher(channels[0], reader, PossiblePublishers.AUTENTICACION.value)
initialize_publisher(channels[0], reader, PossiblePublishers.GESTION_FINANCIERA.value)
initialize_publisher(channels[0], reader, PossiblePublishers.GESTION_INTERNA.value)
initialize_publisher(channels[0], reader, PossiblePublishers.USUARIO.value)

end_rabbitmq_connection(connections[0])

del connections

#Hilos
t1 = threading.Thread(
    target=socketio.run,
    args=(app,),
    kwargs={
        'host': get_value_from_environment_variable(
            environment_variables,
            PossibleKeysForEnvironmentVariables.FLASK_HOST.value),
        'port': get_value_from_environment_variable(
            environment_variables,
            PossibleKeysForEnvironmentVariables.FLASK_PORT.value),
        'debug': True,
        'allow_unsafe_werkzeug': True
    },
    name='runningApp'
)
t2 = threading.Thread(
    target=consume_messages_from_core_queue,
    args=(channels[1],),
    name='consumingCore'
)
t3 = threading.Thread(
    target=consume_messages_from_publisher_trapping_queue,
    args=(app, channels[2], PossiblePublishers.E_COMMERCE.value),
    name='consumingECommerce'
)
t4 = threading.Thread(
    target=consume_messages_from_publisher_trapping_queue,
    args=(app, channels[3], PossiblePublishers.GESTION_FINANCIERA.value),
    name='consumingGestionFinanciera'
)
t5 = threading.Thread(
    target=consume_messages_from_publisher_trapping_queue,
    args=(app, channels[4], PossiblePublishers.GESTION_INTERNA.value),
    name='consumingGestionInterna'
)
t6 = threading.Thread(
    target=consume_messages_from_publisher_trapping_queue,
    args=(app, channels[5], PossiblePublishers.USUARIO.value),
    name='consumingUsuario'
)
t7 = threading.Thread(
    target=consume_messages_from_publisher_trapping_queue,
    args=(app, channels[6], PossiblePublishers.AUTENTICACION.value),
    name='consumingAutenticacion'
)

del channels

for thread in [t1, t2, t3, t4, t5, t6, t7]:
    thread.start()


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
    pass
