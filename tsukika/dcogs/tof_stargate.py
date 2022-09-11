from datetime import datetime
from types import MappingProxyType
import typing
import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext import tasks
from higanhanaSdk.dc.cog import CogExtension
from higanhanaSdk.dc.embed import Embedx
from tsukika.db import DbProfile, db
from discord.raw_models import RawReactionActionEvent
from pydantic import BaseModel, Field
from tsukika import tsukikaConfig

MATERIALS = typing.Literal["Booster Frame", "Nano Coating", "Nanofiber Frame", "Acidproof Glaze"]

class StargateEntry(BaseModel):
    discord_id : int
    rarity : int
    material : MATERIALS
    participants : typing.List[discord.Member]
    last_recorded : typing.Optional[datetime] = Field(default=None)
    
    class Config:
        arbitrary_types_allowed = True

booster_frame_1 = "https://static.wikia.nocookie.net/toweroffantasy/images/3/3d/Icon_Item_Booster_Frame_I.png/revision/latest/scale-to-width-down/80?cb=20220819160142"
booster_frame_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/6/6e/Icon_Item_Booster_Frame_II.png/revision/latest/scale-to-width-down/80?cb=20220819160143"
nano_coating_1 =  "https://static.wikia.nocookie.net/toweroffantasy/images/7/79/Icon_Item_Nano_Coating_I.png/revision/latest/scale-to-width-down/80?cb=20220819160147"
nano_coating_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/c/cc/Icon_Item_Nano_Coating_II.png/revision/latest/scale-to-width-down/80?cb=20220819160149"
nanofiber_1 ="https://static.wikia.nocookie.net/toweroffantasy/images/5/56/Icon_Item_Nanofiber_Frame_I.png/revision/latest/scale-to-width-down/80?cb=20220819160153"
nanofiber_2 ="https://static.wikia.nocookie.net/toweroffantasy/images/8/8d/Icon_Item_Nanofiber_Frame_II.png/revision/latest/scale-to-width-down/80?cb=20220819160155"
acidproof_1 = "https://static.wikia.nocookie.net/toweroffantasy/images/b/b0/Icon_Item_Acidproof_Glaze_I.png/revision/latest/scale-to-width-down/80?cb=20220819160136"
acidproof_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/8/83/Icon_Item_Acidproof_Glaze_II.png/revision/latest/scale-to-width-down/80?cb=20220819160138"


