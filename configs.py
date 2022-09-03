from configparser import ConfigParser

file = "config.ini"
config = ConfigParser()
config.read(file)

def get_values_database_sql(entorno):
    if entorno=='database_local':
        host = config[entorno]['host']
        port = config[entorno]['port']
        db = config[entorno]['db']
        usr = config[entorno]['usr']
        pwd = config[entorno]['pwd']
    return host, port, db, usr, pwd

