import importlib
import os
from re import L
import sys
import inspect
import typing

def load_extension(path : str, as_pkg : str = "ext", get : typing.Union[str, type] = None):
    """
    Load a module from a path.

    Args:
        path (str): The file path to the module.
        as_pkg (str, optional): the name package is going to be loaded as into system
        get (typing.Union[str, type], optional): The name of the class or the class itself to be returned. Defaults to None.
    """
    
    filename = os.path.basename(path)
    filename_noext = os.path.splitext(filename)[0]

    spec = importlib.util.spec_from_file_location(f"{as_pkg}.{filename_noext}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{as_pkg}.{filename_noext}"] = module
    spec.loader.exec_module(module)

    if get is None:
        return module

    for name, obj in inspect.getmembers(module):
        if isinstance(get, str) and name == get:
            return obj
        
        elif inspect.isclass(obj) and issubclass(obj, get) and obj != get:
            return obj

    return None

def import_objs(
    folder_path : str, 
    target : typing.Union[str, type] = None, 
    ignore_slash : bool = True, 
    only_object: bool = True, 
    only_type: bool = False
):
    # list all files
    python_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".py")]
    
    # folder path to package format
    folder_package = folder_path.replace("\\", ".").replace("/", ".")
    
    # import all files
    for file in python_files:
        pkg = importlib.import_module(f"{folder_package}.{os.path.splitext(file)[0]}")

        if target is None:
            yield pkg
            continue
        
        for name, obj in inspect.getmembers(pkg):
            if ignore_slash and name.startswith("_"):
                continue
            
            if isinstance(target, str) and name == target:
                yield obj
                break
            elif only_object and isinstance(obj, target) and obj != target:
                yield obj
                break
            
            elif only_type and isinstance(obj, type) and issubclass(obj, target) and obj != target:
                yield obj
                break
        
        
    
    
