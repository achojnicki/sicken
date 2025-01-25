from ..constants import MSG_FORMAT, LOG_LEVELS

from json import dumps
from pika import BlockingConnection, ConnectionParameters, PlainCredentials


class rabbitmq_emiter:
    _rabbitmq_connection=None
    _rabbitmq_channel=None

    _rabbitmq_host=None
    _rabbitmq_port=None
    _rabbitmq_user=None
    _rabbitmq_passwd=None

    def __init__(self,
                 rabbitmq_host,
                 rabbitmq_port,
                 rabbitmq_queue,
                 rabbitmq_user,
                 rabbitmq_passwd,
                 **kwargs
                 ):
         
        self._rabbitmq_host=rabbitmq_host
        self._rabbitmq_port=rabbitmq_port
        self._rabbitmq_user=rabbitmq_user
        self._rabbitmq_passwd=rabbitmq_passwd
        self._rabbitmq_queue=rabbitmq_queue
    
    def _open_rabbitmq_connection(self):
        self._rabbitmq_connection=BlockingConnection(
            ConnectionParameters(
                host=self._rabbitmq_host,
                port=self._rabbitmq_port,
                credentials=PlainCredentials(
                    self._rabbitmq_user,
                    self._rabbitmq_passwd
                    )
                ))
        
        self._rabbitmq_channel=self._rabbitmq_connection.channel()

    def _close_rabbitmq_connection(self):
        self._rabbitmq_channel.close()
        self._rabbitmq_connection.close()
        
    def emit(self,
             project_name:str,
             message:str,
             datetime:str,
             filename:str,
             function: str,
             line_number:int,
             log_level:int,
             pid:int,
             ppid:int,
             cwd:str,
             excpt_data=None):
        
        msg={
            "project_name":project_name,
            'message':message,
            'datetime':datetime,
            'filename':filename,
            'function':function,
            'line_number':line_number,
            'log_level':LOG_LEVELS[log_level],
            'pid':pid,
            'ppid':ppid,
            'cwd':cwd,
            }
        msg=dumps(msg)

        self._open_rabbitmq_connection()
        self._rabbitmq_channel.basic_publish(
            exchange="",
            routing_key=self._rabbitmq_queue,
            body=msg
        )
        self._close_rabbitmq_connection()
    
        
