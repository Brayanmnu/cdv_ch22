from fastapi import APIRouter
import app.utils as utils
from configs import get_values_database_sql
import json


router = APIRouter(
    prefix="/tipo-documento",
    tags=["tipo-documento"]
    )

host, port, db, usr, pwd = get_values_database_sql('database_remote')

@router.get("/")
async def get_all_tipo_documento():
    dict_json = []
    try:
        conn = utils.conexion_mysql(host,db,usr,pwd)
        query = "SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id_tipo_documento, 'descripcion', descripcion)) from TIPO_DOCUMENTO"
        cursor = conn.cursor()
        cursor.execute(query)
        print('Query ejecutado')
        records = cursor.fetchall()
        for row in records:
            dict_json = json.loads(row[0])
    except Exception as error:
        print('Ocurrió un error inesperado')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    return dict_json

