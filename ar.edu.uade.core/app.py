from flask import Flask
from Exchangers import Messager

app = Flask(__name__)

Messager.prueba()

@app.route('/')
def _enviar_frontend():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
