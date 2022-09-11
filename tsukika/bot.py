import discord
from discord.ext import commands
from tsukika import logger
import os

class tsukikaBrain(commands.Bot):
    async def on_ready(self):
        logger.info("Logged in as {0.user}".format(self))
            
    async def setup_hook(self) -> None:
        for cog in os.listdir("tsukika/dcogs"):
            if cog.startswith("__") or not os.path.isfile(os.path.join("tsukika/dcogs", cog)):
                continue
            try:
                await self.load_extension(f"tsukika.dcogs.{cog[:-3]}")
                logger.info(f"Loaded {cog}")
            except Exception as e:
                logger.error(f"Failed to load {cog} due to {e}")
        await self.tree.sync()

    @classmethod
    def create(cls):
            
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        client = tsukikaBrain(command_prefix="!",intents=intents)
        
        return client
