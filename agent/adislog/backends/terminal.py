from ..constants import MSG_FORMAT,LOG_LEVELS, LEVEL_FATAL, LEVEL_ERROR

from sys import stdout, stderr

class terminal:
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
        
        msg=MSG_FORMAT.format(
            project_name=project_name,
            message=message,
            datetime=datetime,
            filename=filename,
            function=function,
            line_number=line_number,
            log_level=LOG_LEVELS[log_level],
            pid=pid,
            ppid=ppid,
            cwd=cwd
            )
        
        print(msg,file=self._stdout if log_level!=LEVEL_FATAL and log_level!=LEVEL_ERROR else self._stderr)

