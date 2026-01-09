#!/usr/bin/python3.11
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
import sys

_rabbitmq_connection=BlockingConnection(
	ConnectionParameters(
		host='127.0.0.1',
		port=5672,
		credentials=PlainCredentials(
			'admin',
			'sicken'
			)
		))
_rabbitmq_channel=_rabbitmq_connection.channel()

try:
	_rabbitmq_channel.queue_declare(queue=sys.argv[1], durable=True)
	sys.exit(0)
except:
	raise
	sys.exit(1)

