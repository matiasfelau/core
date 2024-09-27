
from flask import Flask
from Connection.Connection import start_connection, end_connection
from Senders.Usuario import inicializar_usuario, publish_usuario

app = Flask(__name__)

connection = start_connection()


j = {
 "ttl":"3"
}
inicializar_usuario()
publish_usuario(j)
end_connection(connection)

@app.route('/')
def _enviar_frontend():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
