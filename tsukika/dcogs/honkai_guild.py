import typing
import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext import tasks
from higanhanaSdk.dc.cog import CogExtension
from higanhanaSdk.dc.embed import Embedx
from higanhanaSdk.models.profile import UserDisplayOptions, UserSetOptions
from tsukika.db import DbProfile, db 
from tsukika import tsukikaConfig

class HonkaiGuildCog(
    commands.GroupCog, 
    CogExtension, 
    group_name = "honkai-guild",
    description = "Honkai Impact 3rd guild related commands"
):
    def __init__(self, bot):
        self.bot : discord.Client = bot
    
    @app_commands.command(
        name = "whois",
        description = "Get a user's Honkai Impact 3rd guild status"
    )
    async def whois(self, ctx : Interaction, user : typing.Optional[discord.User] = None):
        if user is None:
            user = ctx.user
        
        profile : DbProfile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None or profile.honkai_uid is None:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User not registered yet. (or honkai uid not set)"
            )
        
        status_string = f"{'🔴' if not profile.honkai_is_in_guild else '🟢'} in guild."
        wish_to_string = ""
        if profile.honkai_is_in_guild and profile.honkai_intent_to_change:
            wish_to_string = f"🟢 Intends to leave."
        elif not profile.honkai_is_in_guild and profile.honkai_intent_to_change:
            wish_to_string = f"🟢 Intends to join."
        
        
        return await self.x_send_as_embed(
            ctx,
            title = "Honkai Guild Status for " + user.display_name,            
            description = status_string + "\n" + wish_to_string
        )
        
    @app_commands.command(
        name= "apply",
        description = "Apply to join Honkai Impact 3rd guild"
    )
    async def apply(self, ctx : Interaction, user : typing.Optional[discord.User] = None):
        if user is None:
            user = ctx.user
        
        profile : DbProfile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None or profile.honkai_uid is None:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User not registered yet. (or honkai uid not set)"
            )
        
        if profile.honkai_is_in_guild:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User is already in guild."
            )
        
        profile.honkai_intent_to_change = True
        db.session.merge(profile)
        db.session.flush()
        db.session.commit()
        
        return await self.x_send_as_embed(
            ctx,
            title = "Success",
            description = f"{user.display_name} applied to join guild."
        )
        
    @app_commands.command(
        name = "leave",
        description = "Leave Honkai Impact 3rd guild"
    )
    async def leave(self, ctx : Interaction, user : typing.Optional[discord.User] = None):
        if user is None:
            user = ctx.user
        
        profile : DbProfile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None or profile.honkai_uid is None:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User not registered yet. (or honkai uid not set)"
            )
        
        if not profile.honkai_is_in_guild:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User is not in guild."
            )
        
        profile.honkai_intent_to_change = True

        db.session.merge(profile)
        db.session.flush()
        db.session.commit()
        
        return await self.x_send_as_embed(
            ctx,
            title = "Success",
            description = f"{user.display_name} applied to leave guild."
        )
    
    @app_commands.command(
        name="process",
        description = "Process guild application"
    )
    @commands.has_any_role(*tsukikaConfig.HONKAI_MODS)
    async def process(self, ctx : Interaction, user : discord.User, force_change : bool = False):
        profile : DbProfile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None or profile.honkai_uid is None:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User not registered yet. (or honkai uid not set)"
            )
            
        if not profile.honkai_intent_to_change and not force_change:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "User has no pending guild application."
            )        
            
        profile.honkai_is_in_guild = not profile.honkai_is_in_guild
        profile.honkai_intent_to_change = False

        db.session.merge(profile)
        db.session.flush()
        db.session.commit()
        
        return await self.x_send_as_embed(
            ctx,
            title = "Success",
            description = f"Processed guild application for {user.display_name}.\nin guild: {profile.honkai_is_in_guild}"
        )
        
    @app_commands.command(
        name= "list",
        description = "List guild members"
    )
    @commands.has_any_role(*tsukikaConfig.HONKAI_MODS)
    async def list(self, ctx : Interaction, option : typing.Literal["pending_to_join", "pending_to_leave"]):
        if option == "pending_to_join":
            profiles : typing.List[DbProfile] = DbProfile.query.filter_by(honkai_intent_to_change=True, honkai_is_in_guild=False).all()
        elif option == "pending_to_leave":
            profiles : typing.List[DbProfile] = DbProfile.query.filter_by(honkai_intent_to_change=True, honkai_is_in_guild=True).all()
        
        if len(profiles) == 0:
            return await self.x_send_as_embed(
                ctx,
                title = "Error",
                description = "No pending guild application."
            )
        
        description = ""
        
        for profile in profiles:
            user = self.bot.fetch_user(profile.discord_id)
            if user is None:
                continue
            description += f"{user.mention} ({profile.honkai_uid})\n"
        
        
        embed = discord.Embed(
            title = f"List - {option}",
            description = description
        )

        return await self.x_send_as_embed(
            ctx,
            embed = embed
        )

    
async def setup(bot):
    await bot.add_cog(HonkaiGuildCog(bot))