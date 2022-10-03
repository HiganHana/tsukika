
from datetime import datetime
import typing
import discord
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, JSON, LargeBinary, Date, DateTime, Boolean, ForeignKey
base = declarative_base()

class Profile(base):
    __tablename__ = 'profile'
    discord_id = Column(Integer, primary_key=True)
    fields : typing.Dict[str, str] = Column(JSON, nullable=False, default={})
    custom : typing.Dict[str, str] = Column(JSON, nullable=False, default={})
    
class Trophy(base):
    __tablename__ = 'trophy'
    name : str = Column(String(35), primary_key=True)
    unique : bool = Column(Boolean, nullable=False, default=False)
    
    def __str__(self) -> str:
        return self.name
    
class TrophyRecord(base):
    __tablename__ = 'trophy_record'
    unique_string : str = Column(String(55), primary_key=True)
    discord_id : int = Column(Integer, nullable=False)
    # linked
    trophy_name : str = Column(String(35), ForeignKey("trophy.name"), nullable=False)
    fixate : bool = Column(Boolean, nullable=False, default=False)
    
    @classmethod
    def create(cls, discord_id: typing.Union[discord.User, int], trophy_name: typing.Union[Trophy, str], fixate : bool = False):
        discord_id = discord_id if isinstance(discord_id, int) else discord_id.id
        trophy_name = trophy_name if isinstance(trophy_name, str) else trophy_name.name
        unique_string = f"{discord_id}_{trophy_name}"
        
        return cls(
            unique_string=unique_string,
            discord_id=discord_id,
            trophy_name=trophy_name,
            fixate=fixate
        )
        
"""
class HoyoBaseImg(base):
    __tablename__ = 'base_img'
    __bind_key__ = 'hoyovalk'
    id : int = Column(Integer, primary_key=True)
    img : bytes = Column(LargeBinary, nullable=False)

class HoyoCombinedImg(base):
    __tablename__ = 'combined_img'
    __bind_key__ = 'hoyovalk'
    id : str = Column(String(55), primary_key=True)
    img : bytes = Column(LargeBinary, nullable=False)
    
    @classmethod
    def combine(cls, img1, img2, img3, img4):
        pass
"""