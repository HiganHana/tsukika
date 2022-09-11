from datetime import datetime, timedelta
from tsukika.cogs.hoyo.base import hoyoClient
import asyncio
from higanhanaSdk.models.honkaiProfile import HonkaiProfile
from tsukika.db import DbHonkaiProfile, db
from tsukika import logger

def get_honkai_profile(uid : int, expire : int = 24*60) -> HonkaiProfile:
    profile : DbHonkaiProfile = DbHonkaiProfile.query.filter_by(uid=uid).first()
    if profile is not None and datetime.utcnow() - profile.last_fetched < timedelta(minutes=expire):
        logger.info(f"Using cached honkai profile for {uid}")
        return HonkaiProfile(
            uid = profile.uid,
            nickname = profile.nickname,
            lv = profile.lv,
            icon = profile.icon,
            battlesuits = profile.battlesuits,
            sss_battlesuits = profile.sss_battlesuits
        )

    
    data = asyncio.run(hoyoClient.get_honkai_user(uid))
    
    # gather required data
    nickname = data.info.nickname
    lv = data.info.level
    icon = data.info.icon
    battlesuits = data.stats.battlesuits
    sss_battlesuits = data.stats.battlesuits_SSS
    
    profile = HonkaiProfile(
        uid = uid,
        
        icon = icon,
        lv = lv,
        battlesuits = battlesuits,
        sss_battlesuits = sss_battlesuits,
        nickname = nickname
    )
    
    db_profile = DbHonkaiProfile(
        uid = uid,
        icon = icon,
        lv = lv,
        battlesuits = battlesuits,
        sss_battlesuits = sss_battlesuits,
        nickname = nickname,
    )
    
    db.session.merge(db_profile)
    db.session.flush()
    db.session.commit()
    
    return profile

