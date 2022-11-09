
from posixpath import isabs
from higanhanaSdk.frame.keys import DcMainframeCore, DcMainframeKeys
import orjson
import inspect
import os

class DcMfConfig:
    """
    config class is intentionally designated to be an independent class
    
    by default, it loads a config.json and config.py file inside the {project_name} folder
    
    fields contained in config.py will be immutable. Attempting to edit them will result AttributeError
    
    fields contained in config.json is io-bound, meaning that it will write to disk every time it is changed
    
    NOTE `orjson` is used instead of the standard `json` module to improve performance. (10x faster)
    """
    
    def __init__(self,
        project_name : str,
        default_json_config_path : str = DcMainframeCore.default_json_config_path.value,     
        enable_json_config : bool = DcMainframeCore.enable_json_config.value,
        enable_mod_config : bool = DcMainframeCore.enable_mod_config.value,  
        default_mod_config_path : str = DcMainframeCore.default_mod_config_path.value,
        mod_config = None,
        **kwargs
    ) -> None:
        self._project_name = project_name
        self._enable_json_config = enable_json_config
        self._enable_mod_config = enable_mod_config
        
        if self._enable_json_config:
            self._config_json_path = default_json_config_path
            if not os.path.isabs(self._config_json_path):
                self._config_json_path = os.path.join(self._project_name, self._config_json_path)
                self._config_json_path = os.path.abspath(self._config_json_path)
            
            self._json_config = self._load_json_config()
            self._json_config.update(**kwargs)
            
        self._mod_config = mod_config
        if self._enable_mod_config and self._mod_config is None:
            import importlib
            import importlib.util
            mod_path = default_mod_config_path
            if not os.path.isabs(mod_path):
                mod_path = os.path.join(self._project_name, mod_path)
            mod_path = os.path.abspath(mod_path)

            spec = importlib.util.spec_from_file_location(self._project_name + ".config" , mod_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._mod_config = module
            
    def _load_json_config(self):
        if self._config_json_path is None:
            return {}
        
        with open(self._config_json_path, "rb") as f:
            return orjson.loads(f.read())
        
    def _save_json_config(self):
        if self._config_json_path is None:
            return    
    
        with open(self._config_json_path, "wb") as f:
            f.write(orjson.dumps(self._json_config))
        
    def __getattribute__(self, name : str):
        if name.startswith("_") or name in ["get"]:
            return super().__getattribute__(name)
        
        if self._enable_json_config and name in self._json_config:
            return self._json_config[name]
        
        if (
            self._enable_mod_config 
            and self._mod_config is not None 
            and hasattr(self._mod_config, name)
        ):
            return getattr(self._mod_config, name)
        
        if name in DcMainframeKeys.__members__.keys():
            return DcMainframeKeys.__members__[name].value
        
        raise AttributeError(f"Attribute {name} not found")
    
    def __setattr__(self, name : str, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        
        if (
            self._enable_mod_config 
            and self._mod_config is not None 
            and hasattr(self._mod_config, name)
        ):
            raise AttributeError(f"Attribute {name} is read-only")
        
        if self._enable_json_config:
            self._json_config[name] = value
            self._save_json_config()
            return
        
        raise AttributeError(f"Attribute {name} not found")
    
    def __setitem__(self, name : str, value):
        self.__setattr__(name, value)
        
    def __getitem__(self, name : str):
        return self.__getattribute__(name)
    
    def __contains__(self, name : str):
        if name in self._json_config:
            return True
        
        if (
            self._enable_mod_config 
            and self._mod_config is not None 
            and hasattr(self._mod_config, name)
        ):
            return True
        
        return False
    
    def get(self, name : str, default = None):
        return getattr(self, name, default)

        
