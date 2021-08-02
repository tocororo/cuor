from cuor.harvester.wikidata.Controllers.dataCollect import collect, getDataInstance
from cuor.harvester.wikidata.Controllers.entities import Entities

def startCollect(org: str):
    Entities.createTableEntities()
    Entities.createTableOrganizations()
    collect(org)
    getDataInstance('original')
    return org