from pydantic import BaseModel
import inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute

def sqlalchemy_get_fields(db_model : type):
    names = []
        
    for name, obj in inspect.getmembers(db_model):
        if isinstance(obj, InstrumentedAttribute):
            names.append(name)
            
    return names

def is_sqlalchemy_model(obj : type):
    if hasattr(obj, "_sa_registry"):
        return True
    return False

def sqlalchemy_to_pydantic_compatible(db_model : object, pydantic_model : type):
    """
    checks if both classes (one in sqlalchemy model, the other in pydantic model)

    """
    if not is_sqlalchemy_model(db_model):
        raise TypeError("db_model is not a sqlalchemy model")

    if not issubclass(pydantic_model, BaseModel):
        raise TypeError("pydantic_model is not a pydantic model")
        
    db_model_fields = sqlalchemy_get_fields(db_model)
    pydantic_fields = [x for x in pydantic_model.__fields__.keys()]
    
    return db_model_fields, pydantic_fields 

    
def pydantic_to_sqlalchemy_compatible(pydantic_model : type, db_model : type):
    return sqlalchemy_to_pydantic_compatible(db_model, pydantic_model)

def sqlalchemy_to_pydantic(db_obj : object, pydantic_model : type):
    db_model_fields, pydantic_fields  = sqlalchemy_to_pydantic_compatible(db_obj.__class__, pydantic_model)
    
    extract_dict = {}
    for field in db_model_fields:
        if field not in pydantic_fields:
            continue
        
        extract_dict[field] = getattr(db_obj, field)
        
    return pydantic_model(**extract_dict)

def pydantic_to_sqlalchemy(pydantic_obj : BaseModel, db_model : type):
    db_model_fields, pydantic_fields  = pydantic_to_sqlalchemy_compatible(pydantic_obj.__class__, db_model)
    
    extract_dict = {}
    for field in pydantic_fields:
        if field not in db_model_fields:
            continue
        
        extract_dict[field] = getattr(pydantic_obj, field)
        
    return db_model(**extract_dict)