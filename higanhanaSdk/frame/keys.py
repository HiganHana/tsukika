
from enum import Enum

class DcMainframeCore(Enum):
    """
    all config keys mandatory for mainframe constructor
    """
    enable_json_config : bool = True
    enable_mod_config : bool = True
    default_json_config_path : str = "config.json"
    default_mod_config_path : str = "config.py"
    
class DcMainframeKeys(Enum):
    """
    all config keys for mainframe
    """
    messages_intent : bool = True
    flask_host : str = "0.0.0.0"
    flask_port : int = 3000
    flask_debug : bool = False
    discord_token : str = None
    command_prefix : str = "!"
    members_intent : bool = True
    default_flask_cogs : str = "fcogs"
    default_discord_cogs : str = "dcogs"
    sql_db_path : str = "db/test.db"
    sql_sub_db_paths : dict = {}
    flask_blueprint_register_prefix : bool = True