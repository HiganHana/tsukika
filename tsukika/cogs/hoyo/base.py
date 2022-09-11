import genshin
from tsukika import tsukikaConfig


hoyoClient = genshin.Client()
hoyoClient.set_cookies(
    {
        "ltuid" : tsukikaConfig["ltuid"],
        "ltoken" : tsukikaConfig["ltoken"],
    }
)

