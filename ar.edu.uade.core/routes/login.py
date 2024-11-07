import sender
from flask import Blueprint, request

from brokers.RabbitMQ import start_rabbitmq_connection
from utilities import storage

login = Blueprint('login', __name__)


@login.route('/login', methods=['POST'])
def login():
    credentials = request.json
    connection, channel = start_rabbitmq_connection(
        storage.rabbitmq_user_username,
        storage.rabbitmq_user_password,
        storage.rabbitmq_host,
        storage.rabbitmq_port
    )
    authenticator = sender.Authenticator(connection, channel, 'core_auth')
    return authenticator.authenticate(credentials)
