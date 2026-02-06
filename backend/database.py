from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

class Setting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str

class CommandHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    command: str
    timestamp: str
    status: str
    output: str

sqlite_file_name = "atlas.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
