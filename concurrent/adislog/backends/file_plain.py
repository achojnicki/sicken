from ..constants import MSG_FORMAT, LOG_LEVELS

class file_plain:
    def __init__(self,
                 log_file,
                 **kwargs
                 ):
        self._log_file=log_file
        
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
        
        with open(self._log_file,'a', encoding="utf-8") as log_file:
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
                cwd=cwd)+"\n"
            
            log_file.write(msg)
        
    
        
