import typing
from discord.ext import commands
from discord import app_commands
import discord
from higanhanaSdk.dc.embed import Embedx
from higanhanaSdk.frame import DcMainframe
from tsukika.models import Profile, Trophy, TrophyRecord
from tsukika.bot import mf
from sqlalchemy.orm.attributes import flag_modified

class cog_profile(commands.GroupCog, group_name="profile", group_description="profile commands"):
    def __init__(self, bot):
        self.bot = bot
        
    def get_or_create_profile(self, discord_id : typing.Union[int, str, discord.User]):
        """
        creates a new profile if user does not exist

        """
        # cast type
        if isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        
        discord_id = int(discord_id)
        
        # fetch
        profile = mf.db.session.query(Profile).filter_by(discord_id=discord_id).first()
        
        if profile is None:
            profile : Profile = Profile(discord_id=discord_id)
            mf.db.session.add(profile)
            mf.db.session.commit()
        
        return profile
    
    def get_profile(self, discord_id : typing.Union[int, str, discord.User]):
        """
        returns a profile if user exists

        """
        # cast type
        if isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        
        discord_id = int(discord_id)
        
        # fetch
        profile = mf.db.session.query(Profile).filter_by(discord_id=discord_id).first()
        
        return profile
    
    @app_commands.command(name="show", description="Show your profile")
    async def show(self, ctx : discord.Interaction, user : discord.User = None):
        if user is None:
            user = ctx.user
        
        profile = self.get_profile(user.id)

        
        embed = Embedx.Info(
            title=f"{user.name}'s Profile",
        )
        
        # get all trophies belonged to this user
        trophies = mf.db.session.query(TrophyRecord).filter_by(discord_id=user.id).all()
        
        # profile not exist and no trophy
        if profile is None and len(trophies) == 0:
            return await ctx.response.send_message(embed=embed)
        
        # has trophies
        if profile is None:
            profile = self.get_or_create_profile(user.id)
            
        # get profile configs
        if len(profile.fields) > 0:
            field_text = ""
            for k, v in profile.fields.items():
                field_text += f"{k}: `{v}`\n"
            
            embed.add_field(name="Fields", value=field_text, inline=False)

        if len(profile.custom) > 0:
            custom_text = ""
            for k, v in profile.custom.items():
                custom_text += f"{k}: `{v}`\n"
            
            embed.add_field(name="Custom", value=custom_text, inline=False)
        
        # get trophies
        if len(trophies) > 0:
            trophy_text = ""
            for trophy in trophies:
                trophy : TrophyRecord
                trophy_text += f"`{trophy.trophy_name}`,"
                
            trophy_text = trophy_text[:-1]
            
            embed.add_field(name="Trophies", value=trophy_text, inline=False)
    
        await ctx.response.send_message(embed=embed)

    @app_commands.command(name="set", description="Set your profile field")        
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def set_field(self, ctx : discord.Interaction, field : mf.config.PROFILE_FIELDS, value : str):
        profile = self.get_or_create_profile(ctx.user.id)
        
        profile.fields[field.value] = value
        
        #update
        flag_modified(profile, "fields")
        mf.db.session.merge(profile)
        mf.db.session.commit()
        
        await ctx.response.send_message(embed=Embedx.Success(
            title="Success",
            description=f"Set `{value}` to `{field.value}`",
        ))
        
    @app_commands.command(name="set_custom", description="Set your profile custom field")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def set_custom_field(self, ctx : discord.Interaction, field : str, value : str = None):
        profile = self.get_or_create_profile(ctx.user.id)
        
        limit = mf.config.get("PROFILE_CUSTOM_FIELD_LIMIT", 5)
        
        if len(profile.custom) >= limit:
            return await ctx.response.send_message(embed=Embedx.Error(
                title="Error",
                description=f"You have reached the custom field limit ({limit})",
            ))
        
        if value is None and field in profile.custom:
            # del
            del profile.custom[field]
            
        elif value is None:
            return await ctx.response.send_message(embed=Embedx.Error(
                title="Error",
                description=f"Field `{field}` does not exist",
            ))
        else:
            profile.custom[field] = value
        
        #update
        flag_modified(profile, "custom")
        mf.db.session.merge(profile)
        mf.db.session.commit()
        
        await ctx.response.send_message(embed=Embedx.Success(
            title="Success",
            description=f"Set `{field}` to `{value}`",
        ))
        
        
    @app_commands.command(name="trophy-add", description="Add a trophy to profile")
    @commands.cooldown(1, 3600*24, commands.BucketType.user)
    async def trophy_add(
        self, 
        ctx : discord.Interaction, 
        trophy_name : str, 
        is_unique : bool = False, 
        user: discord.User = None
    ):
        if user is None:
            user = ctx.user
        
        if len(ctx.user.roles) <= 3:
            return await ctx.response.send_message("invalid")
        
        # first query whether trophy exists
        trophy : Trophy = mf.db.session.query(Trophy).filter_by(name=trophy_name).first()
        if trophy is None:
            trophy = Trophy(name=trophy_name, unique=is_unique)
            mf.db.session.add(trophy)
            mf.db.session.commit()
        elif trophy.unique:
            # get a trophy record
            record : TrophyRecord = mf.db.session.query(TrophyRecord).filter_by(trophy_name=trophy_name).first()
            if record is not None:
                return await ctx.response.send_message("This trophy is unique and already exists")
        
        # create a trophy record
        record = TrophyRecord.create(user.id, trophy)
        mf.db.session.add(record)
        mf.db.session.commit()
        
        embed = Embedx.Info(
            title=f"{user.name}'s Profile",
            description=f"Added {trophy_name} to {user.name}'s profile"
        )
        
        await ctx.response.send_message(embed=embed)
        
        
async def setup(bot):
    await bot.add_cog(cog_profile(bot))