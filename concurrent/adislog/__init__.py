"""Simple log with function of logging the caller function with arguments and colorful output"""

from .methods import adislog_methods 
from .inspect import inspect
from .process import get_process_details
from .exceptions import EXCEPTION_BACKEND_DO_NOT_EXISTS
from .traceback import traceback

from pprint import pformat
from time import strftime
from sys import exit


class adislog(adislog_methods):
    def __init__(self,
                 time_format=None,
                 log_file:str=None,
                 debug:bool=False,
                 init_message:str="adislog module initializated.",
                 backends:list or array=['file_plain','terminal_table'],
                 project_name:str="Default",
                 rabbitmq_host=None,
                 rabbitmq_port=None,
                 rabbitmq_user=None,
                 rabbitmq_passwd=None,
                 rabbitmq_queue='logs',
                 **kwargs):
        """Time format have to be format of the time.strftime function.
log_file:str                 - Specify the path of the log file,
privacy:bool                 - Set to true log the caller of the function with the arguments. Name of the function otherwise.
debug:bool                   - Sets the condition to store the debug messages or not.
init_message:str             - Message showed after initialisation of the adislog,
backends:list or array       - List is a list with enabled backends. Backends:
    file_plain        - Saves the log to the spewcified file as a plain text.
    terminal          - Prints the log to the console with no formatting.
    terminal_colorful - Same as above - additionally colores the output.
    terminal_table    - Show tabulated log on the console - never be confused by log again.

Note that all of the console backends writes the fatal messages to the STDERR pipe.
"""
        self._backends=[]
        self._time_format="%d/%m/%Y %H:%M:%S" if time_format is None else time_format
        self._log_file='log.log' if log_file is None else log_file
        self._debug=debug
        self._init_message=init_message
        self._project_name=project_name

        self._inspect=inspect()
        self._traceback=traceback()
        
        for a in backends:
            o=None        
            
            if a == 'terminal':
                from .backends import terminal

                o=terminal.terminal()
                
            elif a == 'terminal_colorful':
                from .backends import terminal_colorful
                o=terminal_colorful.terminal_colorful()
                
            elif a == 'terminal_table':
                from .backends import terminal_table
                o=terminal_table.terminal_table()
                
            elif a == 'file_plain':
                from .backends import file_plain
                o=file_plain.file_plain(log_file=self._log_file)
            
            elif a == 'rabbitmq_emitter':
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
            
                    
    def _init_msg(self):
        self.info(self._init_message)
        
    def _message(self,log_level:int, log_item, project_name=None):
        if log_level >0 or self._debug: 
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
            
            time=strftime(self._time_format)
            caller_info=self._inspect.get_caller()
            process_details=get_process_details()
                            
            msg={
            "project_name": project_name if project_name else self._project_name,
            "log_level":log_level,
            "message":message, 
            "datetime":time, 
            **caller_info, 
            **process_details
            }

            self._emit_to_backends(msg)


    def _emit_to_backends(self, msg):
        for backend in self._backends:
            backend.emit(**msg)
        
