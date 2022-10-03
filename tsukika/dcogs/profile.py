import typing
from discord.ext import commands
from discord import app_commands
import discord
from higanhanaSdk.dc.embed import Embedx
from higanhanaSdk.frame import DcMainframe
from tsukika.models import Profile, Trophy, TrophyRecord
from tsukika.bot import mf

class cog_profile(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_or_create_profile(self, discord_id : typing.Union[int, str, discord.User]):
        """
        creates a new profile if user does not exist

        """
        if isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        
        discord_id = int(discord_id)
        
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
        if isinstance(discord_id, discord.User):
            discord_id = discord_id.id
        
        discord_id = int(discord_id)
        
        profile = mf.db.session.query(Profile).filter_by(discord_id=discord_id).first()
        
        return profile
    
    @app_commands.command(name="show", description="Show your profile")
    async def show(self, ctx : discord.Interaction, user : discord.User = None):
        if user is None:
            user = ctx.user
        
        profile = self.get_or_create_profile(user.id)
        
        embed = Embedx.Info(
            title=f"{user.name}'s Profile",
        )
        
        if profile is None:
            return await ctx.response.send_message(embed=embed)
        
    
        
        
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