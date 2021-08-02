import json

from Class.instance import Instance
from Database.connection import DB_USERNAME
from Database.cursorPool import CursorPool
from logger_base import logger


class Instance:
    '''
    DAO (Data Access Object) 
    CRUD: Create-Read-Update-Delete entidad instance
    '''
    __CREATE_INSTANCE = """CREATE TABLE public."instanceOf"(
                            qid character varying COLLATE pg_catalog."default" NOT NULL,
                            label character varying COLLATE pg_catalog."default",
                            "itemDescription" character varying COLLATE pg_catalog."default",
                            "itemAlias" character varying COLLATE pg_catalog."default",
                            "statements" jsonb COLLATE pg_catalog."default",
                            "firstImport" date COLLATE pg_catalog."default" NOT NULL,
                            "lastImport" date COLLATE pg_catalog."default" NOT NULL,
                            "firstUserInImport" character varying COLLATE pg_catalog."default" NOT NULL,
                            "lastUserImport" character varying COLLATE pg_catalog."default" NOT NULL,
                            "state" character varying COLLATE pg_catalog."default NOT NULL,
                            CONSTRAINT "instanceOf_pkey" PRIMARY KEY (qid)
                        )
                        
                        TABLESPACE pg_default;                        
                        
                        ALTER TABLE public."instanceOf"
                            OWNER to """ f'{DB_USERNAME}'""";
                        
                        CREATE OR REPLACE FUNCTION public."before_insert_instanceofFUN"()
                            RETURNS trigger
                            LANGUAGE 'plpgsql'
                            VOLATILE
                            COST 100
                        AS $BODY$
                        BEGIN
                             if EXISTS (select qid FROM "instanceOf" WHERE qid = new.qid ) then 
                                RETURN NULL;
                             else
                                RETURN NEW;
                            end if;
                        END;
                        $BODY$;
                        
                        CREATE TRIGGER before_insert_instanceof
                            BEFORE INSERT
                            ON public."instanceOf"
                            FOR EACH ROW
                            EXECUTE PROCEDURE public."before_insert_instanceofFUN"();"""

    __CREATE_SUBCLASS = """CREATE TABLE public."subClass"
                        (
                            qid character varying(255) COLLATE pg_catalog."default" NOT NULL,
                            label character varying(255) COLLATE pg_catalog."default",
                            CONSTRAINT "subClass_pkey" PRIMARY KEY (qid)
                        )
                        
                        TABLESPACE pg_default;
                        
                        ALTER TABLE public."subClass"
                            OWNER to """ f'{DB_USERNAME}'""";
                        
                        CREATE OR REPLACE FUNCTION public."before_insert_subclassFUN"()
                            RETURNS trigger
                            LANGUAGE 'plpgsql'
                            VOLATILE
                            COST 100
                        AS $BODY$
                        BEGIN
                             if EXISTS (select qid FROM public."subClass" WHERE qid = new.qid ) then 
                                RETURN NULL;
                             else
                                RETURN NEW;
                            end if;
                        END;
                        $BODY$;
                        
                        CREATE TRIGGER before_insert_subclass
                            BEFORE INSERT
                            ON public."subClass"
                            FOR EACH ROW
                            EXECUTE PROCEDURE public."before_insert_subclassFUN"();"""

    __CREATE_COPY_INSTANCEOF = 'CREATE TABLE IF NOT EXISTS public."instanceOfCopy" AS SELECT * FROM "instanceOf";'
    __SELECT = 'SELECT * FROM public."instanceOf";'
    __INSERT = 'INSERT INTO public."instanceOf"(qid, label) VALUES(%s,%s);'
    __UPDATE = """ UPDATE public."instanceOf" SET "itemDescription"=%s, "itemAlias"=%s, statements = %s
                WHERE qid = %s;"""
    __UPDATE_COPY = """UPDATE public."instanceOfCopy" SET statements = %s
                WHERE qid = %s;"""
    __DROP_TABLES = """DROP TABLE IF EXISTS public."subClass", public."instanceOf", public."instanceOfCopy" CASCADE;"""
    __DROP_FUNCTIONS = """DROP FUNCTiON IF EXISTS public."before_insert_instanceofFUN"(), public."before_insert_subclassFUN"() CASCADE;"""
    __GENERATE_JSON = 'SELECT array_to_json(array_agg(row_to_json(u))) FROM public."instanceOf" u;'

    @classmethod
    def createJson(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__GENERATE_JSON))
            cursor.execute(cls.__GENERATE_JSON)
            result = cursor.fetchone()
            result = str(result).replace("(", "")
            result = str(result).replace(")", "")
            return result

    @classmethod
    def generateJSON(cls):
        result = cls.createJson()
        try:
            archivo = open("wd-orgs.json", "w")
            archivo.write(result)
            logger.info('Archive wd-orgs.json created successfully')
        except Exception as e:
            logger.error(f'Ups failed to create wd-orgs.json archive {e}')
        finally:
            archivo.close()
        return result

    @classmethod
    def createTableSubclass(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__CREATE_SUBCLASS))
            cursor.execute(cls.__CREATE_SUBCLASS)
            return cursor.rowcount

    @classmethod
    def createTableInstance(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__CREATE_INSTANCE))
            cursor.execute(cls.__CREATE_INSTANCE)
            return cursor.rowcount

    @classmethod
    def dropTables(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__DROP_TABLES))
            cursor.execute(cls.__DROP_TABLES)
            return cursor.rowcount

    @classmethod
    def dropFunctions(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__DROP_FUNCTIONS))
            cursor.execute(cls.__DROP_FUNCTIONS)
            return cursor.rowcount

    @classmethod
    def createInstanceCopy(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__CREATE_COPY_INSTANCEOF))
            cursor.execute(cls.__CREATE_COPY_INSTANCEOF)
            return cursor.rowcount

    @classmethod
    def select(cls):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__SELECT))
            cursor.execute(cls.__SELECT)
            results = cursor.fetchall()
            instances = []
            for result in results:
                instance = Instance(result[0], result[1])
                instances.append(instance)
            return instances

    @classmethod
    def insert(cls, instance):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__INSERT))
            logger.debug(f'instance to insert: {instance}')
            values = (instance.getQID(), instance.getItemLabel())
            cursor.execute(cls.__INSERT, values)
            return cursor.rowcount

    @classmethod
    def update(cls, instance):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__UPDATE))
            logger.debug(f'instance to update: {instance.getQID()}')
            values = (
                instance.getDescription(), instance.getAlias(), json.dumps(instance.getStatements()), instance.getQID())
            cursor.execute(cls.__UPDATE, values)
            return cursor.rowcount

    @classmethod
    def updateCopy(cls, instance):
        with CursorPool() as cursor:
            logger.debug(cursor.mogrify(cls.__UPDATE_COPY))
            logger.debug(f'instance to update: {instance.getQID()}')
            values = (instance.getDescription(), instance.getAlias(), instance.getStatements(), instance.getQID())
            cursor.execute(cls.__UPDATE_COPY, values)
            return cursor.rowcount


if __name__ == '__main__':
    instances = Instance.select()
    for instance in instances:
        logger.debug(instance)
        logger.debug(instance.getQID())
