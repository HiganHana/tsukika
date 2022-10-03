    #
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

from tsukika.models import Profile

engine = create_engine("sqlite:///bkup.db")

base = declarative_base(engine)

class oldprofile(base):
    __tablename__ = "profile"
    
    discord_id = Column(Integer, primary_key=True)
    genshin_uid = Column(Integer)
    honkai_uid = Column(Integer)
    tower_of_fantasy_uid = Column(Integer)
    
# get all profiles
session = sessionmaker(bind=engine)()
profiles = session.query(oldprofile).all()

new_profiles = []

for profile in profiles:
    profile : oldprofile
    new_profile = Profile(
        discord_id=profile.discord_id,
        fields= {}
    )
    
    if profile.genshin_uid:
        new_profile.fields["Genshin ID"] = profile.genshin_uid
    if profile.honkai_uid:
        new_profile.fields["Honkai ID"] = profile.honkai_uid
    if profile.tower_of_fantasy_uid:
        new_profile.fields["ToF ID"] = profile.tower_of_fantasy_uid

    new_profiles.append(new_profile)
    

mf.db.session.add_all(new_profiles)
mf.db.session.commit()
