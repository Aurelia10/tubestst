from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import urllib

# SQLAlchemy specific code, as with any other app
# DATABASE_URL = "sqlite:///./test.db"

#host_server = os.environ.get('host_server', 'localhost')
#db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
#database_name = os.environ.get('database_name', 'fastapi')
#db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
#db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'secret')))
#ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
host_server = 'tubes-tst.postgres.database.azure.com'
db_server_port = '5432'
database_name = 'Member'
db_username = 'aureliatt@tubes-tst'
db_password = 'Sadajiwa000'
ssl_mode = 'prefer'
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username,db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

member = sqlalchemy.Table(
    "member",
    metadata,
    sqlalchemy.Column("username", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("nama", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("alamat", sqlalchemy.String),
    sqlalchemy.Column("no_telp", sqlalchemy.String),
    sqlalchemy.Column("total_poin", sqlalchemy.Integer),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, pool_size=3, max_overflow=0
)
metadata.create_all(engine)

class MemberIn(BaseModel):
    username : str
    nama : str
    password : str
    alamat : str
    no_telp : str

class Member(BaseModel):
    username : str
    nama : str
    alamat : str
    no_telp : str
    #total_poin : Optional[int]

app = FastAPI(title = "Tubes TST")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()