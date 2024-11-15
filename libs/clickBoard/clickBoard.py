import sys
from os import path
from copy import deepcopy
from utils.connectorSpec import getConnectorSignalMapMikroToBUSXplainPro

shdClickBoardHelp = 'SHDClickBoardHelp'

class ClickBoard:
    def __init__(self, yamlFileName):
        self.__currentConfig = {}
        self.__useXplainProAdaptor = False
        self.__hwAdaptatorComponent = None
        for item in sys.path:
            if "shd\\clickBoards" in item:
                boardYamlFile = path.join(item, yamlFileName)
                break
        else:
            raise AttributeError("clickBoards path is not found in sys path")

        if not path.isfile(boardYamlFile):
            raise AttributeError("{} does not exist".format(boardYamlFile))
        
        import yaml
        with open(boardYamlFile, 'r') as file:
            self.__defaultConfig = yaml.safe_load(file)
            if isinstance(self.__defaultConfig, dict) == False:
                raise AttributeError("{} file format is not correct".format(boardYamlFile))

            if self.__defaultConfig.get('supported') == None:
                raise AttributeError("{} data content is not correct".format(boardYamlFile))

            self.__currentConfig = deepcopy(self.__defaultConfig)

    def __str__(self):
        return "{}".format(self.__currentConfig)

    def getName(self):
        return self.__currentConfig.get('name')

    def getDescription(self):
        return self.__currentConfig.get('description')

    def getDocumentation(self):
        return self.__currentConfig.get('documentation')

    def getConnectorCompatible(self):
        return self.__currentConfig.get('compatible')

    def getConnections(self):
        return self.__currentConfig.get('supported')

    def getDependencies(self):
        return self.__currentConfig.get('dependencies')

    def getMulticonnection(self):
        return self.__currentConfig.get('multiconnection')
    
    def convertFromMikroBusToXplainProBoard(self):
        if self.__currentConfig['compatible'] == 'mikrobus':
            self.__useXplainProAdaptor = True
            # Rename Signals
            signalMapRename = getConnectorSignalMapMikroToBUSXplainPro()
            signalSupport = self.__currentConfig['supported']

            # Signal Map : {XplainPro, mikroBus}
            for key, value in signalSupport.items():
                newKey = signalMapRename.get(key)
                if newKey != None:
                    signalSupport.setdefault(newKey, value)
                    del signalSupport[key]

    def restoreFromXplainProToMikroBusBoard(self):
        if self.__useXplainProAdaptor == True:
            self.__currentConfig = deepcopy(self.__defaultConfig)
            self.__useXplainProAdaptor = False