class ToFStargateCog(commands.GroupCog, CogExtension, group_name="tof-stargate", description="ToF Stargate commands"):
    def __init__(self, bot):
        self.bot : discord.Client = bot
        self.stargate_entries = {}
        self._current_date = datetime.utcnow().date()
        self.check_stargate_entries.start()
        
    @tasks.loop(hours=1)
    async def check_stargate_entries(self):
        if datetime.utcnow().date() != self._current_date:
            self._current_date = datetime.utcnow().date()
            self.stargate_entries = {}
            try:
                ch = self.bot.fetch_channel(1016656415147954237)
                await ch.send("Stargate entries have been reset.")
            except:
                pass
    
        self.expire_stargate_entry()
    
    def expire_stargate_entry(self):
        if len(self.stargate_entries) == 0:
            return
        
        # pop list 
        pop_list = []
        for msg, entry in self.stargate_entries.items():
            if entry.last_recorded is None:
                continue
            if datetime.utcnow() - entry.last_recorded > datetime.timedelta(minutes=60):
                pop_list.append(msg)
                
        for msg in pop_list:
            self.stargate_entries.pop(msg)
        
    @app_commands.command(
        name="add",
        description="Add a stargate entry"
    )
    async def tof_stargate_add(
        self, 
        ctx : Interaction, 
        rarity : typing.Literal[2,3], 
        material : MATERIALS
    ):
        """
        this command adds a stargate entry
        NOTE: this command requires the user to have a profile and tof id in the database

        Args:
            ctx (Interaction): _description_
            rarity (typing.Literal[2,3]): _description_
            material (MATERIALS): _description_
        """
        
        # if more than 5 counts of the same user, return
        if len([x for x in self.stargate_entries.values() if x.discord_id == ctx.user.id]) >= 5:
            return await self.x_send_as_embed(ctx, "You have already added 5 entries.")

        """# if not registered tof uid, return
        profile = DbProfile.query.filter_by(discord_id=ctx.user.id).first()
        if not profile or profile.tower_of_fantasy_uid is None:
            return await self.x_send_as_embed(ctx, "You have not registered your ToF UID.")"""
        
        embed = Embedx(
            title=f"{'⭐'* rarity} {material}",
            description=f"partcipants:\n{ctx.user.mention}",
            color=0x00ff00
        )
        self.embed_add_material_img(embed, material, rarity)
        
        msg = await ctx.channel.send(embed=embed)
        
        await msg.add_reaction("🆗")
        await msg.add_reaction("⛔")
        
        await ctx.response.send_message(f"Opened {material} {rarity}*", ephemeral=True)
        
        self.stargate_entries[msg] = StargateEntry(
            discord_id=ctx.user.id,
            rarity=rarity,
            material=material,
            participants=[ctx.user]
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : RawReactionActionEvent):
        if payload.event_type != "REACTION_ADD":
            return

        if payload.emoji.name != "🆗" and payload.emoji.name != "⛔":
            return
    
        if payload.channel_id not in tsukikaConfig.STARGATE_CHANNELS:
            return
    
        found = False

        for msg, entry in self.stargate_entries.items():
            if payload.message_id == msg.id:
                found = True
                break
            
        if not found:
            return
         
        msg : discord.Message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        entry : StargateEntry
        
        if payload.emoji.name == "⛔":
            if payload.member.id == entry.participants[0].id:
                embed = msg.embeds[0]
                embed.title += " (closed)"
                embed.color = 0xff0000
                
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                self.stargate_entries.pop(msg)
            return
        
        if payload.user_id in [u.id for u in entry.participants]:
            return
        
        
        profile = DbProfile.query.filter_by(discord_id=payload.user_id).first()
        if not profile:
            return
    
        user = await self.bot.fetch_user(payload.user_id)
        entry.participants.append(user)

        embed =Embedx(
            title=f"{'⭐'* entry.rarity} {entry.material}",
            description=f"partcipants:\n{' '.join([x.mention for x in entry.participants])}",
            color=0x00ff00
        )

        self.embed_add_material_img(embed, entry.material, entry.rarity)
        
        await msg.edit(
            embed=embed
        )
        
        if len(entry.participants) >= 4:
            entry.last_recorded = datetime.utcnow()
            return
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload : RawReactionActionEvent):
        if payload.event_type != "REACTION_REMOVE":
            return

        if payload.channel_id not in tsukikaConfig.STARGATE_CHANNELS:
            return
        
        found = False

        for msg, entry in self.stargate_entries.items():
            if payload.message_id == msg.id:
                found = True
                break
            
        if not found:
            return
        
        msg : discord.Message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        entry : StargateEntry 
        if payload.user_id not in [u.id for u in entry.participants]:
            return
        
        # add check that author cannot remove himself
        if payload.user_id == entry.participants[0].id:
            return
    
        user = await self.bot.fetch_user(payload.user_id)
        entry.participants.remove(user)

        embed =Embedx(
            title=f"{'⭐'* entry.rarity} {entry.material}",
            description=f"partcipants:\n{' '.join([x.mention for x in entry.participants])}",
            color=0x00ff00
        )
        self.embed_add_material_img(embed, entry.material, entry.rarity)
        
        await msg.edit(
            embed=embed
        )
        
    def embed_add_material_img(self, embed, material, rarity):
        if material == "Booster Frame":
            embed.set_thumbnail(url=booster_frame_2)
        elif material == "Nano Coating":
            embed.set_thumbnail(url=nano_coating_2)
        elif material == "Nanofiber Frame":
            embed.set_thumbnail(url=nanofiber_2)
        elif material == "Acidproof Glaze":        
            embed.set_thumbnail(url=acidproof_2)
            
    @app_commands.command(
        name="opened",
        description="returns a opened stargate entry",
    )
    async def opened(self, ctx : Interaction, material : MATERIALS = None, member : discord.Member = None):
        """
        returns a opened stargate entry
        """
        all_entries = {
            k : v for k, v in 
            sorted(
                self.stargate_entries.items(), 
                key=lambda x: x[1].rarity * 10 + len(x[1].participants), 
                reverse=True
            )
        }
        
        for msg, entry in all_entries.items():
            if material is not None and entry.material != material:
                continue
            if member is not None and member.id != entry.discord_id:
                continue
            if len(entry.participants) == 4:
                continue
            
            await ctx.response.send_message(f"Pulled {entry.material} {entry.rarity}*", ephemeral=True)
            
            newmsg = await ctx.channel.send(embed=msg.embeds[0])
            self.stargate_entries.pop(msg)
            self.stargate_entries[newmsg] = entry
            await newmsg.add_reaction("🆗")
            await newmsg.add_reaction("⛔")
        
            return
        
        await self.x_send_as_embed(
            ctx,
            "no entry found",
            title="warning",
            color=0xff0000
        )    
         
    
            
async def setup(bot):
    await bot.add_cog(ToFStargateCog(bot))