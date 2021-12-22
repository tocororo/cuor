from cuor.harvester.wikidata.logger_base import logger
from psycopg2 import pool
import sys

DB_USERNAME = 'wdorgs'
DB_PASSWORD = 'wdorgs'
#__HOST = 'postgres.sceiba.cu'

class Connection:
    __DATABASE = 'wdorgs'
    __USERNAME = 'wdorgs'
    __PASSWORD = 'wdorgs'
    __DB_PORT = '5432'
    __HOST = '10.143.231.120' #TODO: arreglar, poner la direccion de postgres segun la config
    __MIN_CON = 1
    __MAX_CON = 5
    __pool = None

    @classmethod
    def getPool(cls):
        if cls.__pool is None:
            try:
                cls.__pool = pool.SimpleConnectionPool(
                    cls.__MIN_CON,
                    cls.__MAX_CON,
                    host=cls.__HOST,
                    user=cls.__USERNAME,
                    password=cls.__PASSWORD,
                    port=cls.__DB_PORT,
                    database=cls.__DATABASE)
                logger.debug(f'Pool creation successfully: {cls.__pool}')
                return cls.__pool
            except Exception as e:
                logger.error(f'Error at poll creation: {e}')
                sys.exit()
        else:
            return cls.__pool

    @classmethod
    def getConnection(cls):
        # Obtener una connection del pool
        connection = cls.getPool().getconn()
        logger.debug(f'Connection from pool: {connection}')
        return connection

    @classmethod
    def releaseConnection(cls, connection):
        # Regresar el objeto connection al pool
        cls.getPool().putconn(connection)
        logger.debug(f'Release connection to pool: {connection}')
        logger.debug(f'State of pool: {cls.__pool}')

    @classmethod
    def closeConnections(cls):
        # Cerrar el pool y todas sus conexiones
        cls.getPool().closeall()
        logger.debug(f'Close all connections from pool: {cls.__pool}')


if __name__ == '__main__':
    # Obtener una connection a partir del pool
    conexion1 = Connection.getConnection()
    conexion2 = Connection.getConnection()
    # Regresamos las conexiones al pool
    Connection.releaseConnection(conexion1)
    Connection.releaseConnection(conexion2)
    # Cerramos el pool
    Connection.closeConnections()
    # Si intentamos pedir una connection de un pool cerrado manda error
    # conexion3 = Connection.obtenerConexion()
