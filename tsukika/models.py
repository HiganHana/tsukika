
import typing
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, JSON
base = declarative_base()

ALLOWED_FIELDS = [
    "honkai_uid",
    "genshin_uid",
]

class Profile(base):
    __tablename__ = 'profile'
    discord_id = Column(Integer, primary_key=True)
    fields : typing.Dict[str, str] = Column(JSON, nullable=False, default={})
    
class Trophy(base):
    __tablename__ = 'trophy'
    name : str = Column(String, primary_key=True)
    unique : bool = Column(Integer, nullable=False, default=0)
    users : typing.List[int] = Column(JSON, nullable=False, default=[])


    
    