from pathlib import Path

import os
import sys
import signal
import psutil

class DaemonizeException(Exception):
    pass
class AnotherInstanceRunning(DaemonizeException):
    pass

class Daemon:
    def __init__(
            self,
            root,
            pidfile,
            ):
        self._root=root
        self._log=self._root._log
        self._pidfile=pidfile

        #Keeping reference of the STDIN, STDOUT and STDERR
        self._stdin=sys.stdin
        self._stdout=sys.stdout
        self._stderr=sys.stderr
        
        #Opening null device to replace the STDIN, STDOUT AND STDERR
        #self._null_stdin=open('/dev/null','r')
        #self._null_stdout=open('/dev/null','a+')
        #self._null_stderr=open('/dev/null','a+')
        
        
    def _prepare_streams(self):
        #Flushing STDOUT and STDERR
        self._stdout.flush()
        self._stderr.flush()
        
        #Switching the STDIN, STDOUT and STDERR with the null ones - Keeping the STDIN, STDOUT and STDERR binded as we want the error messages to be readable by systemd
        #os.dup2(self._stdin.fileno(),self._null_stdin.fileno())
        #os.dup2(self._stdout.fileno(),self._null_stdout.fileno())
        #os.dup2(self._stderr.fileno(),self._null_stderr.fileno())

        #To make sure all the streams are redirected, replacing the sys.stdin, sys.stdout, sys.stderr - causing OSError on attempt to raise exception
        #sys.stdin=self._null_stdin
        #sys.stdout=self._null_stdout
        #sys.stderr=self._null_stderr
 
    def _fork(self):
        try:
            #performing fork
            pid=os.fork()
            if pid>0:
                #Exitting the child process
                sys.exit(0)
        except OSError:
            self._log.fatal('Failed to fork')
            
    def _write_pidfile(self):
        self._log.debug('Writing pidfile')
        with open(self._pidfile,'w+') as pidfile:
            pidfile.write(str(os.getpid()))

    def _remove_pidfile(self):
        os.remove(self._pidfile)
        
    def _pidfile_exists(self):
        return Path(self._pidfile).is_file()

    def _process_active(self):
        try:
            return psutil.Process(int(open(self._pidfile,'r').read())).status() in ['sleeping','running']
        except psutil.NoSuchProcess:
            return False
               
    def _set_env(self):
        os.setsid()
        os.umask(0)
    
    def stop(self):
        self._remove_pidfile()
        
    def daemonize(self):
        """daemonizating procedure"""
        self._log.info('starting daemonizing procedure')
        if self._pidfile_exists():
            if self._process_active():
                raise AnotherInstanceRunning
            else:
                self._remove_pidfile()

        self._fork()
        self._set_env()
        self._fork()
        self._write_pidfile()
        self._prepare_streams()
    
        self._log.success('Daemonizing procedure successed')