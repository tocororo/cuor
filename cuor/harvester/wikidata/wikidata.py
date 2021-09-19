from cuor.harvester.wikidata.Controllers.dataCollect import collect, getDataInstance
from cuor.harvester.wikidata.Controllers.instance import Instance


async def startCollect(org: str):
    await Instance.createTableInstance()
    await Instance.createTableSubclass()
    await collect(org)
    await getDataInstance('original')
    return org
