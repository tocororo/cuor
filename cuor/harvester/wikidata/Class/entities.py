from cuor.harvester.wikidata.logger_base import logger


class Entities:
    def __init__(self, QID=None, label=None, description=None, alias=None, jsonb=None):
        self.__QID = QID
        self.__label = label
        self.__description = description
        self.__alias = alias
        self.__jsonb = jsonb

    def __str__(self):
        return (
            f'QID: {self.__QID}, '
            f'label: {self.__label}, '
            f'description: {self.__description}'
        )

    def getQID(self):
        return self.__QID

    def setQID(self, QID):
        self.__QID = QID

    def getItemLabel(self):
        return self.__label

    def setItemLabel(self, label):
        self.__label = label

    def getDescription(self):
        return self.__description

    def setDescription(self, description):
        self.__description = description

    def getAlias(self):
        return self.__alias

    def setAlias(self, alias):
        self.__alias = alias

    def getJsonb(self):
        return self.__jsonb

    def setJsonb(self, jsonb):
        self.__jsonb = jsonb


if __name__ == '__main__':
    instance = Entities(QID='Q4564', label='Gomez')
    logger.debug(instance)
