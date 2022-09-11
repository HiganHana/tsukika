"""
tsukika profile cog
"""

import typing
import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext import tasks
from higanhanaSdk.dc.cog import CogExtension
from higanhanaSdk.dc.embed import Embedx
from higanhanaSdk.models.profile import UserDisplayOptions, UserSetOptions
from tsukika.db import DbProfile, db, DbTrophy
from tsukika import tsukikaConfig

already_registered_embed = Embedx.Error(description="You have already registered.")
user_not_registered_embed = Embedx.Error(description="User not registered yet.")

class profileCog(commands.GroupCog, CogExtension, group_name="profile", description="Profile related commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(
        name="register",
        description="Register your profile"
    )
    async def profile_add(self, ctx : Interaction, user : typing.Optional[discord.User] = None):
        if user is None:
            user = ctx.user
        if DbProfile.query.filter_by(discord_id=user.id).first() is not None:
            return await self.x_send_embed(ctx, already_registered_embed)
        
        profile = DbProfile(
            discord_id=user.id,
            on_init_nickname=user.display_name
        )
        db.session.add(profile)
        db.session.commit()
        
        await self.x_send_as_embed(
            ctx,
            title="Success",
            description="You have successfully registered!"
        )
        
    @app_commands.command(
        name="get",
        description="Get a field from profile"
    )
    async def profile_get(self, ctx : Interaction, field : UserDisplayOptions, user : typing.Optional[discord.User] = None):
        if user is None:
            user = ctx.user
        
        profile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None:
            return await self.x_send_embed(ctx, user_not_registered_embed)

        if (val := getattr(profile, field.value)) is None:
            return await self.x_send_as_embed(
                ctx,
                title="Error",
                description="Field is empty!",
                color=0xff0000
            )

        await self.x_send_as_embed(
            ctx,
            title=f"{field.name} for {user.display_name}",
            description=f"{val}"
        )    
        
    @app_commands.command(
        name="set-field",
        description="Update a field from profile"
    )
    async def profile_update_field(self, ctx : Interaction, field : UserSetOptions, value : str):
        profile = DbProfile.query.filter_by(discord_id=ctx.user.id).first()
        if profile is None:
            return await self.x_send_embed(ctx, user_not_registered_embed)
        
        if not value.isnumeric():
            return await self.x_send_as_embed(
                ctx,
                title="Error",
                description="Value must be numeric!",
                color=0xff0000
            )
        
        
        if getattr(profile, field.value) is not None and not self.x_has_any_role(ctx, *tsukikaConfig.MOD_ROLES):
            return await self.x_send_as_embed(
                ctx,
                title="Error",
                description="You cannot edit your field, contact a mod pls",
                color=0xff0000
            )
            
        setattr(profile, field.value, value)
        db.session.commit()
        
        await self.x_send_as_embed(
            ctx,
            title="Success",
            description=f"Updated `{field.value}` to `{value}`"
        )

    @app_commands.command(
        name="reset-field",
        description="Reset a field from profile"
    )
    @commands.has_any_role(*tsukikaConfig.MOD_ROLES)
    async def profile_reset_field(self, ctx : Interaction, field : UserSetOptions, user: discord.User):
        profile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None:
            return await self.x_send_embed(ctx, user_not_registered_embed)
        
        if getattr(profile, field.value) is None:
            return await self.x_send_as_embed(
                ctx,
                title="Error",
                description="Field is already empty!",
                color=0xff0000
            )
        
        
        setattr(profile, field.value, None)
        db.session.commit()
        
        await self.x_send_as_embed(
            ctx,
            title="Success",
            description=f"Reset `{field.value}` for {user.display_name}"
        )
        
    # ANCHOR trophy
    @app_commands.command(
        name="add-trophy",
        description="Add a trophy to profile"
    )
    @commands.has_any_role(*tsukikaConfig.MOD_ROLES)
    async def profile_add_trophy(self, ctx : Interaction, user: discord.User, trophy : str, unique : bool = True):
        discord_id = user.id
        # check if trophy exists
        trophy_obj : DbTrophy = DbTrophy.query.filter_by(name=trophy).first()
        
        # if not then freely creates it
        if trophy_obj is None:
            trophy_obj = DbTrophy(name=trophy, is_unique=unique)
            trophy_obj.first_obtainer = discord_id
            db.session.add(trophy_obj)
            db.session.commit()
            return await self.x_send_as_embed(
                ctx,
                title="Success",
                description=f"Added `{trophy}` to {user.display_name}"
            )
        
        # if it exists, check if it is unique
        if trophy_obj.is_unique and trophy_obj.first_obtainer != discord_id:
            return await self.x_send_as_embed(
                ctx,
                title="Error",
                description="Trophy is unique and already obtained by someone else",
                color=0xff0000
            )
            
        # if it is not unique, check if user already has it
        if discord_id in trophy_obj.obtainers:
            return await self.x_send_as_embed(
                ctx,
                title="Error",
                description="User already has this trophy",
                color=0xff0000
            )
            
        # if it is not unique and user does not have it, add it
        new_trophy_obj = DbTrophy(
            name=trophy_obj.name,
            is_unique=trophy_obj.is_unique,
            first_obtainer=trophy_obj.first_obtainer,
            obtainers=trophy_obj.obtainers + [discord_id]
        )
        # merge
        db.session.merge(new_trophy_obj)
        db.session.commit()
        return await self.x_send_as_embed(
            ctx,
            title="Success",
            description=f"Added `{trophy}` to {user.display_name}"
        )
        
        
    @app_commands.command(
        name="display"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile_display(
        self, 
        ctx : Interaction, 
        user : typing.Optional[discord.User] = None, 
        show_all : bool = False
    ):
        if user is None:
            user = ctx.user
        
        profile : DbProfile = DbProfile.query.filter_by(discord_id=user.id).first()
        if profile is None:
            return await self.x_send_embed(ctx, user_not_registered_embed)
        
        # query all unique trophies limit 10
        trophies = DbTrophy.query.filter(DbTrophy.first_obtainer == user.id).limit(10).all()
        
        embed = discord.Embed(
            title=f"{user.display_name}'s profile",
            description=f"{' '.join(f'`{t.name}`' for t in trophies)}",
            color=0x00ff00
        )
    
        if show_all and self.x_has_any_role(ctx, *tsukikaConfig.MOD_ROLES):
            all_trophies = DbTrophy.query.all()
            non_unique_trophies = []
            for trophy in all_trophies:
                if user.id in trophy.obtainers:
                    non_unique_trophies.append(trophy)
    
            if non_unique_trophies:
                embed.add_field(
                    name="Non-unique trophies",
                    value=f"{' '.join(f'`{t.name}`' for t in non_unique_trophies)}"
                )
        
        if profile.genshin_uid:
            embed.add_field(name="Genshin UID", value=profile.genshin_uid)
        
        if profile.honkai_uid:
            embed.add_field(
                name="Honkai UID", 
                value=f"`{profile.honkai_uid}` {'Guildee' if profile.honkai_is_in_guild else ''}" 
            )
        
        await self.x_send_embed(ctx, embed)        
    

async def setup(bot):
    await bot.add_cog(profileCog(bot))