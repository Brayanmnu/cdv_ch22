from fastapi import APIRouter
import app.utils as utils
from configs import get_values_database_sql
import json
from pydantic import BaseModel
import uuid
import qrcode
import base64
from os import remove
from pymongo import MongoClient


router = APIRouter(
    prefix="/registrar-maker",
    tags=["registrar-maker"]
    )

host, port, db, usr, pwd = get_values_database_sql('database_local')

class Maker (BaseModel):
    id_tipo_doc: int
    nro_doc: str
    nombre: str
    apellido: str
    id_ciudad: int
    desc_new_ciudad: str
    edad: int
    id_iglesia: int
    desc_new_iglesia: str
    celular: str
    email: str
    id_evento: int


@router.post("/")
async def insert_maker(maker: Maker):
    try:
        conn = utils.conexion_mysql(host,db,usr,pwd)
        cursor = conn.cursor(buffered=True)
        #Validar si es una nueva ciudad
        id_ciudad = maker.id_ciudad
        if id_ciudad == 0:
            insert_ciudad = "insert into ciudad(descripcion) values(%s)"
            cursor.execute(insert_ciudad,(maker.desc_new_ciudad,))
            conn.commit()
            print('Nueva ciudad registrada')

            select_id_ciudad = "select id_ciudad from ciudad where descripcion = %s"
            cursor.execute(select_id_ciudad,(maker.desc_new_ciudad,))
            print('Query ejecutado select_id_ciudad')

            id_ciudad = cursor.fetchone()
            id_ciudad = id_ciudad[0]
            print(f'id_ciudad: {id_ciudad}')

        #Validar si es una iglesia ciudad
        id_iglesia = maker.id_iglesia
        if id_iglesia == 0:
            insert_iglesia = "insert into iglesia(nombre) values(%s)"
            cursor.execute(insert_iglesia,(maker.desc_new_iglesia,))
            conn.commit()
            print('Nueva iglesia registrada')

            select_id_iglesia = "select id_iglesia from iglesia where nombre = %s"
            cursor.execute(select_id_iglesia,(maker.desc_new_iglesia,))
            print('Query ejecutado select_id_ciudad')

            id_iglesia = cursor.fetchone()
            id_iglesia = id_iglesia[0]
            print(f'id_iglesia: {id_iglesia}')

        id_maker = str(uuid.uuid4())
        insert_maker = f"insert into makerv2(id_makerv2,id_tipo_doc,nro_doc,nombres,apellidos,email,celular,fecha_creacion,fecha_actualizacion) values(UUID_TO_BIN(\'{id_maker}\'),%s,%s,%s,%s,%s,%s,SYSDATE(),SYSDATE())"
        cursor.execute(insert_maker,(maker.id_tipo_doc, maker.nro_doc, maker.nombre, maker.apellido, maker.email, maker.celular))
        conn.commit()
        print('Nuevo maker registrado')

        insert_evento_ciudad = f"insert into maker_evento_ciudad(id,id_evento,id_makerv2,id_ciudad) values(UUID_TO_BIN(UUID()),%s,UUID_TO_BIN(\'{id_maker}\'),%s)"
        cursor.execute(insert_evento_ciudad,(maker.id_evento,id_ciudad,))
        conn.commit()
        print('Maker registrado a evento con su ciudad')

        insert_evento_iglesia = f"insert into maker_evento_iglesia(id,id_evento,id_makerv2,id_iglesia) values(UUID_TO_BIN(UUID()),%s,UUID_TO_BIN(\'{id_maker}\'),%s)"
        cursor.execute(insert_evento_iglesia,(maker.id_evento,id_iglesia,))
        conn.commit()
        print('Maker registrado a evento con su iglesia')

        #Generar codigoQR
        
        nombres_apellidos = maker.nombre +" " +maker.apellido
        dict_json = {"status":"ok", "codigo_qr":"XXXXXX/BASE64", "nombres_apellidos" : nombres_apellidos}
    except Exception as error:
        dict_json = {"status": "error"}
        print(f'Ocurrió un error inesperado,, cause: {error.__str__}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json

