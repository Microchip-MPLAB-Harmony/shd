# coding: utf-8
"""*****************************************************************************
* Copyright (C) 2023 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*****************************************************************************"""
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
        boardYamlFile = None
        for item in sys.path:
            if path.join("shd", "clickBoards") in item:
                boardYamlFile = path.join(item, yamlFileName)
                break
        else:
            raise AttributeError("clickBoards path is not found in sys path")

        if (boardYamlFile is None) or (not path.isfile(boardYamlFile)):
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
