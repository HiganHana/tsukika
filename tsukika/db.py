from enum import unique
from flask import Flask
import typing
from datetime import datetime


flask_app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../tsukika.db'
# other db  
flask_app.config['SQLALCHEMY_BINDS'] = {
    "honkai" : "sqlite:///../honkai.db",
}
#echo
flask_app.config['SQLALCHEMY_ECHO'] = False

flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(flask_app)

class DbProfile(db.Model):
    __tablename__ = 'profile'
    discord_id : int                                = db.Column(db.Integer, primary_key=True)
    on_init_nickname : str                          = db.Column(db.String(255), nullable=False)
    genshin_uid : typing.Optional[int]              = db.Column(db.Integer, nullable=True, unique=True)
    honkai_uid : typing.Optional[int]               = db.Column(db.Integer, nullable=True, unique=True)
    honkai_is_in_guild : typing.Optional[bool]      = db.Column(db.Boolean, nullable=True)
    honkai_intent_to_change : typing.Optional[bool] = db.Column(db.Boolean, nullable=True)
    tower_of_fantasy_uid : typing.Optional[int]     = db.Column(db.Integer, nullable=True, unique=True)
    currency : int                                  = db.Column(db.Integer, nullable=True, default=0)
    etc : dict                                      = db.Column(db.JSON, default={})
    
class DbTrophy(db.Model):
    __tablename__ = 'trophy'
    name : str                                = db.Column(db.String(255), primary_key=True)
    is_unique : bool                                = db.Column(db.Boolean, nullable=False)
    first_obtainer : int                            = db.Column(db.Integer, nullable=False)
    obtainers : typing.List[int]                    = db.Column(db.JSON, nullable=False, default=[])

# ANCHOR honkai dbs
class DbHonkaiProfile(db.Model):
    __bind_key__ = 'honkai'
    __tablename__ = 'honkai_profile'
    uid : int                                       = db.Column(db.Integer, primary_key=True)
    nickname : str                                  = db.Column(db.String(255), nullable=False)
    lv : int                                        = db.Column(db.Integer, nullable=False)
    icon : str                                      = db.Column(db.String(255), nullable=False)
    battlesuits : int                               = db.Column(db.Integer, nullable=False)
    sss_battlesuits : int                           = db.Column(db.Integer, nullable=False)
    last_fetched : datetime                         = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

db.create_all()