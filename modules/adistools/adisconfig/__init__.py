from yaml import safe_load, dump
from pathlib import Path
from pprint import pformat

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self     
        
class adisconfig:
    _config=None
    _config_file=None
    
    def __init__(self, config_file):
        self._config={}
        
        self._config_file=Path(config_file)
        self._load_config()


    def _load_config(self):
        with open(self._config_file,'r') as config_file:
            config_data=safe_load(config_file)
            
            for item in config_data:
                self._config[item]=AttrDict(config_data[item])
    
    def save(self):
        d={}
        for data in self._config:
            d[data]=dict(self._config[data])

        with open(self._config_file,'w') as config_file:
            dump(d, config_file, sort_keys=False)

    def __getattr__(self, attr):
        return self._config[attr]

    def __repr__(self):
        return pformat(self._config)
