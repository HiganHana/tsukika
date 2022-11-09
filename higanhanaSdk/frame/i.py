import logging
import typing


from higanhanaSdk.frame.config import DcMfConfig
import inspect
import functools

_NOSAVE = object()

class mfi:
    """
    this is currently a placeholder interface for the mainframe 
    """
    
    project_name :str
    _init_mode : bool
    config : DcMfConfig
    logger : logging.Logger
    
    @typing.overload
    def _has_flag(self, name : typing.Union[str, typing.Callable]): pass
    
    @typing.overload
    def _must_have_flag(self, name : typing.Union[str, typing.Callable]): pass
    
    @classmethod
    def _parse_params(cls, func):
        def wrapper(self, **kwargs):
            if hasattr(self, f"_{func.__name__}_flag"):
                return _NOSAVE
            
            # inspect func parameters
            params = {}
            for k, v in inspect.signature(func).parameters.items():
                if k == "self":
                    continue
                
                if isinstance(v.default, inspect._empty) or v.default == inspect._empty:
                    params[k] = None
                else:
                    params[k] = v.default
            
            
            # filter kwargs to only contain parameters
            for k, v in params.items():
                if k in kwargs:
                    params[k] = kwargs[k]
                    del kwargs[k]
            
            # check if a config key exist
            config : DcMfConfig = self.config
            
            for k, v in params.items():
                if k.startswith("_"):
                    continue
                
                config_val = config.get(k)
                if v is None and config_val is not None:
                    params[k] = config_val
                elif v is not None and v != config_val:
                    config[k] = v
                elif v is None and config_val is None:
                    raise ValueError(f"Parameter {k} is required")

            return func(self, **params)
                
        return wrapper

    @classmethod
    def _save_flag(cls, func):
        @functools.wraps(func)
        def wrapper(self, **kwargs):
            val = func(self, **kwargs)
            if val == _NOSAVE:
                return
            
            self.__setattr__(f"_{func.__name__}_flag", val)
            return val
        return wrapper
