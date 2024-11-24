import json

from flask import Blueprint, request

from brokers.RabbitMQ import start_rabbitmq_connection, end_rabbitmq_connection
from utilities import storage
from utilities.authenticator import Authenticator

login = Blueprint('login', __name__)


@login.route('/authlogin', methods=['GET'])
def signin():
    username = request.args.get('username')
    password = request.args.get('password')
    cheison = {
        'user': username,
        'password': password,
        'case': 'login',
        'origin': 'core'
    }
    credentials = json.dumps(cheison)
    connection, channel = start_rabbitmq_connection(
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password,
        storage.rabbitmq_host,
        storage.rabbitmq_port
    )
    try:
        authenticator = Authenticator(connection, channel)
        response = authenticator.authenticate(credentials)
        return response
    except Exception as e:
        print(f'\nError in routes.signin(): \n{str(e)}')
    end_rabbitmq_connection(connection)

