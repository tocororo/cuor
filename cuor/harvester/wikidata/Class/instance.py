from cuor.harvester.wikidata.logger_base import logger


class Instance:
    def __init__(self, QID=None, label=None, description=None, alias=None, statements=None, firstImport=None,
                 lastImport=None, firstUserInImport=None, lastUserImport=None, state=None):
        self.__QID = QID
        self.__label = label
        self.__description = description
        self.__alias = alias
        self.__statements = statements
        self.__firstImport = firstImport
        self.__lastImport = lastImport
        self.__firstUserInImport = firstUserInImport
        self.__lastUserImport = lastUserImport
        self.__state = state

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

    def getStatements(self):
        return self.__statements

    def setStatements(self, statements):
        self.__statements = statements

    def getFirstImport(self):
        return self.__firstImport

    def setFirstImport(self, firstImport):
        self.__firstImport = firstImport

    def getLastImport(self):
        return self.__lastImport

    def setLastImport(self, lastImport):
        self.__lastImport = lastImport

    def getFirstUserInImport(self):
        return self.__firstUserInImport

    def setFirstUserInImport(self, firstUserInImport):
        self.__firstUserInImport = firstUserInImport

    def getLastUserImport(self):
        return self.__lastUserImport

    def setLastUserImport(self, lastUserImport):
        self.__lastUserImport = lastUserImport

    def getState(self):
        return self.__state

    def setState(self, state):
        self.__state = state


if __name__ == '__main__':
    instance = Instance(QID='Q4564', label='Gomez')
    logger.debug(instance)
