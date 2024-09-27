import json
import threading
from flask_socketio import SocketIO, emit
from flask import Flask, render_template
from Connection.Connection import start_rabbitmq_connection, end_connection
"""
from Consumer.Tracing import consume_tracing, inicializar_tracing
from Database.Cassandra import start_cassandra_connection
"""
from Senders.Usuario import inicializar_usuario, publish_usuario, consume_usuario

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' #TODO abstraer

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
    t1 = threading.Thread(target=consume_usuario(channel), name='t1')
    #t2 = threading.Thread(target=consume_e_commerce(channel), name='t2')
    #t3 = threading.Thread(target=consume_gestion_financiera(channel), name='t3')
    #t4 = threading.Thread(target=consume_gestion_interna(channel), name='t4')
    #t5 = threading.Thread(target=consume_tracing(channel), name='t5')
    t6 = threading.Thread(target=socketio.run(app, debug=True), name='t6')

    t1.start()
    #t2.start()
    #t3.start()
    #t4.start()
    #t5.start()
    t6.start()