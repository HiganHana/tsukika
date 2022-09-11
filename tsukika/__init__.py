from tsukika.logger import logger

from higanhanaSdk.config import Config as _config_
import tsukika.config as _config

tsukikaConfig = _config_(_config)

import discord as _discord
from discord.ext import commands as _commands
from higanhanaSdk.dc.bot import load_extensions as _load_extensions
from tsukika import logger as _logger

class tsukikaBrain(_commands.Bot):
    async def on_ready(self):
        logger.info("Logged in as {0.user}".format(self))
            
    async def setup_hook(self) -> None:
        _load_extensions(self, "tsukika/dcogs", logger=logger)
        await self.tree.sync()

    @classmethod
    def create(cls):
        intents = _discord.Intents.default()
        intents.members = True
        intents.message_content = True
        client = tsukikaBrain(command_prefix="!",intents=intents)
        
        return client
