from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
import math
import typing
import discord

@dataclass(frozen=True)
class Text:
    """
    a class represents a text and is primarily used for creating discord messages
    """
    text : str
    marker : str
    
    def __post_init__(self):
        object.__setattr__(self,"_cache", self.marker.format(marker=self.text))
    
    def __str__(self) -> str:
        return self._cache
    
    def __repr__(self) -> str:
        return self._cache
    
    @classmethod
    def bold(cls, text : typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "**{marker}**":
                return text
            text = str(text)
        return cls(text, "**{marker}**")
    
    @classmethod
    def italic(cls, text: typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "*{marker}*":
                return text
            text = str(text)
        
        return cls(text, "*{marker}*")
    
    @classmethod
    def underline(cls, text : typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "__{marker}__":
                return text
            text = str(text)
    
        return cls(text, "__{marker}__")
    
    @classmethod
    def strikethrough(cls, text : typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "~~{marker}~~":
                return text
            text = str(text)
        
        return cls(text, "~~{marker}~~")

    @classmethod
    def code(cls, text : typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "`{marker}`":
                return text
            text = str(text)
            
        return cls(text, "`{marker}`")
    
    @classmethod
    def codeblock(cls, text : typing.Union[str, 'Text'], lang : str = None) -> str:
        if not lang:
            lang = ""
        else:
            lang = f"{lang}\n"
            
        if isinstance(text, Text):
            if text.marker == "```" + lang + "{marker}```":
                return text
            text = str(text)
            
        return cls(text,"```" + lang + "{marker}```")
    
    @classmethod
    def time(cls, dt : typing.Union[datetime, str, int]) -> str:
        if isinstance(dt, datetime):
            dt = math.floor(dt.timestamp())
            
        return cls(f"{dt}", "<t:{marker}>")
    
    @classmethod
    def time_remaining(cls, dt : typing.Union[datetime, str, int]) -> str:
        if isinstance(dt, datetime):
            dt = math.floor(dt.timestamp())
            
        return cls(f"{dt}", "<t:{marker}:R>")
    
    @classmethod
    def role_mention(cls, role : typing.Union[discord.Role, int]) -> str:
        if isinstance(role, discord.Role):
            role = role.id
            
        return cls(f"{role}", "<@&{marker}}>")
    
    @classmethod
    def user_mention(cls, user : typing.Union[discord.User, int]) -> str:
        if isinstance(user, discord.User):
            user = user.id
            
        return cls(f"{user}","<@{marker}>")
    
    @classmethod
    def channel_mention(cls, channel : typing.Union[discord.TextChannel, int]) -> str:
        if isinstance(channel, discord.TextChannel):
            channel = channel.id
            
        return cls(f"{channel}", "<#{marker}>")
    
    @classmethod
    def secret(cls, text : typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "||{marker}||":
                return text
            text = str(text)
            
        return cls(text, "||{marker}||")
    
    @classmethod
    def quote(cls, text : typing.Union[str, 'Text']) -> str:
        if isinstance(text, Text):
            if text.marker == "> {marker}":
                return text
            text = str(text)
            
        return cls(text, "> {marker}")
    
    @classmethod
    def auto(cls, obj):
        if not obj:
            raise ValueError("Object cannot be None")
        
        if isinstance(obj, discord.Role):
            return cls.role_mention(obj)
        
        if isinstance(obj, datetime):
            return cls.time(obj)
        
        if isinstance(obj, discord.User):
            return cls.user_mention(obj)
        
        if isinstance(obj, discord.TextChannel):
            return cls.channel_mention(obj)
        
        raise ValueError("The object type is not supported with auto")
