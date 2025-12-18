from os import getpid, getppid, getcwd

def get_process_details():
    return {'pid':getpid(), 'ppid':getppid(), 'cwd': getcwd()}
