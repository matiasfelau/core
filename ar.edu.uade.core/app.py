from flask import Flask
from Senders import *
from Senders.Usuario import Usuario

app = Flask(__name__)
usuario = Usuario()
usuario.publish('Hello prueba ')
@app.route('/')
def _enviar_frontend():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
