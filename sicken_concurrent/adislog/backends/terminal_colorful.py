from ..constants import MSG_FORMAT,LOG_LEVELS, LEVEL_FATAL, LEVEL_ERROR, TERMINAL_COLORS

from colored import stylize, fg, bg, attr
from sys import stdout, stderr

class terminal_colorful:
    def __init__(self):
        self._stderr=stderr
        self._stdout=stdout
    
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
        cwd:str):

        msg_data={
        "project_name": project_name,
        "datetime":datetime,
        "filename":filename,
        "function":stylize(function,fg(248)),
        "line_number":str(line_number),
        "log_level":stylize(LOG_LEVELS[log_level],TERMINAL_COLORS[log_level]+attr('bold')),
        "message":stylize(message,TERMINAL_COLORS[log_level]),
        "pid":pid,
        "ppid":ppid,
        "cwd":cwd}
        
        msg=MSG_FORMAT.format(**msg_data)
        
        print(msg,file=self._stdout if log_level!=LEVEL_FATAL and log_level!=LEVEL_ERROR else self._stderr)

            
