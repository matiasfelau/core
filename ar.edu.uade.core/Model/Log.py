"""
import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from Database.Cassandra import syncronize_cassandra_tables


class LogModel(Model):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    status = columns.Integer(index=True)
    timestamp = columns.DateTime(index=True, clustering_order='DESC')
    ttl = columns.Integer()
    payload = columns.Text()
    origin = columns.Text(index=True)
    destination = columns.Text(index=True)

def save_log(status, timestamp, ttl, payload, origin, destination):
    LogModel.create(status=status, timestamp=timestamp, ttl=ttl, payload=payload, origin=origin, destination=destination)
    syncronize_cassandra_tables()
"""
