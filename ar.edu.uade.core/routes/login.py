import json

from sender import Authenticator
from flask import Blueprint, request

from brokers.RabbitMQ import start_rabbitmq_connection
from utilities import storage

login = Blueprint('login', __name__)


@login.route('/authlogin', methods=['GET'])
def signin():
    username = request.args.get('username')
    password = request.args.get('password')
    cheison = {
        'username': username,
        'password': password
    }
    credentials = json.dumps(cheison)
    connection, channel = start_rabbitmq_connection(
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password,
        storage.rabbitmq_host,
        storage.rabbitmq_port
    )
    authenticator = Authenticator(connection, channel, 'core_auth')
    return authenticator.authenticate(credentials)
