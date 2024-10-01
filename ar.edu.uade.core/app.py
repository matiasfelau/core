import json
import os
import threading
from flask_socketio import SocketIO, emit
from flask import Flask, render_template
from Connection.Connection import start_rabbitmq_connection, end_connection
from Consumer.Core import consume_core, inicializar_core
from Utils import System

"""
from Consumer.Tracing import consume_tracing, inicializar_tracing
from Database.Cassandra import start_cassandra_connection
"""
from Senders.Usuario import inicializar_usuario, publish_usuario, consume_usuario

app = Flask(__name__)

environment_variables = System.get_environment_variables()

app.config['SECRET_KEY'] = environment_variables[2] #TODO verificar

socketio = SocketIO(app)

"""
inicio de conexiones
"""

connection, channel = start_rabbitmq_connection()
#start_cassandra_connection()
diccionario = {
    "ttl":"3"
}

js = json.dumps(diccionario)
"""
inicializacion de colas, exchanges y 

"""
inicializar_core(channel)
inicializar_usuario(channel)
#inicializar_tracing(channel)
"""
prueba de publicacion de json
"""

publish_usuario(channel,js)


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
    t1 = threading.Thread(target=consume_usuario(channel), name='ConsumingUsuario')
    #t2 = threading.Thread(target=consume_e_commerce(channel), name='ConsumingECommerce')
    #t3 = threading.Thread(target=consume_gestion_financiera(channel), name='ConsumingFinanciera')
    #t4 = threading.Thread(target=consume_gestion_interna(channel), name='ConsumingInterna')
    #t5 = threading.Thread(target=consume_tracing(channel), name='ConsumingTracing')
    t6 = threading.Thread(target=consume_core(channel), name='ConsumingCore')
    t7 = threading.Thread(target=socketio.run(app, host=host, port=port, debug=True), name='runningApp')


    t1.start()
    #t2.start()
    #t3.start()
    #t4.start()
    #t5.start()
    t6.start()

