import threading
import time

from flask import Flask, render_template
from flask_socketio import SocketIO

from brokers.RabbitMQ import start_rabbitmq_connection, end_rabbitmq_connection
from queues.Publisher import initialize_publisher, consume_messages_from_publisher_trapping_queue
from queues.consumers.Core import consume_messages_from_core_queue, initialize_core_queue
from utilities.Configuration import initialize_configuration_reader
from utilities.Enumerations import PossiblePublishers
from utilities.Environment import *
from utilities.Logger import initialize_logging_for_messaging_errors

app = Flask(__name__)

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

for i in range(6):
    while True:
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
        if (connection != None):
            break
        time.sleep(5)
    
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

#Publishers
initialize_publisher(channels[0], reader, PossiblePublishers.E_COMMERCE.value)
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
        'debug': True},
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

del channels

for thread in [t1, t2, t3, t4, t5, t6]:
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
