from .constants import LOG_LEVELS
from .methods import adislog_methods 
from .exceptions import EXCEPTION_BACKEND_DO_NOT_EXISTS
from .probes import Probes

from pprint import pformat
from datetime import datetime

class Log(adislog_methods):
    _time_format="%d/%m/%Y %H:%M:%S"

    def __init__(self,
                 debug:bool=False,
                 backends:list or array=['rabbitmq_emitter'],
                 rabbitmq_host=None,
                 rabbitmq_port=None,
                 rabbitmq_user=None,
                 rabbitmq_passwd=None,
                 rabbitmq_queue='sicken-logs',
                 parent=None
                 ):
        self._parent=parent

        self._probes=Probes(self)
        self._backends=[]
        self._debug=debug
        
        
        for a in backends:
            o=None        
            
            if a == 'rabbitmq_emitter':
                from .backends import rabbitmq_emiter
                o=rabbitmq_emiter.rabbitmq_emiter(
                    rabbitmq_host=rabbitmq_host,
                    rabbitmq_port=rabbitmq_port,
                    rabbitmq_user=rabbitmq_user,
                    rabbitmq_passwd=rabbitmq_passwd,
                    rabbitmq_queue=rabbitmq_queue
                    )
            
            
            else:
                raise EXCEPTION_BACKEND_DO_NOT_EXISTS
            
            if o:
                self._backends.append(o)
            


    def _message(self,log_level:int, log_item, exception_data=None):
        if log_level >0 or self._debug: 
            time=datetime.now()

            if type(log_item) is str:
                message=log_item
            
            elif type(log_item) is tuple or type(log_item) is list:
                message=pformat(log_item)
                
            elif type(log_item) is dict:
                message=pformat(log_item)
            
            elif type(log_item) is int:
                message=log_item
                
            elif type(log_item) is bytes or type(log_item) is bytearray:
                message=log_item.decode('utf-8')

            else:
                message=str(log_item) 
            

            msg={
                "project_name": self._parent.project_name,
                "log_level": LOG_LEVELS[log_level],
                "message": message, 
                "strtime": time.strftime(self._time_format),
                "timestamp":time.timestamp(),
                "system": {
                    "node": self._probes.node,
                    "pid": self._probes.pid,
                    "ppid": self._probes.ppid,
                    "cwd": self._probes.cwd,
                },
                "caller": self._probes.caller,
                "app_specific":self._probes.parent,
                "exception_data": exception_data

            }

            self._emit_to_backends(msg)


    def _emit_to_backends(self, msg):
        for backend in self._backends:
            backend.emit(msg)