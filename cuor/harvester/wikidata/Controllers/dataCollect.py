import time
from random import randint

from cuor.harvester.wikidata.Class.entities import Entities
from cuor.harvester.wikidata.Class.organizations import Organizations
from cuor.harvester.wikidata.Controllers.entities import Entities
from cuor.harvester.wikidata.Controllers.organizations import Organizations
from cuor.harvester.wikidata.Database.SPARQL import getSparqlOrganizations, getSparqlEntities, getEntitiesStatements, getEntitiesDescription
from cuor.harvester.wikidata.logger_base import logger


# Q43229
def collect(QID):
    sleep_time = randint(3, 9)
    print('sleep {0} seconds'.format(sleep_time))
    time.sleep(sleep_time)
    sparqlEntities = getSparqlEntities(QID)

    # print(sparqlEntities)
    if sparqlEntities and len(sparqlEntities["results"]["bindings"]) > 0:
        for sparqlI in sparqlEntities["results"]["bindings"]:
            if "countryLabel" in sparqlI and sparqlI["countryLabel"]["value"] == "Cuba":
                instanceCollect(sparqlI)

    postgresOrganizations = Organizations.select()

    sleep_time = randint(3, 9)
    print('sleep {0} seconds'.format(sleep_time))
    time.sleep(sleep_time)
    sparqlOrganizations = getSparqlOrganizations(QID)

    if sparqlOrganizations and len(sparqlOrganizations["results"]["bindings"]) > 0:
        for sparqlS in sparqlOrganizations["results"]["bindings"]:
            _QID = sparqlS["item"]["value"].split('/')
            if not any(_QID[len(_QID) - 1] == postgres.getQID() for postgres in postgresOrganizations):
                subclass = Organizations(_QID[len(_QID) - 1], sparqlS["itemLabel"]["value"])
                subclass_inserted = Organizations.insert(subclass)
                logger.debug(f'Subclass inserted: {subclass_inserted}')
                collect(_QID[len(_QID) - 1])
            else:
                logger.info(f'Organizations exist: {sparqlS["itemLabel"]["value"]}')


def instanceCollect(sparql):
    postgresEntities = Entities.select()
    _QID = sparql["item"]["value"].split('/')
    if not any(_QID[len(_QID) - 1] == postgres.getQID() for postgres in postgresEntities):
        instance = Entities(_QID[len(_QID) - 1], sparql["itemLabel"]["value"])
        instance_inserted = Entities.insert(instance)
        logger.debug(f'Subclass inserted: {instance_inserted}')
    else:
        logger.info(f'Entities exist: {sparql["itemLabel"]["value"]}')


def getDataInstance(updateType):
    postgresEntities = Entities.select()
    for postgres in postgresEntities:
        if postgres.getItemLabel() != 'null' and postgres.getItemLabel() != 'None' and postgres.getItemLabel() != '':
            sleep_time = randint(3, 9)
            print('sleep {0} seconds'.format(sleep_time))
            time.sleep(sleep_time)
            infoInstances = getEntitiesStatements(postgres.getItemLabel())
            desc_alias = getEntitiesDescription(postgres.getItemLabel())

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

            if len(infoInstances["results"]["bindings"]) > 0:
                instance = Entities(
                    postgres.getQID(), None, __description, __alias, infoInstances["results"]["bindings"]
                )
                if updateType == 'original':
                    instance_updated = Entities.update(instance)
                    logger.info(f'Instance Updated: {instance_updated}')
                elif updateType == 'copy':
                    instance_updated = Entities.updateCopy(instance)
                    logger.info(f'Instance Updated: {instance_updated}')
