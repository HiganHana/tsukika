from asyncio.log import logger
import logging
from typing import Callable
import typing
import os
from higanhanaSdk.frame.config import DcMfConfig
from higanhanaSdk.frame.ext_bot import BotExtension
from higanhanaSdk.frame.ext_flask import flaskExtension
from higanhanaSdk.frame.ext_sqla import sqlaExtension
import inspect
import logging

class DcMainframe(sqlaExtension, flaskExtension, BotExtension):

    
    @classmethod
    def _init_mode_internal(cls, project_name : str):
        if not project_name:
            raise ValueError("project_name must not be empty")
        
        os.makedirs(project_name, exist_ok=True)    
        with open(os.path.join(project_name, "config.py"), "w") as f:
            pass
        
        with open(os.path.join(project_name, "config.json"), "w") as f:
            f.write("{}")
             
        with open(os.path.join(project_name, "__init__.py"), "w") as f:
            pass
        
        with open(os.path.join(project_name, "bot.py"), "w") as f:
            f.write(f"""
from higanhanaSdk.frame import DcMainframe

# if sqla
# from .models import base

mf = DcMainframe("{project_name}")
""")
    
    @classmethod
    def init(cls, project_name, init_mode : bool = False, **kwargs):
        import sys
        # check if arg contains "--init"    
        if "--init" in sys.argv:
            init_mode = True
    
        if init_mode:
            cls._init_mode_internal(project_name)
    
        return cls(project_name, init_mode=init_mode, **kwargs)
    
    
    def __getattribute__(self, name: str):
        if name.startswith("setup_"):
            # if its init mode, load init method if exist
            if self._init_mode:
                func =  getattr(self, f"init_{name[6:]}", lambda **kwargs: None)
                return func
            
            func = super().__getattribute__(name)
            
            return func
                
        return super().__getattribute__(name)
    
    def __init__(self,
        project_name : str,
        mod_config = None,
        init_mode : bool = False,
        **kwargs
    ) -> None:
        self.project_name = project_name
        self.config = DcMfConfig(
            **kwargs, 
            project_name=project_name,
            mod_config=mod_config, 
        )
        self._init_mode = init_mode

        self.logger = logging.getLogger(self.project_name)

    def _run_flag(self, name : typing.Union[str, typing.Callable]):
        """
        this is a post-setup function
        
        every setup function, upon return, will set its return value to a flag
        
        by storing a lambda function to the flag, we can then acheive abstracted calling for post-setup functions
        
        """
        
        if (
            isinstance(name, Callable) and not isinstance(name, str)
            and (func := getattr(self,(flagname:=f"_{name.__name__}_flag") , None)) is None
        ):
            return   
        elif (
            isinstance(name, str) 
            and (func := getattr(self, (flagname:=f"_{name}_flag"), None)) is None
        ):
            return 
        if not isinstance(func, Callable):
            raise ValueError(f"{flagname} is not callable")
        
        func()
    
    def _must_have_flag(self, name : typing.Union[str, typing.Callable]):
        if (
            isinstance(name, str) 
            and (func := getattr(self, (name:=f"_{name}_flag"), None)) is not None
        ):
            return False
        elif (
            isinstance(name, Callable) 
            and (func := getattr(self,(name:=f"_{name.__name__}_flag") , None)) is not None
        ):
            return False
        
        return True
    
    

    def run(self):
        self._run_flag("setup_flask")
        self._run_flag("setup_flask_cold_trigger")
        
        self._run_flag("setup_bot")
        
if __name__ == "__main__":
    
    frame = DcMainframe.init("something", init_mode=True)
    frame.setup_bot()
    frame.setup_flask()
    frame.setup_flask_sqlalchemy()
    frame.setup_flask_cold_trigger()
        
    
    frame = DcMainframe.init("something")
    frame.setup_bot(discord_token="123")
    frame.setup_flask()
    frame.setup_flask_sqlalchemy()
    frame.setup_flask_cold_trigger(cold_trigger_token="123")
        
    