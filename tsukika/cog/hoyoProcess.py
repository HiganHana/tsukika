import typing
import genshin
from tsukika.bot import mf
from fuzzywuzzy import process

class hoyoProcessor:
    def __init__(self) -> None:
        self.hoyo_client = genshin.Client({
            "ltuid": mf.config.hoyo_ltuid,
            "ltoken": mf.config.hoyo_ltoken,
        })
        
        self.close_matches = {}

    async def get_honkai_all_battlesuits(self, uid : int) -> typing.List[genshin.models.FullBattlesuit]:
        try:
            uid = int(uid)
            return await self.hoyo_client.get_honkai_battlesuits(uid), None
        except genshin.errors.GenshinException as e:
            return None, e.msg
    
    async def get_honkai_character(self, uid : int, character : typing.Union[int, str]) -> typing.Optional[genshin.models.FullBattlesuit]:
        try:
            uid=int(uid)
            battlesuits = await self.hoyo_client.get_honkai_battlesuits(uid)
        except genshin.errors.GenshinException as e:
            return None, e.msg
        
        for b in battlesuits:
            if isinstance(character, int) and b.id == character:
                return b, None
            elif isinstance(character, str) and b.name.lower() == character.lower().strip():    
                return b, None
            elif (
                isinstance(character, str) 
                and character.lower().strip() in self.close_matches
                and b.name.lower() == self.close_matches[character.lower().strip()].lower()
            ):
                return b, None
    
        # do fuzzy matching
        if not isinstance(character, int):
            return None, None
        
        characters_owned = [b.name for b in battlesuits]
        close_match = process.extractOne(character, characters_owned)
        self.close_matches[character] = close_match[0].name

        return close_match, None
    
HOYO_PROCESSOR = hoyoProcessor()

            

        
        
        
    