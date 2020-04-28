#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import configparser
import os
from contextlib import contextmanager
import datetime
import copy

from sqlalchemy import create_engine, Column, Table, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary,JSON)
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.sql.functions import current_timestamp

class Singleton(type):
    instance = None
    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance

class PersitenceDatabase:
    def __init__(self,dbname:str):
        self.dbname = dbname
        self.conn = self.Connector(dbname)
        self.model = self.Model()
    
    class Connector(metaclass=Singleton):
        _CFG_PATH:str = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource/settings/db.cfg'))
        def __init__(self,db_name: str):
            if os.path.isfile(self._CFG_PATH) is False:
                raise FileNotFoundError("There is no database settings. allocate setting in " + self._CFG_PATH)
            cfg = configparser.ConfigParser(os.environ)
            cfg.read(self._CFG_PATH)
            self.conn_string_init = '{drivername}://{user}:{password}@{host}:{port}'.format(
                drivername = 'mysql+pymysql',
                user = cfg["persistance_db_" + db_name]["db_user"],
                password = cfg["persistance_db_" + db_name]["db_password"],
                host = cfg["persistance_db"]["db_host"],
                port = cfg["persistance_db"]["db_port"]
            )
            self.conn_string = '{drivername}://{user}:{password}@{host}:{port}/{db_name}?charset=UTF8MB4'.format(
                drivername = 'mysql+pymysql',
                user = cfg["persistance_db_" + db_name]["db_user"],
                password = cfg["persistance_db_" + db_name]["db_password"],
                host = cfg["persistance_db"]["db_host"],
                port = cfg["persistance_db"]["db_port"],
                db_name = cfg["persistance_db_" + db_name]["db_database"]
                )
            
            self.__engines = create_engine(self.conn_string),create_engine(self.conn_string_init, echo=True)

        def get_engines(self):
          return self.__engines
        
        @contextmanager
        def session(self):
            session = Session(self.__engines[0])
            try:
                yield session
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

    def create_database(self):
      schema = 'CREATE DATABASE IF NOT EXISTS {dbname} DEFAULT CHARACTER SET UTF8MB4;'.format(dbname=self.dbname)
      self.conn.get_engines()[1].connect().execute(schema)
      
    def create_table(self):
      self.model.base.metadata.create_all(bind=self.conn.get_engines()[0])

    def fetch_all(self,model,*columns: str):
        with self.conn.session() as ss:
          if len(columns) == 0:
            result = [row.toDict() for row in ss.query(model).all()]
          else:
            result = []
            for row in ss.query(*[getattr(model,column) for column in columns]).all():
              temp = {}
              for i,v in enumerate(row):
                temp[columns[i]] = v
              result.append(temp)

          # result = copy.deepcopy([a.toDict() for a in gen])

        return result

    class Model:
      class Base:
        def toDict(self):
          model = {}
          for column in self.__table__.columns:
              model[column.name] = str(getattr(self, column.name))
          return model

      base = declarative_base(cls=Base)
      # base.query = session.query_property()
    
      def __init__(self):
        pass

      class Users(base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)
        user_id = Column('user_id', String(255),nullable=False)
        status = Column(Integer,default=0,nullable=False)
        created_at = Column(DateTime, nullable=False, server_default=current_timestamp())
        updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')) 

        
          

