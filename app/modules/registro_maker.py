from fastapi import APIRouter
import app.utils as utils
from configs import get_values_database_sql,get_values_database_nosql_collection_qr, get_values_hosting
import json
from pydantic import BaseModel
import uuid
import qrcode
import base64
from os import remove
from pymongo import MongoClient
from typing import Optional


router = APIRouter(
    prefix="/registrar-maker",
    tags=["registrar-maker"]
    )

host, port, db, usr, pwd = get_values_database_sql('database_remote')

uri_qr, database_no_sql_qr, collection_db_qr = get_values_database_nosql_collection_qr('mongodb_pdn')

hosting = get_values_hosting()

class Maker (BaseModel):
    id_tipo_doc: int
    nro_doc: str
    nombre: str
    apellido: str
    ciudad: Optional[str]
    edad: int
    iglesia: str
    celular: str
    email: Optional[str]
    id_evento: int


@router.post("/")
async def insert_maker(maker: Maker):
    try:
        
        print(f'maker.iglesia: {maker.iglesia}')
        
        conn = utils.conexion_mysql(host,db,usr,pwd)
        cursor = conn.cursor(buffered=True)
        
        id_maker = str(uuid.uuid4().hex)
        insert_maker = f"insert into makerv2(id_makerv2,id_tipo_doc,nro_doc,nombres,apellidos,email,celular,fecha_creacion,fecha_actualizacion) values(UNHEX(\'{id_maker}\'),%s,%s,%s,%s,%s,%s,SYSDATE(),SYSDATE())"
        cursor.execute(insert_maker,(maker.id_tipo_doc, maker.nro_doc, maker.nombre, maker.apellido, maker.email, maker.celular))
        conn.commit()
        print('Nuevo maker registrado')

        #Registrar a maker en evento
        id_evento_maker = str(uuid.uuid4().hex)
        insert_evento_ciudad = f"insert into maker_evento(id,id_makerv2,id_evento, ciudad, iglesia) values(UNHEX(\'{id_evento_maker}\'),UNHEX(\'{id_maker}\'),%s,%s,%s)"
        cursor.execute(insert_evento_ciudad,(maker.id_evento,maker.ciudad,maker.iglesia))
        conn.commit()
        print('Maker registrado a evento')

        nombres_apellidos = maker.nombre +" " +maker.apellido

        #Generar codigoQR
        url_qr = hosting
        url_qr = str(url_qr)+ id_evento_maker
        img = qrcode.make(url_qr)
        print('qr generado correctamente')
        img.save("qr_auxiliar.jpg")
        with open("qr_auxiliar.jpg", "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
            b64_string = str(b64_string)
        remove("qr_auxiliar.jpg")
        client_mongo = MongoClient(uri_qr)
        db_mongo = client_mongo[database_no_sql_qr]
        collection_qr = db_mongo[collection_db_qr]
        mydict = { "id_evento_maker": id_evento_maker, "b64_string": b64_string , "nombres_apellidos" : nombres_apellidos}
        qr_result = collection_qr.insert_one(mydict)
        print(f"Qr Guardado correctamente: {qr_result}")
        client_mongo.close()

        dict_json = {"status":"ok", "codigo_qr":b64_string[2:-1] , "nombres_apellidos" : nombres_apellidos}
    except Exception as error:
        dict_json = {"status": "error"}
        print(f'Ocurrió un error inesperado,, cause: {error.__str__}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json

