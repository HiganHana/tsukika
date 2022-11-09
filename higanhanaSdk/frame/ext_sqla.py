
import os
import typing
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from higanhanaSdk.frame.config import DcMfConfig
from higanhanaSdk.frame.i import mfi
import typing

class MfSqlAlchemy(SQLAlchemy):
    @property
    def tables(self):
        return self.metadata.tables

class sqlaExtension(mfi):
    """
    extension for flask_sqlalchemy
    """
    
    _flask_app : Flask
    
    @mfi._parse_params
    def init_flask_sqlalchemy(self):
        """
        create models.py
        """
        os.makedirs("db", exist_ok=True)
        
        with open(os.path.join(self.project_name, "models.py"), "w") as f:
            
            
            
            f.write("""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
base = declarative_base()

class Example(base):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True)
    name = Column(String)
        
""")
    
    @mfi._parse_params
    @mfi._save_flag
    def setup_flask_sqlalchemy(
        self,
        _declarative_base,
        sql_db_path : str,
        sql_sub_db_paths : typing.Dict[str, str],
        sql_echo : bool = False,
    ):
        self._must_have_flag(self.setup_flask)
        
        sql_db_path = os.path.abspath(sql_db_path)
        
        self._flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sql_db_path}"
        self._flask_app.config["SQLALCHEMY_BINDS"] = {}
        self._flask_app.config["SQLALCHEMY_ECHO"] = sql_echo
        #SQLALCHEMY_TRACK_MODIFICATIONS 
        self._flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        for k, v in sql_sub_db_paths.items():
            self._flask_app.config["SQLALCHEMY_BINDS"][k] = f"sqlite:///{v}"
        
        self.db = MfSqlAlchemy(self._flask_app)
    
        self.db.Model = _declarative_base
    
        self.db.create_all()

        