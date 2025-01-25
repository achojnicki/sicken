from pathlib import Path
from subprocess import Popen, PIPE
from os import environ, getcwd, listdir, chdir, kill, setuid, setgid, set_blocking
from copy import deepcopy
from select import select
from time import sleep


def demote(uid, gid):
    def prepare_process():
        setgid(gid)
        setuid(uid)


    return prepare_process


class Uwsgi_manager:
    _root=None
    _log=None
    _config=None

    _workers={}
    _active_workers=[]
    
    _stdout_line_buffer=""
    _stderr_line_buffer=""

    def __init__(self, root):
        self._root=root
        self._log=root._log
        self._log.debug('Starting initialization of the UWSGI_manager')
        self._config=root._config 
        self._config_uwsgi_workers=root._config_uwsgi_workers
         
        self._log.success('Initialisation of UWSGI_manager successed!')

    def _count_active_workers(self, name:str):
        count=0
        for a in self._active_workers:
            if a['name']==name:
                count+=1
        return count

    def _start_workers(self,name):        
        for _ in range(self._count_active_workers(name),1):
            self._start_worker(name)

    def _generate_python_path(self, modules_dir):
        return "{0}".format(modules_dir)
    
    def _start_worker(self,name):
        self._log.info('Starting UWSGI worker: '+name)
        worker=self._workers[name]
        

        env=environ.copy()
        env['PYTHONPATH']=self._generate_python_path(self._config.directories.modules_directory)

        p=Popen(
                [
                    worker['exec'].absolute(),
                    '--ini',
                    worker['ini_file']
                ],
                shell=False,
                preexec_fn=demote(worker['uid'],worker['gid']) if self._config.general.daemonize else None,
                stdout=PIPE,
                stderr=PIPE,
                env=env,
                #pipesize=1024*200
                )
        set_blocking(p.stdout.fileno(), False)
        set_blocking(p.stderr.fileno(), False)



        self._active_workers.append({
            "name":name,
            'process_obj': p,
            "polled": False
        })
        
    def _clear_zombies(self):
        for worker in self._active_workers:
            poll=worker['process_obj'].poll()
            if poll != None:
                del self._active_workers[self._active_workers.index(worker)]


    def _declare_uwsgi_worker(self,name:str, exec:Path, ini_file:Path, uid:int, gid:int, stderr_as_info: bool, **kwargs): 
        self._workers[name]={
            "name":name,
            "exec":exec,
            "ini_file":ini_file,
            "uid":uid,
            "gid":gid,
            "stderr_as_info": stderr_as_info
             }

    def load_uwsgi_workers(self):
        for worker in self._config_uwsgi_workers:
            settings=self._config_uwsgi_workers[worker]
            ini_file=Path(self._config.directories.ini_directory+"/"+worker+'.ini')

            if settings['enable'] and ini_file.is_file():
                self._declare_uwsgi_worker(
                    name=worker,
                    exec=Path(self._config.uwsgi.uwsgi_executable_path),
                    ini_file=ini_file,
                    uid=settings['uid'],
                    gid=settings['gid'],
                    stderr_as_info=settings['stderr_as_info'] if "stderr_as_info" in settings else False
                )
                
    def _poll_processes(self):
        processes_indexes=[]
        for process in self._active_workers:
            processes_indexes.append(self._active_workers.index(process))

        for process_index in processes_indexes:
            process=self._active_workers[process_index]
            if process['polled'] == False:
                poll=process['process_obj'].poll()
                if poll != None:
                    self._active_workers[process_index]['polled']=True   
    
    @property
    def _all_polled(self):
        for worker in self._active_workers:
            if worker['polled']==False:
                return False
        return True

    def stop(self):
        for worker in self._active_workers:
            process=worker['process_obj']
            kill(process.pid, 15)

         
        

        while not self._all_polled:
            self._poll_processes()
            sleep(0.1)


        for worker in self._active_workers:
            self._read_process_stream(worker,'stdout')
            self._read_process_stream(worker,'sterr')

    def _read_process_stream(self, process, stream):
        x=[process['process_obj'].stdout if stream=='stdout' else process['process_obj'].stderr ]
        r, w, e=select(x,[],[], .000001)
        for a in r:
            data=a.read()

            if data:
                if stream=='stdout':
                    self._stdout_line_buffer+=data.decode('utf-8')

                    if "\n" in self._stdout_line_buffer:
                        self._log.info(project_name=process['name'], log_item=self._stdout_line_buffer)
                        self._stdout_line_buffer=""
                    
                else:
                    self._stderr_line_buffer+=data.decode('utf-8')

                    if "\n" in self._stderr_line_buffer:
                        if not self._workers[process['name']]['stderr_as_info']:
                            self._log.error(project_name=process['name'], log_item=self._stderr_line_buffer)
                        else:
                            self._log.info(project_name=process['name'], log_item=self._stderr_line_buffer)
                            self._stderr_line_buffer=""

    def task(self):
        #iterate through all active UWSGI workers and get the data from STDOUT and STDERR
        for process in self._active_workers:
            self._read_process_stream(process, 'stdout')
            self._read_process_stream(process, 'stderr')
            
        self._clear_zombies()
        for worker in self._workers:
            self._start_workers(worker)