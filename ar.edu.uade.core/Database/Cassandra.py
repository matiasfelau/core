import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from datetime import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from Model.Log import LogModel

def start_cassandra_connection():
    connection.setup(['127.0.0.1'], "cqlengine", protocol_version=3) #TODO extraer lista hosts

def syncronize_cassandra_tables():
    sync_table(LogModel)

def stop_cassandra_connection(cluster):
    pass