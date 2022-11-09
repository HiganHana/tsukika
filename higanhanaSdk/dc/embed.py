import typing
from discord.embeds import Embed

class Embedx(Embed):
    def Color(self, color : str):
        self.color = color
        return self
    
    @typing.overload
    def __iadd__(self, other : Embed):pass
    
    def __iadd__(self, other):
        instance_type = type(other)
        if instance_type is Embed:
            other : Embed
            # just call this
            self.fields
            # and this
            self._fields += other.fields
        else:
            raise TypeError(f"unsupported operand type(s) for +=: '{type(self).__name__}' and '{instance_type.__name__}'")

    # ANCHOR color codes
    @classmethod
    def Info(cls, title : str= "Info", description : str= None, color : int= 0x00ff00):
        return cls(title=title, description=description, color=color)
        
    @classmethod
    def Error(cls, title : str= "Error", description : str= None, color : int= 0xff0000):
        return cls(title=title, description=description, color=color)
    
    @classmethod
    def Warning(cls, title : str= "Warning", description : str= None, color : int= 0xffff00):
        return cls(title=title, description=description, color=color)
    
    @classmethod
    def Success(cls, title : str= "Success", description : str= None, color : int= 0x00ff00):
        return cls(title=title, description=description, color=color)
    
    @classmethod
    def Critical(cls, title : str= "Critical", description : str= None, color : int= 0xff0000):
        return cls(title=title, description=description, color=color)

    @classmethod
    def QuickTest(cls, title : str= "QuickTest", description : str= "This is a test", color : int= 0x00ff00):
        return cls(title=title, description=description, color=color)
    