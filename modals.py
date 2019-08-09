from sqlalchemy import Column, String, Integer, Date, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, create_engine, exists
from sqlalchemy.orm import sessionmaker

# For first time setup, run this file!
# this will create a null user that will get referenced before a picker picks up the
# master label and after the master label gets created


metadata = MetaData()
Base = declarative_base()

SQLITE = 'sqlite'
Base = declarative_base()
engine = create_engine('sqlite:////Users\diazric\Downloads\sqlite-tools-win32-x86-3290000\sqlite-tools-win32-x86-3290000/batches.db', echo=False)
metadata = MetaData()



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
    date = Column(Date)
    time = Column(Float)


class Batch(Base):
    __tablename__ = "Batch"
    id = Column(Integer, autoincrement=False, primary_key=True)
    MasterBatch = Column(Integer, ForeignKey(MasterBatch.id))
    date = Column(Date)
    time = Column(Float)


class DropStation(Base):
    __tablename__ = "DropStation"
    id = Column(Integer, autoincrement=True, primary_key=True)
    pickerid = Column(Integer, ForeignKey(Picker.id))
    masterid = Column(Integer, ForeignKey(MasterBatch.id))
    date = Column(Date)
    time = Column(Float)
    station = Column(String)


class Dematic(Base):
    __tablename__ = "Dematic"
    id = Column(Integer, autoincrement=True, primary_key=True)
    work_id = Column(String) # BATCH
    suborder_id = Column(String) # Carton ID
    sales_id = Column(String) # Order Number
    route = Column(String)
    desc = Column(String)
    sku = Column(String)
    status = Column(String)
    user_id = Column(String)


db = SqlLitedb()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    session = db.get_session()
    null_user = Picker(id=0, name="Currently Picking")
    null_user_exists = session.query(exists().where(Picker.id==0)).scalar()
    if not null_user_exists:
        session.add(null_user)
        session.commit()
    session.close()
