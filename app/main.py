from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.cruds import tipo_documento_crud

app = FastAPI()

'''
SECCION DONDE SE LLAMAN A LAS APIS DESARROLLADAS
'''
# CRUDS
app.include_router(tipo_documento_crud.router)

#MODULES


'''
SECCION DONDE SE AGREGAN LOS CORS
'''
origins = [
    "https://coquitofrontadmin.herokuapp.com",
    "http://localhost",
    "http://localhost:3000",
    "https://adminv2.ferrerepuestoscoquito.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


'''
SECCION DONDE SE INICIALIZA LA APLICACION
'''
@app.get("/")
async def root():
    return {"message": "WELCOME TO APP CONGRESO-HACEDORES"}

