from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

metadata = MetaData()
Base = declarative_base()

SQLITE = 'sqlite'
Base = declarative_base()
engine = create_engine('sqlite:////sqlite3/batches.db', echo=True)
metadata = MetaData()
metadata.reflect(bind=engine)


class SqlLitedb:
    user = ''
    paswd = ''
    dialiect = 'sqlite'
    server = ''
    port = ''
    db = ''

    def __init__(self):
        self.metadata = metadata
        self.base = Base
        self.engine = engine

    def get_session(self):
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        session = Session()
        return session



class Picker(Base):
    __tablename__ = "Picker"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)


class MasterBatch(Base):
    __tablename__ = "MasterBatch"
    id = Column(Integer, autoincrement=False, primary_key=True)
    pickerid = Column(Integer, ForeignKey(Picker.id))


class Batch(Base):
    __tablename__ = "Batch"
    id = Column(Integer, autoincrement=False, primary_key=True)
    MasterBatch = Column(Integer, ForeignKey(MasterBatch.id))


class DropStation(Base):
    __tablename__ = "DropStation"
    id = Column(Integer, autoincrement=True, primary_key=True)
    picker = Column(String)
    pickerid = Column(Integer, ForeignKey(Picker.id))
    date = Column(Date)
    station = Column(String)
