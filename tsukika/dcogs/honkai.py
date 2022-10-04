import typing
from discord.ext import commands
from discord import ButtonStyle, app_commands, Interaction
import discord
from matplotlib.image import thumbnail
from tsukika.bot import mf
from higanhanaSdk.dc.embed import Embedx
from discord.utils import get
from discord.ui import View, Button, Select
from tsukika.cog.hoyoProcess import HOYO_PROCESSOR
from tsukika.models import Profile
from genshin.models import FullBattlesuit

matching_rairty = {
    "A" : 1, 
    "B" : 2, 
    "S" : 3, 
    "SS" : 4, 
    "SSS" : 5
}

reverse_matching_rairty = {v: k for k, v in matching_rairty.items()}

class honkai_characters_view(View):
    def __init__(self, author : discord.User, data : typing.List[FullBattlesuit]):
        super().__init__()
        # add page buttons 
        self.author = author
        self.current_page = 0
        self.data = data
        
    @classmethod
    def get_embed(cls, data : typing.List[FullBattlesuit], page : int):
        embed = Embedx.Info(
            title="Honkai Characters",
            description="Here are all the characters you have (page {}/{}).".format(page + 1, len(data) // 5 + 1)
        )
        
        # add all characters
        for i in range(page * 5, page * 5 + 5):
            if i >= len(data):
                break
            embed.add_field(
                name=f"{data[i].id} - {data[i].name}", 
                value=f"Rarity: {reverse_matching_rairty[data[i].rarity]}",
                inline=False
            )
        return embed
    
    def get_battlesuits_in_interest(self):
        bs = []
        for i in range(self.current_page * 5, self.current_page * 5 + 5):
            if i >= len(self.data):
                break
            bs.append(self.data[i])
        
        return bs
        
    async def interaction_check(self, interaction : Interaction):
        # check if user is the same
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You are not the same person!", ephemeral=True)
            return False
        return True
        
    @discord.ui.button(label='Previous', style=discord.ButtonStyle.green)
    async def previous(self, interaction : Interaction, button : discord.ui.Button):
        if self.current_page == 0:
            return await interaction.response.send_message("You are already on the first page!", ephemeral=True)
        self.current_page -= 1
        await interaction.response.edit_message(embed=self.get_embed(self.data, self.current_page))

    @discord.ui.button(label='Next', style=discord.ButtonStyle.green)
    async def next(self, interaction : Interaction, button : discord.ui.Button):
        if self.current_page == len(self.data) // 5:
            return await interaction.response.send_message("You are already on the last page!", ephemeral=True)
        self.current_page += 1
        await interaction.response.edit_message(embed=self.get_embed(self.data, self.current_page))        


class cog_honkai(commands.GroupCog, group_name="honkai", group_description="honkai guild commands"):
    @app_commands.command(name="hoyovalk", description="fetch genshin client profile")
    async def hoyovalk(self, ctx : Interaction, user: discord.User=None, query : str = None, create_rich_view : bool = False):
        if user is None:
            user : discord.User = ctx.user
        
        # check if has profile
        profile : Profile = mf.db.session.query(Profile).filter_by(discord_id=user.id).first()
        if profile is None or "Honkai ID" not in profile.fields:
            embed = Embedx.Error(
                "You do not have honkai profile recorded",
                "Please use `profile set` to register"
            )
        
        if query is None:
            battlesuits, successiful_run = await HOYO_PROCESSOR.get_honkai_all_battlesuits(profile.fields["Honkai ID"])
            if not successiful_run:
                embed = Embedx.Error(
                    "Failed to fetch data",
                    "Please try again later"
                )
                return await ctx.response.send_message(embed=embed)
            
            # send a view
            #battlesuits.sort(key=lambda x: matching_rairty[x.rarity], reverse=True)
            
            embed = honkai_characters_view.get_embed(battlesuits, 0)
            
            view = honkai_characters_view(user, battlesuits)
            return await ctx.response.send_message(embed=embed, view=view)
        
        if query.isdigit():
            query = int(query)
        
        # fetch hoyo profile
        battlesuit, successiful_run = await HOYO_PROCESSOR.get_honkai_character(profile.fields["Honkai ID"], query)
        if not successiful_run:
            embed = Embedx.Error(
                "Failed to fetch data",
                "Please try again later"
            )
            return await ctx.response.send_message(embed=embed)
        
        if battlesuit is None:
            embed = Embedx.Error(
                "Character not found",
                "I am sorry, current searching is very limited. Please either make sure you have the correct ID or name."
            )
            return await ctx.response.send_message(embed=embed)
        
        embed : discord.Embed = Embedx.Info(
            title=f"{battlesuit.name} - {reverse_matching_rairty[battlesuit.rarity]}",
            description=f"Battlesuit build for {user.name}",
        )

        embed.set_thumbnail(url=battlesuit.icon)

        #weapon
        embed.add_field(
            name="Weapon",
            value=f"{battlesuit.weapon.name} - {battlesuit.weapon.rarity}/{battlesuit.weapon.max_rarity}",
            inline = False
        )

        # stigs
        stig_text = ""
        if battlesuit.stigmata is not None:
            for stig in battlesuit.stigmata:
                if stig is None:
                    stig_text += "None\n"
                
                stig_text += f"{stig.name}\n"
        

        embed.add_field(
            name="Stigmas",
            value=stig_text,
            inline=False
        )
        
        return await ctx.response.send_message(embed=embed)
        
        
async def setup(bot):
    await bot.add_cog(cog_honkai(bot))