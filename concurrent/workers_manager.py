from .constants.workers_manager import MANIFEST_FILE
from pathlib import Path
from subprocess import Popen, PIPE
from platform import system
from yaml import safe_load
from copy import deepcopy
from select import select
from time import sleep
from uuid import uuid4
from sys import executable

if system()=='Linux' or system()=='Darwin':
    from os import environ, getcwd, listdir, chdir, kill, setuid, setgid, set_blocking
else:
    from os import environ, getcwd, listdir, chdir, kill, set_blocking


def demote(uid, gid):
    def prepare_process():
        setgid(gid)
        setuid(uid)


    return prepare_process

class Workers_manager:
    _root=None
    _log=None
    _config=None

    _workers={}
    _active_workers=[]

    _stdout_line_buffer={}
    _stderr_line_buffer={}

    def __init__(self, root):
        self._root=root
        self._log=root._log
        self._log.debug('Starting initialization of the Workers_manager')
        
        self._config=root._config
        self._config_workers=root._config_workers
        
        self._log.success('Initialisation of workers_manager successed!')

    def _count_active_workers(self, name:str):
        count=0
        for a in self._active_workers:
            if a['name']==name:
                count+=1
        return count

    def _start_workers(self,name):        
        for _ in range(self._count_active_workers(name),self._workers[name]['workers']):
            self._start_worker(name)
                    
    def _generate_python_path(self, worker_dir, modules_dir):
        s="{0}:{1}" if system()=='Linux' or system()=='Darwin' else "{0};{1}"
        return s.format(worker_dir, modules_dir)
    
    def _start_worker(self,name):
        self._log.info('Starting worker: '+name)
        worker_uuid=str(uuid4())
        worker=self._workers[name]

        env=environ.copy()
        env['PYTHONPATH']=self._generate_python_path(worker['worker_dir'], self._root._paths("CONCURRENT_MODULES_DIRECTORY"))
        env['PYTHONUNBUFFERED']='True'
        env['PYTHONIOENCODING']='utf-8'
        env['WEBKIT_DISABLE_COMPOSITING_MODE']='1'

        
        chdir(worker['worker_dir'])
        p=Popen(
                [
                    worker['exec'].absolute() if worker['exec'] else executable,
                    worker['script'].absolute()
                ],
                env=env,
                shell=False,
                preexec_fn=demote(worker['uid'], worker['gid']) if self._config.general.daemonize else None,
                stdout=PIPE,
                stderr=PIPE,
                #pipesize=1024*200
                )

        set_blocking(p.stdout.fileno(), False)
        set_blocking(p.stderr.fileno(), False)

        self._active_workers.append({
            "worker_uuid": worker_uuid,
            "name":name,
            'process_obj': p,
            'polled': False
        })
        chdir(self._root._paths("CONCURRENT_MAIN_DIRECTORY"))
        
    def _clear_zombies(self):
        for worker in self._active_workers:
            poll=worker['process_obj'].poll()
            if poll != None:
                del self._active_workers[self._active_workers.index(worker)]

    def _declare_worker(self,name:str, exec:Path or type(None), script:Path, workers:int, worker_dir:Path, uid:int, gid: int, stderr_as_info: bool, **kwargs):
        self._workers[name]={
            "name":name,
            "exec":exec,
            "script":script,
            "workers":workers,
            "worker_dir":worker_dir,
            "uid":uid,
            "gid":gid,
            "stderr_as_info": stderr_as_info,
             }

    def _parse_manifest(self, manifest_path:Path):
        with open(manifest_path, 'r') as manifest_file:
            return safe_load(manifest_file)
            

    def load_workers(self):
        for worker in self._config_workers:
            settings=self._config_workers[worker]
            manifest_file=Path(self._root._paths("CONCURRENT_WORKERS_DIRECTORY")) / worker / "manifest.yaml"
            manifest=self._parse_manifest(manifest_file)            

            if settings['enable']:
                self._declare_worker(
                    name=worker,
                    exec=Path(manifest['exec']) if manifest['exec']!='__DEFAULT_PYTHON_3__' else None,
                    script=Path(self._root._paths("CONCURRENT_WORKERS_DIRECTORY")) / worker / manifest['script'],
                    uid=settings['uid'],
                    gid=settings['gid'],
                    workers=settings['workers_count'],
                    worker_dir=Path(self._root._paths("CONCURRENT_WORKERS_DIRECTORY")) / worker,
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

    def stop_windows(self):
        for worker in self._active_workers:
            process=worker['process_obj']
            process.terminate()


        while not self._all_polled:
            self._poll_processes()
            sleep(0.1)


        for worker in self._active_workers:
            self._read_process_stream_windows(worker,'stdout')
            self._read_process_stream_windows(worker,'sterr')

    def _read_process_stream(self, process, stream):
        x=[process['process_obj'].stdout if stream=='stdout' else process['process_obj'].stderr ]
        r, w, e=select(x,[],[], .000001)
        for a in r:
            data=a.read()

            if data:
                if stream=='stdout':
                    if process['worker_uuid'] in self._stdout_line_buffer:
                        self._stdout_line_buffer[process['worker_uuid']]+=data.decode('utf-8')
                    else:
                        self._stdout_line_buffer[process['worker_uuid']]=data.decode('utf-8')

                    if "\n" in self._stdout_line_buffer[process['worker_uuid']]:
                        self._log.info(project_name=process['name'], log_item=self._stdout_line_buffer[process['worker_uuid']])
                        del self._stdout_line_buffer[process['worker_uuid']]
                    
                else:
                    if process['worker_uuid'] in self._stderr_line_buffer:
                        self._stderr_line_buffer[process['worker_uuid']]+=data.decode('utf-8')
                    else:
                        self._stderr_line_buffer[process['worker_uuid']]=data.decode('utf-8')


                    if "\n" in self._stderr_line_buffer[process['worker_uuid']]:
                        self._log.error(project_name=process['name'], log_item=self._stderr_line_buffer[process['worker_uuid']])
                        del self._stderr_line_buffer[process['worker_uuid']]
    
    def _read_process_stream_windows(self, process, stream):
        st=process['process_obj'].stdout if stream=='stdout' else process['process_obj'].stderr
        data=st.read()

        if data:
            if stream=='stdout':
                if process['worker_uuid'] in self._stdout_line_buffer:
                    self._stdout_line_buffer[process['worker_uuid']]+=data.decode('utf-8')
                else:
                    self._stdout_line_buffer[process['worker_uuid']]=data.decode('utf-8')

                if "\n" in self._stdout_line_buffer[process['worker_uuid']]:
                    self._log.info(project_name=process['name'], log_item=self._stdout_line_buffer[process['worker_uuid']])
                    del self._stdout_line_buffer[process['worker_uuid']]
                
            else:
                if process['worker_uuid'] in self._stderr_line_buffer:
                    self._stderr_line_buffer[process['worker_uuid']]+=data.decode('utf-8')
                else:
                    self._stderr_line_buffer[process['worker_uuid']]=data.decode('utf-8')


                if "\n" in self._stderr_line_buffer[process['worker_uuid']]:
                    self._log.error(project_name=process['name'], log_item=self._stderr_line_buffer[process['worker_uuid']])
                    del self._stderr_line_buffer[process['worker_uuid']]
    
    def task(self):
        for process in self._active_workers:
            self._read_process_stream(process, 'stdout')
            self._read_process_stream(process, 'stderr')
            

        self._clear_zombies()
        for worker in self._workers:
            self._start_workers(worker)

    def task_windows(self):
        for process in self._active_workers:
            self._read_process_stream_windows(process, 'stdout')
            self._read_process_stream_windows(process, 'stderr')
            

        self._clear_zombies()
        for worker in self._workers:
            self._start_workers(worker)