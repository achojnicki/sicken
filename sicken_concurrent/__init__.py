#!/usr/bin/env python3

from .workers_manager import Workers_manager
from .scheduler import Scheduler
from .daemon import Daemon
from .adislog import adislog
from .adisconfig import adisconfig

from platform import system
from pathlib import Path
from sys import exit
from signal import signal, SIGTERM, SIGINT
from platform import system


class SickenConcurrent:
    _active=None

    _daemon=None
    _config=None
    _log=None
    _workers_manager=None
    _scheduler=None
    
    def __init__(self, paths):

        self._paths=paths
        try:
            self._config=adisconfig(self._paths("CONCURRENT_MAIN_CONFIG"))

        except:
            print("Fatal error during loading the main config file. Exitting...")
            raise
            exit(1)
        
        try:
            self._config_workers=adisconfig(self._paths("CONCURRENT_WORKERS_CONFIG"))
        except:
            print("Fatal error during loading the workers config file. Exitting...")
            exit(2)

        _backends=[]
        if not self._config.general.daemonize:
            if self._config.log.print_log:
                if self._config.log.print_log_mode == 'colorful':
                    _backends.append('terminal_colorful')
                elif self._config.log.print_log_mode == 'table':
                    _backends.append('terminal_table')
                elif self._config.log.print_log_mode == 'terminal':
                    _backends.append('terminal')
        else:
            if self._config.log.report_to_systemd:
                _backends.append('terminal')

        if self._config.log.save_to_file:
            _backends.append('file_plain')


        #initialisation of the log module
        try:
            self._log=adislog(
                project_name="sickens-concurrent",
                backends=_backends,
                log_file=Path(self._paths("CONCURRENT_LOGS_DIRECTORY")).joinpath("sicken-concurrent.log"),
                debug=self._config.log.debug,
                )
        except:
            raise
            print("Fatal Error during initializating the log module. Exitting")
            exit(4)
        
        try:
            self._log.info("Initialising Sicken's Concurrent")

            #binding for the signals
            sig1=signal(handler=self._signal_handler, signalnum=SIGTERM)
            sig2=signal(handler=self._signal_handler, signalnum=SIGINT)
            #initialisation of the daemonization module
            if self._config.general.daemonize:
                self._daemon=Daemon(
                    root=self,
                    pidfile=self._config.daemon.pid_file
                    )
            
            #initialisating all of the child objects
            self._scheduler=Scheduler(self)
            self._workers_manager=Workers_manager(self)
            
            #starting workers if enabled in config
            if self._config.general.start_workers:
                self._workers_manager.load_workers()
                if system()=='Linux' or system()=='Darwin':
                    self._scheduler.add_task('workers_manager',self._workers_manager.task, 100)
                else:
                    self._scheduler.add_task('workers_manager',self._workers_manager.task_windows, 100)
            
        except:
            self._log.fatal('Initialisation failed. Exitting...')
            self._log.exception()
            exit(5)

    def _signal_handler(self, sig, frame):
        """Callback handler for the signal coming from OS"""
        self._log.debug('Got the signal')
        if sig==SIGTERM or sig==SIGINT:
            self.stop()

    def stop(self):
        try:
            self._log.debug('Got termination signal. Starting procedure...')

            self._active=False
            self._scheduler.stop()
            if system()=='Linux' or system()=='Darwin':
                self._workers_manager.stop()
            else:
                self._workers_manager.stop_windows()
            if self._daemon:
                self._daemon.stop()
            self._log.success('Exitting...')
            exit(0)

        except SystemExit:
            pass
        
        except Exception:
            self._log.fatal('Fatal error during stop procedure. Exitting...')
            self._log.exception()
            exit(5)

    def start(self):
        try:
            self._log.debug("Called start method")
            self._active=True
            if self._daemon:
                self._log.info('Starting as daemon...')
                self._daemon.daemonize()
                
            self._scheduler.start()
        except SystemExit:
            pass

        except Exception:
            self._log.fatal('Error occured during start procedure. Exitting...')
            self._log.exception()
            exit(6)

