import logging
from typing import Callable
from higanhanaSdk.frame.config import DcMfConfig
from higanhanaSdk.frame.keys import DcMainframeCore
import discord
from discord.ext import commands
from higanhanaSdk.frame.i import mfi
import os

async def _load_extensions(bot : commands.Bot, config : DcMfConfig, project_name : str, default_discord_cogs : str):
    """
    loads bot extensions
    
    if `load_extensions` is False in config, process will be skipped
    
    if `disable_dcog_{extension name}` exist in config, that extension will be skipped
    """
    
    # into .
    path = os.path.join(project_name, default_discord_cogs)
    package_name = f"{project_name}.{default_discord_cogs}"
    
    logger = logging.getLogger(project_name)
    
    if getattr(config, "load_extensions", True) is False:
        logger.info("Skipping extension loading")
        return
    
    for cog in os.listdir(path):
        if cog.startswith("__") or not os.path.isfile(os.path.join(path, cog)):
            continue
        try:
            cog_no_extension = cog.split(".")[0]
            
            # check for disable
            if getattr(config, "disable_dcog_" + cog_no_extension, False):
                logger.info(f"Extension {cog_no_extension} is disabled.")
                continue    
            
            await bot.load_extension(f"{package_name}.{cog_no_extension}")
            logger.info(f"Loaded {cog}")
        except Exception as e:
            logger.error(f"Failed to load {cog} due to {e}")

class DcMfBot(commands.Bot):
    """
    a custom bot that supports dynamic offload of extension loading
    """
    def __init__(
        self,
        lambda_hook : Callable,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._lambda_hook = lambda_hook
    
    async def on_ready(self):
        print("Logged in as {0.user}".format(self))
        
            
    async def setup_hook(self) -> None:
        await self._lambda_hook(self)
        await self.tree.sync()

class BotExtension(mfi):
    """
    specifies bot setup
    """
    @mfi._parse_params
    def init_bot(self):
        os.makedirs(
            os.path.join(
                self.project_name, 
                self.config.default_discord_cogs
            ),
            exist_ok=True
        )
    

    @mfi._parse_params
    @mfi._save_flag
    def setup_bot(self,
        members_intent : bool,
        messages_intent : bool,
        command_prefix : str,
        default_discord_cogs : str,
        discord_token : str
    ):
        self.intents = discord.Intents.default()
        self.intents.members = members_intent
        self.intents.messages = messages_intent
        
        project_name = self.project_name
        
        self.bot = DcMfBot(
            command_prefix=command_prefix, 
            intents=self.intents,
            lambda_hook=lambda bot : _load_extensions(bot, self.config, project_name, default_discord_cogs)
        )
        
        return lambda : self.bot.run(discord_token)