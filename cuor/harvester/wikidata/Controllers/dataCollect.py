import time
from enum import Enum
from random import randint

from cuor.harvester.wikidata.Controllers.instance import Instance
from cuor.harvester.wikidata.Controllers.subclass import Subclass
from cuor.harvester.wikidata.Database.SPARQL import getSparqlSubclass, getSparqlInstance, getInstanceStatements, getInstanceDescription
from cuor.harvester.wikidata.logger_base import logger


class States(Enum):
    existente = 'Existente'
    noExistente = 'NoExistente'
    conSemejantes = 'ConSemejantes'
    sinSemejantes = 'SinSemejantes'
    desambiguada = 'Desambiguada'
    noDesambiguada = 'NoDesambiguada'
    coincidencias = 'Coincidencias'
    noCoincidencias = 'NoCoincidencias'
    combinada = 'Combinada'
    conflictoAlCombinar = 'ConflictoAlCombinar'
    noCombinada = 'NoCombinada'


# Q43229
def collect(QID):
    sleep_time = randint(3, 9)
    print('sleep {0} seconds'.format(sleep_time))
    time.sleep(sleep_time)
    sparqlInstance = getSparqlInstance(QID)

    # print(sparqlInstance)
    if sparqlInstance and len(sparqlInstance["results"]["bindings"]) > 0:
        for sparqlI in sparqlInstance["results"]["bindings"]:
            if "countryLabel" in sparqlI and sparqlI["countryLabel"]["value"] == "Cuba":
                instanceCollect(sparqlI)

    postgresSubclass = Subclass.select()

    sleep_time = randint(3, 9)
    print('sleep {0} seconds'.format(sleep_time))
    time.sleep(sleep_time)
    sparqlSubclass = getSparqlSubclass(QID)

    if sparqlSubclass and len(sparqlSubclass["results"]["bindings"]) > 0:
        for sparqlS in sparqlSubclass["results"]["bindings"]:
            _QID = sparqlS["item"]["value"].split('/')
            if not any(_QID[len(_QID) - 1] == postgres.getQID() for postgres in postgresSubclass):
                subclass = Subclass(_QID[len(_QID) - 1], sparqlS["itemLabel"]["value"])
                subclass_inserted = Subclass.insert(subclass)
                logger.debug(f'Subclass inserted: {subclass_inserted}')
                collect(_QID[len(_QID) - 1])
            else:
                logger.info(f'Subclass exist: {sparqlS["itemLabel"]["value"]}')


def instanceCollect(sparql):
    postgresInstance = Instance.select()
    _QID = sparql["item"]["value"].split('/')
    if not any(_QID[len(_QID) - 1] == postgres.getQID() for postgres in postgresInstance):
        instance = Instance(_QID[len(_QID) - 1], sparql["itemLabel"]["value"])
        instance_inserted = Instance.insert(instance)
        logger.debug(f'Subclass inserted: {instance_inserted}')
    else:
        logger.info(f'Instance exist: {sparql["itemLabel"]["value"]}')


def getDataInstance(updateType):
    postgresInstance = Instance.select()
    for postgres in postgresInstance:
        if postgres.getItemLabel() != 'null' and postgres.getItemLabel() != 'None' and postgres.getItemLabel() != '':
            sleep_time = randint(3, 9)
            print('sleep {0} seconds'.format(sleep_time))
            time.sleep(sleep_time)
            infoInstance = getInstanceStatements(postgres.getItemLabel())
            desc_alias = getInstanceDescription(postgres.getItemLabel())

            if len(desc_alias["results"]["bindings"]) > 0:
                desc_alias = desc_alias["results"]["bindings"]
                desc_alias = desc_alias[0]
                if "itemDescription" in desc_alias:
                    __description = desc_alias["itemDescription"]["value"]
                else:
                    __description = None

                if "itemAltLabel" in desc_alias:
                    __alias = desc_alias["itemAltLabel"]["value"]
                else:
                    __alias = None

            if len(infoInstance["results"]["bindings"]) > 0:
                instance = Instance(
                    postgres.getQID(), None, __description, __alias, infoInstance["results"]["bindings"]
                )
                if updateType == 'original':
                    instance_updated = Instance.update(instance)
                    logger.info(f'Instance Updated: {instance_updated}')
                elif updateType == 'copy':
                    instance_updated = Instance.updateCopy(instance)
                    logger.info(f'Instance Updated: {instance_updated}')
