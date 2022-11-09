import typing
import discord
from discord.ext import commands

class staticInteract:
    @staticmethod
    async def get_guild(guild : typing.Union[discord.Guild, int, str], bot : commands.Bot = None, force : bool = False):
        if isinstance(guild, discord.Guild):
            return guild
        
        if bot is None:
            return None 
        
        guild = int(guild)    
        
        guildObj = bot.get_guild(guild)
        if guildObj is None and force:
            guildObj = await bot.fetch_guild(guild)
            
        return guildObj
    
    @staticmethod
    async def get_role(role : typing.Union[discord.Role, int, str], guild : typing.Union[discord.Guild, int, str] = None, bot : commands.Bot = None, force : bool = False):
        if isinstance(role, discord.Role):
            return role
        
        if guild is None:
            return None
        
        role = int(role)    
        
        guild = await staticInteract.get_guild(guild, bot, force)
        if guild is None:
            return None
        
        roleObj = guild.get_role(role)
        if roleObj is None and force:
            roleObj = guild.get_role(role)

        return roleObj
    
    @staticmethod
    async def get_channel(
        channel : typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, int, str], 
        bot : commands.Bot = None, 
        force : bool = False
    ):
        if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
            return channel
        
        if bot is None:
            return None
        
        channel = int(channel)    
        
        channelObj = bot.get_channel(channel)
        if channelObj is None and force:
            channelObj = await bot.fetch_channel(channel)
            
        return channelObj
    
    @staticmethod
    async def get_user(
        user : typing.Union[discord.User, int, str], 
        bot : commands.Bot = None, 
        force : bool = False
    ):
        if isinstance(user, discord.User):
            return user
        
        if bot is None:
            return None
        
        user = int(user)    
        
        userObj = bot.get_user(user)
        if userObj is None and force:
            userObj = await bot.fetch_user(user)
            
        return userObj
    
    @staticmethod
    def has_permission(interact : discord.Interaction, bot : commands.Bot = None, **kwargs) -> bool:
        """
        check if the user has permission in guild
        """
        return all(getattr(interact.user.guild_permissions, name, None) == value for name, value in kwargs.items())

    @staticmethod
    def has_any_permission(interact : discord.Interaction, bot : commands.Bot = None, **kwargs) -> bool:
        """
        check if the user has any permission in guild
        """
        return any(getattr(interact.user.guild_permissions, name, None) == value for name, value in kwargs.items())
    
    @staticmethod
    def has_role(interact : discord.Interaction, bot : commands.Bot = None, *query_roles : typing.Union[discord.Role, int, str]) -> bool:
        """
        check if the user has any role in guild
        """
        uids = [role.id for role in interact.user.roles]
        
        for role in interact.user.roles:
            if isinstance(role, discord.Role) and role not in query_roles:
                return False
            if isinstance(role, int) and role not in uids:
                return False
            if isinstance(role, str) and int(role) not in uids:
                return False
        
        return True
    
    @staticmethod
    def has_any_role(interact : discord.Interaction, bot : commands.Bot = None, *query_roles : typing.Union[discord.Role, int, str]) -> bool:
        """
        check if the user has any role in guild
        """
        uids = [role.id for role in interact.user.roles]
        
        for role in interact.user.roles:
            if isinstance(role, discord.Role) and role in query_roles:
                return True
            if isinstance(role, int) and role in uids:
                return True
            if isinstance(role, str) and int(role) in uids:
                return True
        
        return False
    
    @staticmethod
    async def user_has_any_role(
        user : typing.Union[discord.User, int, str], 
        bot : commands.Bot = None, 
        *query_roles : typing.Union[discord.Role, int, str]
    ) -> bool:
        """
        check if the user has any role in guild
        """
        user = await staticInteract.get_user(user, bot, force=True)
        
        uids = [role.id for role in user.roles]
        
        for role in user.roles:
            if isinstance(role, discord.Role) and role in query_roles:
                return True
            if isinstance(role, int) and role in uids:
                return True
            if isinstance(role, str) and int(role) in uids:
                return True
        
        return False
        
    @staticmethod
    async def user_has_role(
        user : typing.Union[discord.User, int, str],
        bot : commands.Bot = None,
        *query_roles : typing.Union[discord.Role, int, str]
    ) -> bool:
        """
        check if the user has any role in guild
        """
        user = await staticInteract.get_user(user, bot, force=True)
        
        uids = [role.id for role in user.roles]
        
        for role in user.roles:
            if isinstance(role, discord.Role) and role not in query_roles:
                return False
            if isinstance(role, int) and role not in uids:
                return False
            if isinstance(role, str) and int(role) not in uids:
                return False
        
        return True
    
    @staticmethod
    async def user_has_any_permission(
        user : typing.Union[discord.User, int, str],
        bot : commands.Bot = None,
        **kwargs
    ) -> bool:
        """
        check if the user has any permission in guild
        """
        user = await staticInteract.get_user(user, bot, force=True)
        
        return any(getattr(user.guild_permissions, name, None) == value for name, value in kwargs.items())
    
    @staticmethod
    async def user_has_permission(
        user : typing.Union[discord.User, int, str],
        bot : commands.Bot = None,
        **kwargs
    ) -> bool:
        """
        check if the user has permission in guild
        """
        user = await staticInteract.get_user(user, bot, force=True)
        
        return all(getattr(user.guild_permissions, name, None) == value for name, value in kwargs.items())
    
class Interact:
    def __init__(self, interact: discord.Interaction) -> None:
        self.interact = interact
        
    def get_guild(self, bot : commands.Bot = None, force : bool = False):
        return staticInteract.get_guild(self.interact.guild_id, bot, force)
    
    def get_channel(self, bot : commands.Bot = None, force : bool = False):
        return staticInteract.get_channel(self.interact.channel_id, bot, force)
    
    def get_user(self, bot : commands.Bot = None, force : bool = False):
        return staticInteract.get_user(self.interact.user, bot, force)
    
    def has_permission(self, bot : commands.Bot = None, **kwargs) -> bool:
        return staticInteract.has_permission(self.interact, bot, **kwargs)
    
    def has_any_permission(self, bot : commands.Bot = None, **kwargs) -> bool:
        return staticInteract.has_any_permission(self.interact, bot, **kwargs)
    
    def has_role(self, bot : commands.Bot = None, *query_roles : typing.Union[discord.Role, int, str]) -> bool:
        return staticInteract.has_role(self.interact, bot, *query_roles)
    
    def has_any_role(self, bot : commands.Bot = None, *query_roles : typing.Union[discord.Role, int, str]) -> bool:
        return staticInteract.has_any_role(self.interact, bot, *query_roles)
    
    async def user_has_any_role(self, bot : commands.Bot = None, *query_roles : typing.Union[discord.Role, int, str]) -> bool:
        return await staticInteract.user_has_any_role(self.interact.user, bot, *query_roles)
    
    async def user_has_role(self, bot : commands.Bot = None, *query_roles : typing.Union[discord.Role, int, str]) -> bool:
        return await staticInteract.user_has_role(self.interact.user, bot, *query_roles)
    
    async def user_has_any_permission(self, bot : commands.Bot = None, **kwargs) -> bool:
        return await staticInteract.user_has_any_permission(self.interact.user, bot, **kwargs)
    
    async def user_has_permission(self, bot : commands.Bot = None, **kwargs) -> bool:
        return await staticInteract.user_has_permission(self.interact.user, bot, **kwargs)
    
        
    

    