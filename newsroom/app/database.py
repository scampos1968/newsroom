from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event
import os

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./newsroom.db")
engine = create_engine(DB_PATH, echo=False)

@event.listens_for(engine, "connect")
def set_sqlite_encoding(dbapi_connection, connection_record):
    dbapi_connection.execute("PRAGMA encoding='UTF-8'")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
