from connection import Connection
from cuor.harvester.wikidata.logger_base import logger


class CursorPool:
    def __init__(self):
        self.__conn = None
        self.__cursor = None

    # inicio de with
    def __enter__(self):
        logger.debug('Start method __enter__')
        self.__conn = Connection.getConnection()
        self.__cursor = self.__conn.cursor()
        return self.__cursor

    # fin del bloque with
    def __exit__(self, exception_type, exception_value, exception_traceback):
        logger.debug('Execute method __exit__()')
        # if exception_value is not None:
        if exception_value:
            self.__conn.rollback()
            logger.debug(f'Error exception: {exception_value}')
        else:
            self.__conn.commit()
            logger.debug('Transaction commit')
            # Cerramos el cursor
        self.__cursor.close()
        # Regresar la conexión al pool
        Connection.releaseConnection(self.__conn)


if __name__ == '__main__':
    # Obtenemos un cursor  a partir de la conexión del pool
    # with se ejecuta __enter__ y termina con __exit__
    with CursorPool() as cursor:
        cursor.execute('SELECT * FROM "subClass"')
        logger.debug('Listado de personas')
        logger.debug(cursor.fetchall())
