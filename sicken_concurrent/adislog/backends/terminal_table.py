from ..constants import LOG_LEVELS, LEVEL_FATAL, LEVEL_ERROR, TERMINAL_COLORS

from tabulate import tabulate
from colored import stylize, fg, bg, attr
from sys import stdout, stderr
from os import get_terminal_size
from pprint import pformat, pprint

class terminal_table:
    def __init__(self):
        self._stderr=stderr
        self._stdout=stdout
        
        self._spacing=7
        self._first_col=11
        
    def _get_line_breaker(self):
        return get_terminal_size().columns-self._first_col-self._spacing-1
    
    def _break_line(self,string:str):
        buff=""
        for i,letter in enumerate(string):
            if i%self._get_line_breaker()==0 and i>0:
                buff+="\n"
            buff+=letter
        return buff
    
    def _get_tb_table(self,tb):
        pass
    
    def emit(
        self,
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
        
        table_data=[
            [stylize("Title",attr("bold")),stylize("Value",attr("bold"))],
            [stylize("Project Name",attr("bold")), project_name],
            [stylize("Date Time",attr("bold")),datetime],
            [stylize("Log Level",attr("bold")),stylize(LOG_LEVELS[log_level],TERMINAL_COLORS[log_level])],
            [stylize("File",attr("bold")),self._break_line(filename) if len(filename)>self._get_line_breaker() else filename],
            [stylize("Function",attr("bold")),self._break_line(function) if len(function)>self._get_line_breaker() else function],
            [stylize("Line Number",attr("bold")), str(line_number)],
            [stylize("PID",attr("bold")),pid],
            [stylize("PPID",attr("bold")),ppid],
            [stylize("CWD",attr("bold")),self._break_line(cwd) if len(cwd)> self._get_line_breaker() else cwd],
            [stylize("Message",attr("bold")),self._break_line(message) if len(message)>self._get_line_breaker() else message]
            ]
        
        #if excpt_data:
            #in excpt_data:
                #pprint(excpt_item)
        
        msg=tabulate(table_data,tablefmt="fancy_grid")
        
        
        print(msg,file=self._stdout if log_level!=LEVEL_FATAL and log_level!=LEVEL_ERROR else self._stderr)

            
