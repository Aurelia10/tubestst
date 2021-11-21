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

host_server = os.environ.get('host_server', 'tubes-tst.postgres.database.azure.com')
db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'Sadajiwa')
db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'aureliatt@tubes-tst')))
db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'Sadajiwa000')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username,db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

member = sqlalchemy.Table(
    "member",
    metadata,
    sqlalchemy.Column("id_produk"    , sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("nama_produk"  , sqlalchemy.String),
    sqlalchemy.Column("deskripsi"    , sqlalchemy.String),
    sqlalchemy.Column("stok_produk"  , sqlalchemy.Integer),
    sqlalchemy.Column("harga_produk" , sqlalchemy.Integer),
    sqlalchemy.Column("promosi"      , sqlalchemy.Float),
)

produk = sqlalchemy.Table(
    "produk",
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

fake_users_db = {
    "asdf": {
        "username": "asdf",
        "nama": "aurel",
        "password": "000",
        "hashed_password": "$2b$12$OS5wetnUfg3Lzek.rGNG6.CHjmK5uILdLnrjZZt53WaYvm7zW2I8u",
        "disabled": False,
    }
}
class Token(BaseModel):
    access_token: str
    token_type: str

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
    total_poin : int 

class Produk(BaseModel):
    id_produk       : str
    nama_produk     : str
    deskripsi       : str
    stok_produk     : int
    harga_produk    : int
    promosi         : float


app = FastAPI(title = "API Deployment Sadajiwa")
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

@app.get("/login/", status_code = status.HTTP_200_OK)
async def read_login(skip: int = 0, take: int = 20):
    query = sqlalchemy.select(member).offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/allproduct/", status_code = status.HTTP_200_OK)
async def read_allproduk(skip: int = 0, take: int = 20):
    query = sqlalchemy.select(produk).offset(skip).limit(take)
    return await database.fetch_all(query)
