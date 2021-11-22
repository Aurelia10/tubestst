from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import urllib
from typing import Optional

host_server = os.environ.get('host_server', 'tubes-tst.postgres.database.azure.com')
db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'Sadajiwa')
db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'aureliatt@tubes-tst')))
db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'Sadajiwa000')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username,db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

produk = sqlalchemy.Table(
    "produk",
    metadata,
    sqlalchemy.Column("id_produk"    , sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nama_produk"  , sqlalchemy.String),
    sqlalchemy.Column("deskripsi"    , sqlalchemy.String),
    sqlalchemy.Column("stok_produk"  , sqlalchemy.Integer),
    sqlalchemy.Column("harga_produk" , sqlalchemy.Integer),
    sqlalchemy.Column("promosi"      , sqlalchemy.Integer),
)

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

pesanan = sqlalchemy.Table(
    "pesanan",
    metadata,
    sqlalchemy.Column("id_pesanan", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("status_pembayaran", sqlalchemy.Boolean),
    sqlalchemy.Column("id_item", sqlalchemy.Integer),
    sqlalchemy.Column("total_harga", sqlalchemy.Integer),
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
    total_poin : Optional[int] = 0

class Produk(BaseModel):
    id_produk : int
    nama_produk : str
    deskripsi : str
    stok_produk : int
    harga_produk : int
    promosi : float

class PesananIn(BaseModel):
    id_pesanan : int
    status_pembayaran : bool
    id_item : int

class Pesanan(BaseModel):
    id_pesanan : int
    status_pembayaran : bool 
    id_item : int
    total_harga : Optional[int] = 0 

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
    query = member.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/allproduct/", status_code = status.HTTP_200_OK)
async def read_allproduk(skip: int = 0, take: int = 20):
    query = produk.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/pesanan/{pesanan_id}/", status_code = status.HTTP_200_OK)
async def read_pesanan(pesanan_id: int):
    query = pesanan.select().where(pesanan.c.id_pesanan == pesanan_id)
    return await database.fetch_one(query)

@app.post("/pesanan/", status_code = status.HTTP_201_CREATED)
async def create_pesanan(pesananin: PesananIn):
    query = pesanan.insert().values(
        id_pesanan=pesananin.id_pesanan, 
        status_pembayaran=pesananin.status_pembayaran,
        id_item=pesananin.id_item
    )
    await database.execute(query)
    #return {"status":"ok","data":pesanan}
    return {
        "id_pesanan" : pesananin.id_pesanan,
        "status_pembayaran" : pesananin.status_pembayaran,
        "id_item" : pesananin.id_item
    }

@app.put("/pesanan/{pesanan_id}/", status_code = status.HTTP_200_OK)
async def update_pesanan(pesanan_id: int, payload: PesananIn):
    query = pesanan.update().where(pesanan.c.id_pesanan == pesanan_id).values(id_pesanan=payload.id_pesanan, status_pembayaran=payload.status_pembayaran,id_item=payload.id_item)
    await database.execute(query)
    return {"status":"ok","data":payload}

@app.delete("/pesanan/{pesanan_id}/", status_code = status.HTTP_200_OK)
async def delete_pesanan(pesanan_id: int):
    query = pesanan.delete().where(pesanan.c.id_pesanan == pesanan_id)
    await database.execute(query)
    return {"message": "Pesanan dengan id: {} berhasil dihapus".format(pesanan_id)}