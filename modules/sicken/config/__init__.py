from yaml import safe_load, dump
from pathlib import Path
from pprint import pformat
from platform import system


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self     
        
class Config:    
    def __init__(self, root):
        self._root=root

        if system()== 'Linux' or system()=='Darwin':
            self._config_path=Path(f"/opt/sicken/configs/{self._root.project_name}.yaml")

        elif system()=='Windows':
            self._config_path=Path(f"C:\\\\sicken\\configs\\{self._root.project_name}.yaml")


        self._load_config()


    def _load_config(self):
        self._config={}
        with open(self._config_path,'r') as config_file:
            config_data=safe_load(config_file)
            
            for item in config_data:
                self._config[item]=AttrDict(config_data[item])
    
    def has_category(self, category):
        return category in self._config

    def save(self):
        d={}
        for data in self._config:
            d[data]=dict(self._config[data])

        with open(self._config_file,'w') as config_file:
            dump(d, config_file, sort_keys=False)

    def __getattr__(self, attr):
        return self._config[attr]

    def __getitem__(self, attr):
        return self._config[attr]
        
    def __repr__(self):
        return pformat(self._config)
