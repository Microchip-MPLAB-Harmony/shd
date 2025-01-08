import sys
from os import path
import glob
from copy import deepcopy
from utils.connectorSpec import getConnectorPinNumberFromSignal, getConnectorSignalMapXplainProToMikroBUS
from utils.deviceSpec import getDeviceFunctionListByPinId, getDevicePinMap, getDeviceGPIOPeripheral, adaptDevicePeripheralDependencies
from utils.dBMsgInterface import getDBMsgPLIBConfiguration, getDBMsgDriverConfiguration, getAutoconnectTable, getDriverDependencyFromPin, checkPlibFromSignalConnector
from clickBoard.clickBoard import ClickBoard

shdMainBoardHelp = 'shdMainBoardHelpKeyword'
shdMultiInstanceDrivers = ['drv_i2c', 'drv_spi', 'drv_usart', 'drv_sdmmc', 'a_drv_i2s', 'drv_sdspi', 'sys_console', 'RNBD_Dependency', 'atecc108a', 'atecc508a', 'atecc608', 'atsha204a', 'atsha206a', 'ecc204', 'sha104', 'sha105', 'ta010']

class MainBoard:
    def __init__(self, context):
        self.__currentConfig = {}
        boardYamlFile = None
        for item in sys.path:
            pathToCheck = path.join("shd", "boards")
            if pathToCheck in item:
                boardYamlFile = path.join(item, context["configuration"])

            pathToCheck = path.join("shd", "clickBoards")
            if pathToCheck in item:
                clickBoardsPath = item

        if (boardYamlFile is None) or (not path.isfile(boardYamlFile)):
            return None

        self.__db = context["database"]
        self.__atdf = context["atdf"]
        self.__log = context["log"]
        self.__pioPeripheralID = 0
        self.__symbolInterfaceByPin = {}
        self.__symbolNamesByConnector = {}
        self.__symbolPinByParent = {}
        self.__collisionsByPinID = {}
        self.__devicePinMap = getDevicePinMap(self.__db, self.__atdf)
        self.__configuredPins = []
        self.__pinControlByPinId = {}
        self.__symbolInterfaces = {}
        self.__symbolConnectors = {}
        self.__signalCallbackBusy = False
        self.__depBindings = {}
        self.__shdDependenciesPlibMultiInstance = {}
        self.__connections = {}
        self.__drvUnconnected = {}
        self.__shdCheckCollisionSymbol = None
        self.__architecture = self.__atdf.getNode("/avr-tools-device-file/devices/device").getAttribute("architecture")
        self.__family = self.__atdf.getNode("/avr-tools-device-file/devices/device").getAttribute("family")
        self.__connectorAdaptorSymbols = {}

        # self.__log.writeInfoMessage("SHD >> __devicePinMap: {}".format(self.__devicePinMap))
        # self.__log.writeInfoMessage("SHD >> __architecture: {}".format(self.__architecture))
        # self.__log.writeInfoMessage("SHD >> __family: {}".format(self.__family))
        
        import yaml
        with open(boardYamlFile, 'r') as file:
            self.__defaultConfig = yaml.safe_load(file)
            self.__currentConfig = deepcopy(self.__defaultConfig)
            self.__interfaceID = "mainBoard_" + self.__defaultConfig['config'].split(".")[0].upper() 

        clickBoardFileList = glob.glob(path.join(clickBoardsPath, '*.yml'))
        self.__clickBoardFileList = {}
        self.__connectedClickBoards = {}
        for clickBoardFile in clickBoardFileList:
            clickBoardFileName = path.basename(clickBoardFile)
            # self.__log.writeInfoMessage("SHD >> clickBoardFileName: {}".format(clickBoardFileName))
            try:
                clickBoardInstance = ClickBoard(clickBoardFileName)
                clickBoardName = clickBoardInstance.getName()
                clickBoardCompatible = clickBoardInstance.getConnectorCompatible()
                self.__clickBoardFileList.setdefault(clickBoardFileName, (clickBoardName, clickBoardCompatible))
                del clickBoardInstance
            except: #Exception as error:
                # self.__log.writeInfoMessage("SHD >> ERROR loading click board : {}".format(error))
                continue

        # self.__log.writeInfoMessage("SHD >> self.__clickBoardFileList: {}".format(self.__clickBoardFileList))

    def __del__(self):
        # self.__log.writeInfoMessage("SHD >> __del__ MainBoard")
        self.resetSignalConfiguration()
        
    def __str__(self):
        return "{}".format(self.__currentConfig)

    def __checkComponentAvailable(self, component):
        # Handle exceptions
        if component.lower() in ['int', 'aic', 'supc']:
            return True
        
        if component.lower() == 'unused':
            return False
        
        if self.__db.isComponentAvailable(component) == False:
            # if component != "":
            #     self.__log.writeInfoMessage("SHD >> WARNING: {} component is not available in your Harmony Content Path.".format(component))
            #     self.__log.writeInfoMessage("SHD >> To be able to use this component, please download the proper H3 repository.")
            return False

        return True
            
    def __setPLIBSettings(self, pinDescr, value):
        idActiveList = self.__db.getActiveComponentIDs()
        for signalId, (pinId, functionValue, nameValue) in pinDescr.items():
            if functionValue.lower() == 'unused':
                continue
            
            functionValue = functionValue.replace(" (in)", "")
            functionValue = functionValue.replace(" (out)", "")
            functionValue = functionValue.replace(" (in/out)", "")
            settings = (signalId, pinId, functionValue, nameValue, value)
            # self.__log.writeInfoMessage("SHD >> __setPLIBSettings : {}".format(settings))
            componentID, messageID, params = getDBMsgPLIBConfiguration(self.__atdf, settings)
            if messageID != None and componentID in idActiveList:
                # self.__log.writeInfoMessage("SHD >> __setPLIBSettings: sending message to {} : {}. params: {}".format(componentID, messageID, params))
                res = self.__db.sendMessage(componentID, messageID, params)
                # if res != None and res.get("Result") != "Success":
                #     self.__log.writeInfoMessage("SHD mainBoard: Error in sending message to PLIB {} : {}({}). Error: {}".format(componentID, messageID, params, res.get("Result")))
            # else:
                # self.__log.writeInfoMessage("SHD >> __setPLIBSettings skip {} messageID:{} idActiveList{}".format(componentID, messageID, idActiveList))

    def __setDriverSettings(self, pinDescr, value):
        # self.__log.writeInfoMessage("SHD >> __setDriverSettings pinDescr: {}".format(pinDescr))
        # Find driver connection
        for signalId, (pinId, functionValue, nameValue) in pinDescr.items():
            if functionValue.lower() != 'unused':
                for plib, driver in self.__connections.items():
                    settings = (driver, signalId, pinId, functionValue, nameValue, value)
                    # self.__log.writeInfoMessage("SHD >> __setDriverSettings Connections : {}".format(settings))
                    componentID, messageID, params = getDBMsgDriverConfiguration(settings)
                    if messageID != None:
                        # self.__log.writeInfoMessage("SHD >> __setDriverSettings: sending message - {} : {}. params: {}".format(componentID, messageID, params))
                        res = self.__db.sendMessage(componentID, messageID, params)
                        # if res != None and res.get("Result") != "Success":
                        #     self.__log.writeInfoMessage("SHD mainBoard: skip sending message to DRV {} : {}. Error: {}".format(componentID, messageID, res.get("Result")))
                    # else:
                    #     self.__log.writeInfoMessage("SHD >> __setDriverSettings ERROR : {} {} {}".format(componentID, messageID, params))

                for driver, drvConfigured in self.__drvUnconnected.items():
                    if drvConfigured == False:
                        self.__drvUnconnected[driver] = True
                        settings = (driver, signalId, pinId, functionValue, nameValue, value)
                        componentID, messageID, params = getDBMsgDriverConfiguration(settings)
                        if messageID != None:
                            if (messageID == "WIRELESS_RNWF_CONFIG_HW_IO"):
                                addon, plib, enable = params['config']
                                wifiParams = dict()
                                wifiParams.setdefault('host', self.__currentConfig.get('name'))
                                wifiParams.setdefault('addon', addon)
                                wifiParams.setdefault('plib', self.__currentConfig.get('name'))
                                wifiParams.setdefault('enable', self.__currentConfig.get('name'))
                                # self.__log.writeInfoMessage("SHD >> sending Wifi message -  {} : {}. params: {}".format(componentID, messageID, wifiParams))
                                res = self.__db.sendMessage(componentID, messageID, wifiParams)
                                # self.__log.writeInfoMessage("SHD >> Wifi message result: {}".format(res))

    def __clearPinConfig(self, pinControl):
        # self.__log.writeInfoMessage("SHD >> __clearPinConfig pinControl: {}".format(pinControl))
        pinNumber = self.__devicePinMap.get(pinControl.get('pinId'))

        for key, value in pinControl.items():
            if key == 'pinId':
                continue
            
            params = dict()
            params.setdefault('pinNumber', pinNumber)
            params.setdefault('setting', key)
            # self.__log.writeInfoMessage("SHD >> send Message PIN_CLEAR_CONFIG_VALUE : {}".format(params))
            self.__db.sendMessage("core", "PIN_CLEAR_CONFIG_VALUE", params)

    def __handleFunctionPioManager(self, pinCtrlFunction, functionByPinId):
        # self.__log.writeInfoMessage("SHD >> __handleFunctionPioManager {} : {}".format(pinCtrlFunction, functionByPinId))
        if 'MCSPI' in pinCtrlFunction:
            functionValues = functionByPinId.split('/')
            # self.__log.writeInfoMessage("SHD >> __handleFunctionPioManager {}".format(functionValues))
            for function in functionValues:
                if pinCtrlFunction in function:
                    return function

        # Adapt function name for some family devices (WBZ)
        if "WBZ" in self.__family:
            if "ADCHS" in pinCtrlFunction:
                pinCtrlFunction = pinCtrlFunction.split("_")[-1]
                
            return pinCtrlFunction

        # Adapt function name for MIPS architecture
        if self.__architecture == "MIPS" or self.__architecture == "33Axxx":
            pinCtrlFunction = pinCtrlFunction.split("_")[-1]
            # self.__log.writeInfoMessage("SHD >> __handleFunctionPioManager MIPS: {}".format(pinCtrlFunction))

        if functionByPinId.startswith(pinCtrlFunction):
            return functionByPinId

        return None

    def __setPinConfig(self, pinControl):
        # self.__log.writeInfoMessage("SHD >> __setPinConfig pinControl: {}".format(pinControl))
        pinId = pinControl.get('pinId')
        pinNumber = self.__devicePinMap.get(pinId)
        pinFunction = pinControl.get('function')
        if pinFunction.lower() != 'unused':
            # Get function values list from the pinNumber
            functionList = getDeviceFunctionListByPinId(self.__db, self.__atdf, pinId)
            # self.__log.writeInfoMessage("SHD >> pin {} - functionList {}".format(pinId, functionList))

            # Sort dictionary by key to set function as first setting
            sortedKeys = sorted(pinControl.keys())
            sortedPinControl = {key:pinControl[key] for key in sortedKeys}
            findFunction = False

            for key, value in sortedPinControl.items():
                if key == 'pinId':
                    continue
                
                if key == 'function':
                    for functionIndex in range(len(functionList)):
                        # Adapt Function Name to the function used in Pio Manager
                        newValue = self.__handleFunctionPioManager(value, functionList[functionIndex])
                        if newValue != None:
                            value = newValue
                            findFunction = True
                            break
                        
                    if findFunction == False:
                        self.__log.writeInfoMessage("SHD mainBoard: Error in function setting of pinId: {} - function: {}".format(pinId, value))
                        self.__log.writeInfoMessage("SHD mainBoard: Match function setting with one of these values: {}".format(functionList))
                        continue
                            
                if key == 'function':
                    value = value.upper()
                    value = value.replace("(IN)", "(in)")
                    value = value.replace("(OUT)", "(out)")
                    value = value.replace("(IN/OUT)", "(in/out)")
                elif key in ['name', 'pinId']:
                    value = value.upper()
                elif type(value).__name__ == 'bool':
                    if key in ['pull up', 'pull down', 'open drain', 'change notification', 'slewrate']:
                        value = "True" if value else "False"
                else:
                    value = value.title()
                    
                # Don't set any value in case of direction: input
                # if key == 'direction' and value == 'In':
                #     continue

                params = dict()
                params.setdefault('pinNumber', pinNumber)
                params.setdefault('setting', key)
                params.setdefault('value', value)
                # self.__log.writeInfoMessage("SHD >> send Message PIN_SET_CONFIG_VALUE : {}".format(params))
                self.__db.sendMessage("core", "PIN_SET_CONFIG_VALUE", params)

    def __checkPinIsConfigured(self, pinId):
        params = dict()
        pinNumber = self.__devicePinMap.get(pinId)
        params.setdefault('pinNumber', pinNumber)
        params.setdefault('setting', 'function')
        retDict = self.__db.sendMessage("core", "PIN_GET_CONFIG_VALUE", params)
        functionValue = retDict.get('value')
        # self.__log.writeInfoMessage("SHD >> __checkPinIsConfigured {} : {}".format(pinId, functionValue))
        if functionValue == "":
            return False
        else:
            return True
    
    def __showSymbol(self, symbol, event):
        eventSymbolID = event['id']
        eventValue = event['value']
        # self.__log.writeInfoMessage("SHD >> __showSymbol eventSymbolID: {} - {}".format(eventSymbolID, eventValue))
        if "CSASGPIO" in eventSymbolID:
            # self.__log.writeInfoMessage("SHD >> __showSymbol eventSymbolID: {}".format(eventSymbolID))
            global mainBoard
            connectorName = self.getConnectorNameFromSymbolID(eventSymbolID)
            newPinControl = {"spi":{"cs":{"function": "GPIO","direction": "out","latch": "high"}}}
            if eventValue == True:
                # Update the pin function
                self.updatePinControlByConnector(connectorName, newPinControl)
            else:
                # Restore the pin function by default
                self.restorePinControlByConnector(connectorName)
                
            # Set Pin configuration
            spiPinControlList = self.getPinControlListByConnectorSignal(connectorName, 'spi')
            for spiPinControl in spiPinControlList:
                signal, pinControl = spiPinControl
                if signal == 'cs':
                    self.__clearPinConfig(pinControl)
                    self.__setPinConfig(pinControl)
                    newLabel = self.__updateFunctionInSymbolLabel(pinControl['function'], symbol.getLabel())
                    symbol.setLabel(newLabel)
                    # self.__log.writeInfoMessage("SHD >> __showSymbol cs detected. Set newlabel: {}".format(newLabel))
        else:
            # self.__log.writeInfoMessage("SHD >> __showSymbol {} setVisible: {}".format(symbol.getLabel(), eventValue))
            if 'unused' not in symbol.getLabel().lower():
                symbol.setVisible(eventValue)
            else:
                # self.__log.writeInfoMessage("SHD >> __showSymbol detected unused function: {}".format(symbol.getLabel()))
                symbol.setVisible(False)

    def __showSettingSymbol(self, symbol, event):
        eventSymbolID = event['id']
        eventValue = event['value']
        symbolName = symbol.getID()
        symbol.setVisible(symbolName == "{}_{}".format(eventSymbolID, eventValue))

    def __setVisibleSignals(self, enable, parentSymbol, pinId):
        board = self.__db.getComponentByID(self.__interfaceID)
        symbolList = self.__symbolPinByParent.get(parentSymbol)
        for symbol in symbolList:
            if pinId in symbol:
                symbolInterface = board.getSymbolByID(symbol)
                symbolInterface.setVisible(enable)
                # self.__log.writeInfoMessage("SHD >> __setVisibleSignals {} -> {}".format(symbol, enable))
                
    def __checkAllSignalsDisabled(self, symbol):
        symbolSignals = self.__symbolPinByParent.get(symbol)
        # self.__log.writeInfoMessage("SHD >> __checkAllSignalsDisabled {}: {}".format(symbol, symbolSignals))
        for symbolId in symbolSignals:
            pinId = symbolId.split('_')[-1]
            if pinId in self.__configuredPins:
                # self.__log.writeInfoMessage("SHD >> __checkAllSignalsDisabled {} PinId: {} is configured".format(symbolId, pinId))
                return False
            
        return True

    def __checkGlobalCollisions(self, symbol, event):
        enablePin = event['value']
        if enablePin == True:
            # Pin Callback selects TRUE. Set rest of the signals with the same Pin as Read Only
            for pinId in self.__configuredPins:
                # Get collision pins in configuredPins
                symbolList = self.__collisionsByPinID.get(pinId)
                # self.__log.writeInfoMessage("SHD >> __checkGlobalCollisions check PinId:{} symbolList:{}".format(pinId, symbolList))
                if symbolList != None:
                    for symbolId in symbolList:
                        symbolInterface = self.__symbolInterfaces.get(symbolId)
                        if symbolInterface != None:
                            if symbolInterface.getValue() == False:
                                # self.__log.writeInfoMessage("SHD >> __checkGlobalCollisions set Read Only - symbolId: {}".format(symbolId))
                                if symbolId.find('SPI') == -1:
                                    symbolInterface.setReadOnly(True)
                                self.__setVisibleSignals(True, symbolId, pinId)
        else:
            # Pin Callback selects False. Clear Read Only values
            for pinId, symbolList in self.__collisionsByPinID.items():
                if pinId in self.__configuredPins:
                    # self.__log.writeInfoMessage("SHD >> __checkGlobalCollisions pind is still configured: {}".format(pinId))
                    continue
                
                # If collision Pin has not been configured. Free Symbol if all subsignals are disabled.
                for symbolId in symbolList:
                    symbolInterface = self.__symbolInterfaces.get(symbolId)
                    if symbolInterface != None:
                        if symbolInterface.getReadOnly() == True:
                            if self.__checkAllSignalsDisabled(symbolId) == True:
                                # self.__log.writeInfoMessage("SHD >> __checkGlobalCollisions clear Read Only - symbolId: {}".format(symbolId))
                                symbolInterface.setReadOnly(False)
                                self.__setVisibleSignals(False, symbolId, pinId)
                        elif symbolId.find('SPI') != -1:
                            self.__setVisibleSignals(False, symbolId, pinId)

    def __connectComponentDependencies(self, connection):
        depId, capId = connection
            
        connectTable = getAutoconnectTable(self.__atdf, depId, capId)
        # self.__log.writeInfoMessage("SHD >> __connectComponentDependencies connectTable: {}".format(connectTable)) 

        if len(connectTable) > 0:
            res = self.__db.connectDependencies(connectTable)
            if res == True:
                # detect if it is multi-instance dep
                if depId[-2] == "_":
                    self.__connections.setdefault(capId, depId[:-2])
                else:
                    self.__connections.setdefault(capId, depId)
                # self.__log.writeInfoMessage("SHD >> __connectComponentDependencies self.__connections: {}".format(self.__connections)) 
        else:
            if depId != "":
                self.__drvUnconnected.setdefault(depId, False)

    def __checkIsMultiInstanceDriver(self, driver):
        for multiInstanceDriver in shdMultiInstanceDrivers:
            if multiInstanceDriver == driver:
                return True

        return False

    def __getDriverMultiInstanceNumber(self, idActiveList, driver):
        drvInstances = []
        drvInstancesUnused = []
        for id in idActiveList:
            if driver != id and driver in id:
                drvInstances.append(id)
                
        drvInstancesUnused = list(drvInstances)
    
        for instance in drvInstances:
            for capId, depId in self.__shdDependenciesPlibMultiInstance.items():
                if instance == depId:
                    drvInstancesUnused.remove(instance)
                    break
                
        if len(drvInstancesUnused) > 0:
            return int("".join(filter(lambda x: x.isdigit(), drvInstancesUnused[0])))
        else:                
            return int(str(idActiveList).count(driver + "_"))

    def __overlapDependencies(self, dependencies, connectorName):
        # self.__log.writeInfoMessage("SHD >> __overlapDependencies {}: {}".format(connectorName, dependencies))
        newDeps = {}
        for depId, capId in dependencies.items():
            newDeps.setdefault(depId, capId)
            # self.__log.writeInfoMessage("SHD >> __overlapDependencies new dep ({},{})".format(depId, capId))
            
            # Only for dependencies from Connectors (click Boards)
            bindings = self.__depBindings.get(connectorName)
            # self.__log.writeInfoMessage("SHD >> __overlapDependencies bindings: {}".format(bindings))
            if bindings != None:
                for binding in bindings:
                    # self.__log.writeInfoMessage("SHD >> __overlapDependencies check binding: {}".format(binding))
                    if len(binding) == 1:
                        # Add only one driver without any PLIB connection
                        depId = binding[0]
                        capId = ""
                        newDeps[depId] = capId
                    elif len(binding) == 2:
                        driver, signal = binding
                        # Check if Plib supports the signal in bindings
                        if checkPlibFromSignalConnector(capId, signal) == True:
                            # Replace driver when signal = plib
                            del newDeps[depId]
                            depId = driver
                            # self.__log.writeInfoMessage("SHD >> __overlapDependencies add checkPlibFromSignalConnector:PLIB {} {}".format(depId, capId))
                            newDeps[depId] = capId
                        elif 'drvExtPhy' in signal:
                            del newDeps[depId]
                            # Replace connection for RMII
                            capId = signal
                            # self.__log.writeInfoMessage("SHD >> __overlapDependencies checkPlibFromSignalConnector:RMII {} {}".format(depId, capId))
                            if depId != "":
                                newDeps[depId] = capId

        # self.__log.writeInfoMessage("SHD >> __overlapDependencies newDeps: {}".format(newDeps))
        return newDeps

    def __configureDriverSettings(self, enabledPinIdList, disabledPinIdList):
        for pinId, pinDescr in enabledPinIdList.items():
            self.__setPLIBSettings(pinDescr, True)
            self.__setDriverSettings(pinDescr, True)
        
        for pinId, pinDescr  in disabledPinIdList.items():
            self.__setPLIBSettings(pinDescr, False)

    def __getPinListByMultiPinDriver(self, dependency):
        pinIdList = []
        for pinId in self.__configuredPins:
            params = dict()
            pinNumber = self.__devicePinMap.get(pinId)
            params.setdefault('pinNumber', pinNumber)
            params.setdefault('setting', 'function')
            ret = self.__db.sendMessage("core", "PIN_GET_CONFIG_VALUE", params)
            pinFunction = ret.get("value")
            # self.__log.writeInfoMessage("SHD >> __getPinListByMultiPinDriver {}: {} in {}".format(pinId, dependency, pinFunction))
            # Handle exceptions: MCPWM, ADCHS, ADC(dsPIC33A)
            updateList = False
            if dependency == 'mcpwm':
                if 'pwm' in pinFunction.lower():
                    updateList = True
            elif dependency == 'adchs':
                if 'an' in pinFunction.lower():
                    updateList = True
            elif dependency == 'cbg':
                if 'ibias' in pinFunction.lower() or 'isrc' in pinFunction.lower():
                    updateList = True
            elif self.__architecture == "33Axxx" and 'adc' in dependency:
                dependency = dependency.replace("adc", "ad")
                if dependency in pinFunction.lower():
                    updateList = True

            if updateList == True:
                pinIdList.append(pinId)

        return pinIdList

    def __updateDriverConnections(self, addDependency, dependencyList, connectorName):
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections[{}]: {}".format(addDependency, dependencyList))

        # Check overlap bindings
        dependencyList = self.__overlapDependencies(dependencyList, connectorName)
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections new dependencyList: {}".format(dependencyList))
        
        # Check if capability is already in use (this is needed because setReadOnly triggers callback)
        dependencyListFiltered = {}
        if addDependency == True:
            for depId, capId in dependencyList.items():
                if capId == "":
                    dependencyListFiltered.setdefault(depId, capId)
                    continue
                
                driverInstance = self.__shdDependenciesPlibMultiInstance.get(capId)
                if driverInstance != None:
                    # self.__log.writeInfoMessage("SHD >> __updateDriverConnections checking {} in {}".format(depId, driverInstance))
                    if depId in driverInstance: 
                        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections already in use ({})".format(capId))
                        continue

                dependencyListFiltered.setdefault(depId, capId)
        else:
            dependencyListFiltered = dependencyList

        # Get Active components    
        idActiveList = self.__db.getActiveComponentIDs()
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections idActiveList: {}".format(idActiveList))

        # Adapt Dependency List according to PIO peripheral ID 
        dependencyList = adaptDevicePeripheralDependencies(self.__atdf, dependencyListFiltered)
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections PIO adapted dependencyList: {}".format(dependencyList))

        newConnections = []
        newComponents = []
        multiInstanceComponent = []
        removeComponents = []
        updatePlibInstance = False
        
        for depId, capId in dependencyList.items():
            createConnection = True
            # self.__log.writeInfoMessage("SHD >> __updateDriverConnections dependencyList.items: {} {}".format(depId, capId))
            if addDependency is True:
                if self.__checkIsMultiInstanceDriver(depId) == True:
                    # self.__log.writeInfoMessage("SHD >> __updateDriverConnections __checkIsMultiInstanceDriver TRUE: {}".format(depId))
                    # Add new component/connection (multi instance)
                    newInstanceNumber = self.__getDriverMultiInstanceNumber(idActiveList, depId)
                    newDep ="{}_{}".format(depId, newInstanceNumber)
                    
                    if self.__checkComponentAvailable(capId) == True:
                        newComponents.append(capId)
                    else:
                        createConnection = False

                    if newInstanceNumber == 0:
                        if self.__checkComponentAvailable(depId) == True:
                            newComponents.append(depId)
                        else:
                            createConnection = False
                    else:
                        if newDep not in idActiveList: 
                            multiInstanceComponent.append(depId)
                    
                    if createConnection == True:
                        newConnections.append((newDep, capId))
                        
                    updatePlibInstance = True
                else:
                    # self.__log.writeInfoMessage("SHD >> __updateDriverConnections __checkIsMultiInstanceDriver FALSE: {}".format(depId))
                    if depId not in idActiveList:
                        # Add new component/connection (single instance)
                        if self.__checkComponentAvailable(depId) == True:
                            newComponents.append(depId)
                        else:
                            createConnection = False
                        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections depId NOT IN idActiveList - adding {}".format(depId))
                        
                    if capId != "" and capId not in idActiveList:
                        # Check if depId has not been previously added
                        if depId not in idActiveList:
                            # self.__log.writeInfoMessage("SHD >> __updateDriverConnections capId NOT IN idActiveList - adding {}".format(capId))
                            if self.__checkComponentAvailable(capId) == True:
                                newComponents.append(capId)
                            else:
                                createConnection = False
                            
                            if createConnection == True:
                                # self.__log.writeInfoMessage("SHD >> __updateDriverConnections adding new connection {}: {}".format(createConnection, (depId, capId)))
                                newConnections.append((depId, capId))
                            
            else:
                if capId in idActiveList:
                    # Check MultiPin drivers (driver that uses more than 1 pin)
                    pinList = self.__getPinListByMultiPinDriver(capId)
                    # self.__log.writeInfoMessage("SHD >> __updateDriverConnections MultiPinDriver 1 pinList: {}".format(pinList))
                    if len(pinList) == 0:
                        removeComponents.append(capId)

                # Handle exceptions (don't be automatically removed): PMSM_FOC,
                if depId == 'pmsm_foc':
                    continue
                  
                if depId in idActiveList:
                    if self.__checkIsMultiInstanceDriver(depId) == False:
                        # MultiInstance drivers are removed in removeComponents loop (Deactivate components)
                        # Check MultiPin drivers (driver that uses more than 1 pin)
                        pinList = self.__getPinListByMultiPinDriver(depId)
                        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections MultiPinDriver 2 pinList: {}".format(pinList))
                        if len(pinList) == 0:
                            removeComponents.append(depId)
                
        # This is needed because multiInstance components cannot be enabled with other components
        if len(multiInstanceComponent) > 0:
            self.__db.activateComponents(multiInstanceComponent)
            
        if len(newComponents) > 0:
            # self.__log.writeInfoMessage("SHD >> __updateDriverConnections newComponents: {}".format(newComponents))
            self.__db.activateComponents(newComponents)

        # Add new dependencies (Activate components)
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections newConnections: {}".format(newConnections))
        for connection in newConnections:
            self.__connectComponentDependencies(connection)
            # Update PLIB MultiInstance information
            if updatePlibInstance == True:
                depId, capId = connection
                self.__shdDependenciesPlibMultiInstance.setdefault(capId, depId)

        # Remove Components (Deactivate components)
        for component in removeComponents:
            # self.__log.writeInfoMessage("SHD >> __updateDriverConnections remove Components: {}".format(component))
            res = self.__db.deactivateComponents([component])
            if res == True:
                if self.__connections.get(component) != None:
                    del self.__connections[component]
                if self.__drvUnconnected.get(component) != None:
                    del self.__drvUnconnected[component]
                    
            # Check multiinstance driver connection
            driver = self.__shdDependenciesPlibMultiInstance.get(component)
            if driver != None:
                driverInstance = int(driver[-1])
                instancesNumber = self.__getDriverMultiInstanceNumber(idActiveList, driver[0:-2])
                # self.__log.writeInfoMessage("SHD >> __updateDriverConnections remove multiInstance: {} {} {}".format(driver, driverInstance, instancesNumber))
                if instancesNumber == 1:
                    # self.__log.writeInfoMessage("SHD >> __updateDriverConnections deactivate component 1: {}".format(driver[0:-2]))
                    self.__db.deactivateComponents([driver[0:-2]])
                elif driverInstance == (instancesNumber - 1):
                    # self.__log.writeInfoMessage("SHD >> __updateDriverConnections deactivate component 2: {}".format(driver))
                    self.__db.deactivateComponents([driver])

                del self.__shdDependenciesPlibMultiInstance[component]
                
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections self.__shdDependenciesPlibMultiInstance: {}".format(self.__shdDependenciesPlibMultiInstance))
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections self.__connections: {}".format(self.__connections))
        # self.__log.writeInfoMessage("SHD >> __updateDriverConnections self.__drvUnconnected: {}".format(self.__drvUnconnected))
        
    def __signalEnableCallback(self, symbol, event):
        dependencies = {}
        enabledPinIdList = {}
        disabledPinIdList = {}
        if self.__signalCallbackBusy == False:
            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback id: {} = {} ------------ ".format(event['id'], event['value']))
            self.__signalCallbackBusy = True

            # Get Pin Control List
            srcSymbolSplit = event["id"].split('_')
            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback srcSymbolSplit: {}".format(srcSymbolSplit))
            if "INTERFACE" in event["id"]:
                connectorName = None
                if "_OPT_" in event["id"]:
                    interfaceIndex = int(srcSymbolSplit[-3])
                    optionIndex = int(srcSymbolSplit[-1])
                    pinControlList = self.getPinControlListByInterface(interfaceIndex, optionIndex)
                    # Extract dependencies from configuration file
                    newDepList = self.__currentConfig['interfaces'][interfaceIndex]['options'][optionIndex].get('dependencies')
                    # self.__log.writeInfoMessage("SHD >> __signalEnableCallback iface_{}: opt_{}".format(interfaceIndex, optionIndex))
                else:
                    interfaceIndex = int(srcSymbolSplit[-1])
                    pinControlList = self.getPinControlListByInterface(interfaceIndex)
                    # Extract dependencies from configuration file
                    newDepList = self.__currentConfig['interfaces'][interfaceIndex].get('dependencies')
                    # self.__log.writeInfoMessage("SHD >> __signalEnableCallback iface_{}".format(interfaceIndex))

                if newDepList != None:
                    for newDep in newDepList:
                        depId = newDep[0]
                        if len(newDep) == 2:
                            capId = newDep[1]
                        else:
                            capId = ""
                        
                        dependencies.setdefault(depId, capId)
            else:
                connectorSignal = srcSymbolSplit[-1].lower()
                connectorName = srcSymbolSplit[-2].replace("-"," ")
                # self.__log.writeInfoMessage("SHD >> __signalEnableCallback {}: {}".format(connectorName, connectorSignal))
                pinControlList = self.getPinControlListByConnectorSignal(connectorName, connectorSignal)

            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback pinControlList: {}".format(pinControlList))

            for pinControl in pinControlList:
                signalId, pinCtrl = pinControl
                pinId = pinCtrl.get('pinId')
                pinName = pinCtrl.get('name')
                pinFunction = pinCtrl.get('function')
                
                pinDescr = {}
                pinDescr.setdefault(signalId, (pinId, pinFunction, pinName))
                
                # Autodetect dependencies if not found in configuration file
                autodetectDeps = True
                depId = ""
                capId = ""
                # Extract DRIVER dependencies from Pin Name
                pinName = pinCtrl.get('name')
                if pinName != None:
                    newDep = getDriverDependencyFromPin(pinName, pinFunction)
                    if (newDep != ""):
                        # self.__log.writeInfoMessage("SHD >> __signalEnableCallback newDep: {}".format((newDep)))
                        depId = newDep
                    
                # Extract PLIB capabilities from Pin Function
                if pinFunction != None and pinFunction != 'GPIO':
                    newCap = pinFunction.upper().split('_')[0].lower()
                    if ('gmac' not in newCap) and ('ethmac' not in newCap):
                        if newCap.startswith("i2s") == True:
                            # Handle exceptions: I2S
                            capId = newCap.replace("i2s", "a_i2s")
                            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback newCap 1: {}".format((capId)))
                        elif newCap != "usb":
                            # Handle exceptions: USB
                            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback newCap 2: {}".format((newCap)))
                            capId = newCap

                # GPIOs don't have dependencies, except I2C_BB
                # Extract PLIB capabilities from Pin Name (I2C_BB)
                if (pinFunction == 'GPIO'):
                    pinNameLower = pinName.lower()
                    if "i2c_bb" in pinNameLower or "_scl" in pinNameLower or "_sda" in pinNameLower:
                        capId = "i2c_bb"
                    else:
                        autodetectDeps = False

                # Not add a new dependency if capId == unused (some pins are not used in click boards)
                if capId == 'unused':
                    # self.__log.writeInfoMessage("SHD >> __signalEnableCallback skip dependency (unused): {}".format((depId, capId)))
                    autodetectDeps = False

                if autodetectDeps == True:
                    # self.__log.writeInfoMessage("SHD >> __signalEnableCallback Autodetect dependency [{},{}]".format(depId, capId))
                    # self.__log.writeInfoMessage("SHD >> __signalEnableCallback dependencies tmp: {}".format(dependencies))
                    if depId != "" or capId != "":
                        addDependency = True
                        for depIdItem, capIdItem in dependencies.items():
                            if capIdItem == capId:
                                addDependency = False
                                break;

                        if addDependency == True:
                            if depId != "":
                                capIdPrev = dependencies.get(depId)
                                if capIdPrev == None or capIdPrev == "":
                                    dependencies[depId] = capId
                            else:
                                dependencies[depId] = capId
                            
                # Set/Clear PIN configuration               
                if event["value"] is True:
                    # Check if that pin is already added                    
                    if not pinId in self.__configuredPins:
                        # self.__log.writeInfoMessage("SHD >> __signalEnableCallback set Pin {}".format(pinId))
                        self.__configuredPins.append(pinId)
                        self.__pinControlByPinId.setdefault(pinId, pinCtrl)
                        self.__setPinConfig(pinCtrl)
                        enabledPinIdList.setdefault(pinId, pinDescr)
                else:
                    # Check if that pin has to be removed
                    if pinId in self.__configuredPins:
                        # self.__log.writeInfoMessage("SHD >> __signalEnableCallback clear Pin {}".format(pinId))
                        self.__configuredPins.remove(pinId)
                        del self.__pinControlByPinId[pinId]
                        self.__clearPinConfig(pinCtrl)
                        disabledPinIdList.setdefault(pinId, pinDescr)

            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback dependencies: {}".format(dependencies))

            # Activate/Deactivate components and create connections
            self.__updateDriverConnections(event["value"], dependencies, connectorName)

            # Configure settings of the drivers of each updated PinId if needed
            self.__configureDriverSettings(enabledPinIdList, disabledPinIdList)
                
            # Check PIN Collisions
            self.__shdCheckCollisionSymbol.setValue(event["value"])

            self.__signalCallbackBusy = False
            # self.__log.writeInfoMessage("SHD >> __signalEnableCallback __configuredPins: {}".format(self.__configuredPins))

    def __getSymbolLabel(self, name, function, subSignal, pinNumber, pinId):
        if subSignal is None:
            return "{}:{}:Pin[{}]:{}".format(name, function, pinNumber, pinId)
        else:
            return "{}:{}:{}:Pin[{}]:{}".format(name, function, subSignal, pinNumber, pinId)
        
    def __updateFunctionInSymbolLabel(self, function, label):
        labelSplit = label.split(":")
        labelSplit[1] = function
        return ":".join(labelSplit)

    def __checkConnectorAdaptor(self, connectorName, clickBoardCompatible):
        # self.__log.writeInfoMessage("SHD >> __checkConnectorAdaptor: connectorName: {} - clickBoardCompatible: {}".format(connectorName, clickBoardCompatible))
        connectorCompatible = self.getCompatibleByConnectorName(connectorName)
        # self.__log.writeInfoMessage("SHD >> __checkConnectorAdaptor: connectorCompatible: {}".format(connectorCompatible))
        if connectorCompatible == 'xplainpro' and clickBoardCompatible == 'mikrobus':
            return True
        else:
            return False

    def __checkAvailableClickBoard(self, connectorName, clickBoardInterface):
        result = True
        for connector in self.__currentConfig['connectors']:
            if connector['name'] == connectorName:
                # Skip connector
                continue

            connectorSymbolName = self.getConnectorSymbolName(connector['name'])
            connectorInterface = self.__symbolConnectors.get(connectorSymbolName)
            if connectorInterface != None:
                connectorValue = connectorInterface.getValue()
                if connectorValue == clickBoardInterface.getName():
                    result = clickBoardInterface.getMulticonnection()
                    
        return result
        
    def __connectClickBoard(self, symbol, event):
        clickBoardSelection = event['value']
        connectorSymbolID = symbol.getID().replace("_DUMMY", "")
        connectorName = self.getConnectorNameFromSymbolID(connectorSymbolID)
        # self.__log.writeInfoMessage("SHD >> __connectClickBoard: connectorName: {}".format(clickBoardSelection))
        # self.__log.writeInfoMessage("SHD >> __connectClickBoard: connectorSymbolName: {}".format(connectorSymbolID))
        # self.__log.writeInfoMessage("SHD >> __connectClickBoard: connectorName: {}".format(connectorName))

        self.resetConnectorConfig(connectorName)

        if clickBoardSelection == "Select extension board":
            if self.__depBindings.get(connectorName) != None:
                del self.__depBindings[connectorName]
                del self.__connectedClickBoards[connectorName]
                self.__connectedClickBoards[connectorName] = None
                connectorAdaptorSymbol = self.__connectorAdaptorSymbols.get(connectorName)
                if connectorAdaptorSymbol != None:
                    connectorAdaptorSymbol.setVisible(False)

        else:
            clickBoardInterface = None
            for clickBoardFileName, (clickBoardName, clickBoardCompatible) in self.__clickBoardFileList.items():
                if clickBoardName == clickBoardSelection:
                    clickBoardInterface = ClickBoard(clickBoardFileName)
                    self.__connectedClickBoards.setdefault(connectorName, clickBoardInterface)
                    break

            if clickBoardInterface != None:
                # Check if multi-connection is allowed
                if self.__checkAvailableClickBoard(connectorName, clickBoardInterface) == True:
                    self.__log.writeInfoMessage("SHD >> Connect Click Board: {}".format(clickBoardInterface.getName()))
                    self.__log.writeInfoMessage("SHD >> For further information: {}".format(clickBoardInterface.getDocumentation()))

                    # Check if XplainPro to mikroBUS adapator board is needed
                    connectorAdaptorSymbol = self.__connectorAdaptorSymbols.get(connectorName)
                    useHWAdaptor = False
                    if connectorAdaptorSymbol != None:
                        if self.__checkConnectorAdaptor(connectorName, clickBoardCompatible) == True:
                            # self.__log.writeInfoMessage("SHD >> __connectClickBoard WITH ADAPTOR - {}".format(connectorAdaptorSymbol))
                            connectorAdaptorSymbol.setVisible(True)
                            useHWAdaptor = True
                            clickBoardInterface.convertFromMikroBusToXplainProBoard()
                        else:
                            # self.__log.writeInfoMessage("SHD >> __connectClickBoard WITHOUT ADAPTOR - {}".format(connectorAdaptorSymbol))
                            connectorAdaptorSymbol.setVisible(False)
                            clickBoardInterface.restoreFromXplainProToMikroBusBoard()

                    # Handle Bindings
                    bindingList = clickBoardInterface.getDependencies()
                    # self.__log.writeInfoMessage("SHD >> __connectClickBoard: bindingList - {}".format(bindingList))
                    if bindingList != None:
                        index = 0
                        rmiiConDetected = False
                        for binding in bindingList:
                            if len(binding) == 1:
                                bindingList[index] = binding
                            elif len(binding) == 2:
                                depIdCon, signalCon = binding
                                pinControlConnector = self.getPinControlByConnectorName(connectorName)
                                pinControlSignal = pinControlConnector.get(signalCon)
                                if pinControlSignal != None:
                                    pinFunction = pinControlSignal.get("function")
                                    if pinFunction == None: # this is a bus signals (usart, i2c, spi, rmii)
                                        if signalCon == 'spi':
                                            pinFunction = pinControlSignal.get("mosi").get("function")
                                        elif signalCon == 'uart':
                                            pinFunction = pinControlSignal.get("tx").get("function")
                                        elif signalCon == 'i2c':
                                            pinFunction = pinControlSignal.get("sda").get("function")
                                        elif signalCon == 'ethphy':
                                            rmiiConDetected = True
                                            pinFunction = pinControlSignal.get("txen").get("function")

                                    if pinFunction != None:
                                        pinFunction = pinFunction.upper()
                                        if pinFunction != 'GPIO':
                                            plib = pinFunction.split("_")
                                            if len(plib) > 1:
                                                plib = plib[0]
                                            # Overwrite the current element of the bindingList
                                            if rmiiConDetected == False:
                                                bindingList[index] = [depIdCon, plib.lower()]
                                            else:
                                                # RMII binding adaptation: depIdCon is the capability, PLIB includes the dependency (driver)
                                                bindingList[index] = [plib.lower(), depIdCon]
                                                
                                            # self.__log.writeInfoMessage("SHD >> __connectClickBoard added bindingList[{}]: {}".format(index, bindingList[index]))
                            index = index + 1
                            
                        self.__depBindings.setdefault(connectorName, bindingList)
                        # self.__log.writeInfoMessage("SHD >> __connectClickBoard: __setAdditionalDependencies: {}".format(self.__depBindings))

                    # Get only the active signals from ClickBoard
                    pinControlClickBoard = clickBoardInterface.getConnections()
                    # self.__log.writeInfoMessage("SHD >> __connectClickBoard: pinControlClickBoard - {}".format(pinControlClickBoard))

                    # Set connector configuration
                    self.setConnectorConfig(connectorName, pinControlClickBoard, useHWAdaptor)
         
    def __updatePinConfiguration(self, config, newConfig):
        result = config.copy()
        # self.__log.writeInfoMessage("SHD >> __updatePinConfiguration: result: {}".format(result))
        for key, value in newConfig.items():
            result[key] = value

        # self.__log.writeInfoMessage("SHD >> __updatePinConfiguration: new result: {}".format(result))
        # Check discrepancies
        if result.get('direction') == 'in' and result.get('latch') != None:
            # Remove latch since pin is an input
            del result['latch']
        elif result.get('direction') == 'out':
            if result.get('pull up') != None:
                del result['pull up']
            if result.get('pull down') != None:
                del result['pull down']
            
        return result
    
    def getName(self):
        return self.__currentConfig.get('name')
    
    def getDocumentation(self):
        return self.__currentConfig.get('documentation')

    def isPinSignal(self, pinCtrl):
        if pinCtrl.get('pinId') != None:
            return True
        else:
            return False

    def getInterfaceList(self):
        interfaceList = []
        index = 0
        for interface in self.__currentConfig['interfaces']:
            hasOptions = interface.get('options') != None
            interfaceList.append((index, interface['name'], interface['description'], hasOptions))
            index = index + 1
            
        return interfaceList

    def getOptionsList(self, interface):
        optionList = []
        index = 0
        for options in self.__currentConfig['interfaces'][interface]['options']:
            optionList.append((index, options['name'], options['description']))
            index = index + 1
            
        return optionList

    def getDescriptionListByInterface(self, interfaceIndex, optionIndex = None):
        if interfaceIndex >= len(self.__currentConfig['interfaces']):
            return None
        
        pinList = []
        if optionIndex == None:
            pinControl = self.__currentConfig['interfaces'][interfaceIndex]['pinctrl']
        else:
            pinControl = self.__currentConfig['interfaces'][interfaceIndex]['options'][optionIndex]['pinctrl']
        index = 0
        if self.isPinSignal(pinControl):
            # Single pin signal
            pinList.append((index, pinControl.get('function'), pinControl.get('pinId')))
            index = index + 1
        else:
            for key, value in pinControl.items():
                # Multi pin signal
                pinList.append((index, value.get('function'), value.get('pinId')))
                index = index + 1

        return pinList 

    def getPinControlListByInterface(self, interfaceIndex, optionIndex = None):
        if interfaceIndex >= len(self.__currentConfig['interfaces']):
            return None
        
        pinList = []
        if optionIndex == None:
            pinControl = self.__currentConfig['interfaces'][interfaceIndex]['pinctrl']
        else:
            pinControl = self.__currentConfig['interfaces'][interfaceIndex]['options'][optionIndex]['pinctrl']

        if self.isPinSignal(pinControl):
            # Single pin signal
            pinList.append(('gpio', pinControl))
        else:
            for signalID, pinCtrl in pinControl.items():
                # Multi pin signal
                pinList.append((signalID, pinCtrl))

        return pinList     
            
    def getConnectorList(self):
        connectorList = []
        index = 0
        for connector in self.__currentConfig['connectors']:
            connectorList.append((index, connector['name'], connector['description']))
            index = index + 1
            
        return connectorList  

    def getConnectorNameByIndex(self, connectorIndex):
        if connectorIndex >= len(self.__currentConfig['connectors']):
            return None

        return self.__currentConfig['connectors']['name']

    def getSignalListByConnector(self, connectorIndex):
        if connectorIndex >= len(self.__currentConfig['connectors']):
            return None
        
        signalList = []
        signalControl = self.__currentConfig['connectors'][connectorIndex]['pinctrl']
        for signal in signalControl:
            signalList.append(signal)
        
        return signalList
            
    def getSignalListByConnectorName(self, connectorName):
        signalList = []
        for connector in self.__currentConfig['connectors']:
            if connector['name'] == connectorName:
                signalControl = connector['pinctrl']
                for signal in signalControl:
                    signalList.append(signal)
                
                return signalList
        else:
            return None

    def getPinControlByConnectorName(self, connectorName):
        pinControl = []
        for connector in self.__currentConfig['connectors']:
            if connector['name'] == connectorName:
                pinControl = connector['pinctrl']
                
        return pinControl

    def getCompatibleByConnectorName(self, connectorName):
        for connector in self.__currentConfig['connectors']:
            if connector['name'] == connectorName:
                return connector['compatible']
                
        return None
            
    def getDescriptionListByConnectorSignal(self, connectorName, connectorSignal):
        pinControlList = []
        for connector in self.__currentConfig['connectors']:
            if connector['name'] == connectorName:
                signalControl = connector['pinctrl'].get(connectorSignal)
                if signalControl != None:
                    if self.isPinSignal(signalControl):
                        # Single pin signal
                        pinNumber = getConnectorPinNumberFromSignal(connector.get("compatible"), signalPin=connectorSignal)
                        data = (signalControl['name'], signalControl['function'], pinNumber, signalControl['pinId'])
                        pinControlList.append(data)
                    else:
                        for subSignal, pinControl in signalControl.items():
                            # Multi pin signal
                            pinNumber = getConnectorPinNumberFromSignal(connector.get("compatible"), signalGroup=connectorSignal, signalPin=subSignal)
                            data = (pinControl['name'], pinControl['function'], subSignal.upper(), pinNumber, pinControl['pinId'])
                            pinControlList.append(data)
                
                return pinControlList
        else:
            return None
            
    def getPinControlListByConnectorSignal(self, connectorName, connectorSignal):
        pinControlList = []
        for connector in self.__currentConfig['connectors']:
            # self.__log.writeInfoMessage("SHD >> getPinControlListByConnectorSignal: {} - {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                signalControl = connector['pinctrl'].get(connectorSignal)
                if signalControl != None:
                    if self.isPinSignal(signalControl):
                        # Single pin signal
                        pinControlList.append((connectorSignal, signalControl))
                    else:
                        for signalId, pinControl in signalControl.items():
                            # Multi pin signal
                            pinControlList.append((signalId, pinControl))
                return pinControlList
        else:
            return None

    def updatePinControlByConnector(self, connectorName, newPinControl, useHWAdaptor=False):
        for connector in self.__currentConfig['connectors']:
            # self.__log.writeInfoMessage("SHD >> SHD updatePinControlByConnector {} == {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                pinControlCurrent = connector['pinctrl']
                break

        # self.__log.writeInfoMessage("SHD >> SHD updatePinControlByConnector pinControlCurrent 1: {}".format(pinControlCurrent))
        
        # Update signal labels according to useHWAdaptor (only for xplainPro to mikroBUS)
        if useHWAdaptor == True:
            board = self.__db.getComponentByID(self.__interfaceID)
            signalsToAdapt = getConnectorSignalMapXplainProToMikroBUS()
            for xproSignal, uBusSignal in signalsToAdapt.items():
                signalSymbolID = self.getConnectorSignalSymbolName(connectorName, xproSignal)
                symbolInterface = board.getSymbolByID(signalSymbolID)
                if uBusSignal is None:
                    symbolInterface.setVisible(False)
                else:
                    symbolInterface.setLabel(uBusSignal.upper())
                        
        for signal, newConfig in newPinControl.items():
            if newConfig.get('name') != None:
                # Single Pin
                if pinControlCurrent.get(signal) != None:
                    pinControlCurrent[signal] = self.__updatePinConfiguration(pinControlCurrent[signal], newConfig)
            else:
                # Multi Pin
                for subSignal, newSubConfig in newConfig.items():
                    if pinControlCurrent.get(signal) != None and pinControlCurrent[signal][subSignal] != None:
                        pinControlCurrent[signal][subSignal] = self.__updatePinConfiguration(pinControlCurrent[signal][subSignal], newSubConfig)
                    
        # self.__log.writeInfoMessage("SHD >> SHD updatePinControlByConnector pinControlCurrent 2: {}".format(pinControlCurrent))

    def restorePinControlByConnector(self, connectorName):
        connectorIndex = 0
        for connector in self.__currentConfig['connectors']:
            # self.__log.writeInfoMessage("SHD >> restorePinControlByConnector: {} - {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                pinControlCurrent = connector['pinctrl']
                break
            else:
                connectorIndex = connectorIndex + 1

        # self.__log.writeInfoMessage("SHD >> restorePinControlByConnector: connectorIndex: {}".format(connectorIndex))
        pinControlDefault = self.__defaultConfig['connectors'][connectorIndex]['pinctrl']
        
        for signal in pinControlCurrent:
            defaultSignal = pinControlDefault.get(signal)
            if defaultSignal != None:
                pinControlCurrent[signal] = deepcopy(defaultSignal)

    def getConnectorSymbolName(self, connectorName):
        return "SHD_MAINBOARD_CONNECTOR_{}".format(connectorName.replace(" ","-"))

    def getConnectorNameFromSymbolID(self, connectorSymbolName):
        return connectorSymbolName.split("_")[3].replace("-", " ")

    def getConnectorSignalSymbolName(self, connectorName, signalName):
        connectorSymbolName = self.getConnectorSymbolName(connectorName)
        return "{}_{}".format(connectorSymbolName, signalName.upper())

    def getConnectorSignalPinSymbolName(self, connectorName, signalName, pinId):
        connectorSignalName = self.getConnectorSignalSymbolName(connectorName, signalName)
        return "{}_{}".format(connectorSignalName, pinId.upper())

    def setConnectorConfig(self, connectorName, pinCtrl, useHWAdaptor):
        # self.__log.writeInfoMessage("SHD >> SHD setConnectorConfig connectorName: {}, pinCtrl: {}".format(connectorName, pinCtrl))
        board = self.__db.getComponentByID(self.__interfaceID)
        
        # Update Pin Control of the Main Board by Connector
        self.updatePinControlByConnector(connectorName, pinCtrl, useHWAdaptor)

        # Update Configuration Options by Connector
        signalList = self.getSignalListByConnectorName(connectorName)
        signalList.sort(reverse=True)
        # self.__log.writeInfoMessage("SHD >> setConnectorConfig signalList: {}".format(signalList))
        for signal in signalList:
            # Enable/Disable signals
            connectorSignalName = self.getConnectorSignalSymbolName(connectorName, signal)
            signalSymbol = board.getSymbolByID(connectorSignalName)
            if pinCtrl.get(signal) != None:
                pinDescriptionList = self.getDescriptionListByConnectorSignal(connectorName, signal)
                # self.__log.writeInfoMessage("SHD >> setConnectorConfig pinDescriptionList: {}".format(pinDescriptionList))
                # Update Symbol label
                for pinDescription in pinDescriptionList:
                    if len(pinDescription) == 4:
                        name, function, pinNumber, pinId = pinDescription
                        label = self.__getSymbolLabel(name, function, None, pinNumber, pinId)
                    else:
                        name, function, subSignal, pinNumber, pinId = pinDescription
                        label = self.__getSymbolLabel(name, function, subSignal, pinNumber, pinId)
                        # Handle SPI CS exception (configuration option is not allowed)
                        if subSignal.lower() == 'cs' and function.lower() is not "unused":
                            # self.__log.writeInfoMessage("SHD >> Handle SPI CS exception - subSignal: {}".format(subSignal.lower())) 
                            symbolName = self.__symbolNamesByConnector[connectorName][pinId][signal]
                            shdSpiCSConfigSymbolName = "{}_{}".format(symbolName, "CSASGPIO")
                            signalSpiCsPinSymbol = self.__symbolInterfaces.get(shdSpiCSConfigSymbolName)
                            if signalSpiCsPinSymbol is not None:
                                signalSpiCsPinSymbol.setVisible(True)
                                if function.lower() == "gpio":
                                    signalSpiCsPinSymbol.setValue(True)

                    signalPinSymbol = board.getSymbolByID(self.__symbolNamesByConnector[connectorName][pinId][signal])
                    signalPinSymbol.setLabel(label)
                    
                # self.__log.writeInfoMessage("SHD >> setConnectorConfig Enable symbol: {}".format(connectorSignalName))
                signalSymbol.setValue(True)

    def resetConnectorConfig(self, connectorName):
        # self.__log.writeInfoMessage("SHD >> SHD restoreConnections connectorName: {}".format(connectorName))
        board = self.__db.getComponentByID(self.__interfaceID)
        
        # Restore Pin Control by default of the Main Board by Connector
        self.restorePinControlByConnector(connectorName)

        # Update Configuration Options by Connector
        signalList = self.getSignalListByConnectorName(connectorName)
        for signal in signalList:
            connectorSignalName = self.getConnectorSignalSymbolName(connectorName, signal)
            signalSymbol = board.getSymbolByID(connectorSignalName)
            signalSymbol.clearValue()
            # signalSymbol.setReadOnly(False)
            signalSymbol.setVisible(True)
            signalSymbol.setLabel(signal.upper())
            # Update Symbol label
            pinDescriptionList = self.getDescriptionListByConnectorSignal(connectorName, signal)
            # self.__log.writeInfoMessage("SHD >> SHD restoreConnections connectorName: {} signal: {}".format(connectorName, signal))
            for pinDescription in pinDescriptionList:
                if len(pinDescription) == 4:
                    name, function, pinNumber, pinId = pinDescription
                    label = self.__getSymbolLabel(name, function, None, pinNumber, pinId)
                    symbolID = self.__symbolNamesByConnector[connectorName][pinId][signal]
                    # self.__log.writeInfoMessage("SHD >> SHD restoreConnections symbolID 1: {}".format(symbolID))
                else:
                    name, function, subSignal, pinNumber, pinId = pinDescription
                    # self.__log.writeInfoMessage("SHD >> SHD pinDescription: {}".format(pinDescription))
                    label = self.__getSymbolLabel(name, function, subSignal, pinNumber, pinId)
                    symbolID = self.__symbolNamesByConnector[connectorName][pinId][signal]
                    # self.__log.writeInfoMessage("SHD >> SHD restoreConnections symbolID 2: {}".format(symbolID))
                    # Handle SPI CS exception (configuration option is not allowed)
                    if subSignal.lower() == 'cs' and function != "GPIO":
                        symbolName = self.__symbolNamesByConnector[connectorName][pinId][signal]
                        shdSpiCSConfigSymbolName = "{}_{}".format(symbolName, "CSASGPIO")
                        signalSpiCsPinSymbol = self.__symbolInterfaces.get(shdSpiCSConfigSymbolName)
                        if signalSpiCsPinSymbol is not None:
                            signalSpiCsPinSymbol.setVisible(True)

                signalPinSymbol = board.getSymbolByID(self.__symbolNamesByConnector[connectorName][pinId][signal])
                signalPinSymbol.setLabel(label)

    def handleMessage(self, id, args):
        retDict = {}
        # self.__log.writeInfoMessage("SHD >> mainBoard handleMessage: {} args: {}".format(id, args))
        if (id == "CONNECTOR_SET_CONFIGURATION"):
            for connectorName, pinCtrl in args.items():
                self.setConnectorConfig(connectorName, pinCtrl)
                retDict= {"Return": "Success"}
                
        elif (id == "CONNECTOR_CLEAR_CONFIGURATION"):
            for connectorName, pinCtrl in args.items():
                self.resetConnectorConfig(connectorName)
                retDict= {"Return": "Success"}
                
        elif (id == "GET_CONNECTOR_LIST"):
            # args : {}
            retDict= {"Return": self.getConnectorList()}
                
        elif (id == "GET_CONNECTOR_CONFIGURATION"):
            # args : {'connector' : connectorName}
            connectorName = args['connector']
            retDict= {"Return": self.getPinControlByConnectorName(connectorName)}
                
        else:
            retDict= {"Return": "MainBoard UnImplemented Command"}
        
        return retDict

    def createConfigurationSymbols(self, boardInterface):
        self.__log.writeInfoMessage("SHD >> Loading SHD Board: {}".format(self.getName()))
        self.__log.writeInfoMessage("SHD >> For further information: {}".format(self.getDocumentation()))

        self.__db.activateComponents(["HarmonyCore"])

        self.__shdCheckCollisionSymbol = boardInterface.createBooleanSymbol("SHD_CHECK_COLLISIONS", None)
        self.__shdCheckCollisionSymbol.setLabel("")
        self.__shdCheckCollisionSymbol.setVisible(False)
        self.__shdCheckCollisionSymbol.setDependencies(self.__checkGlobalCollisions, ["SHD_CHECK_COLLISIONS"])
        
        symbol = boardInterface.createStringSymbol("SHD_MAINBOARD_NAME", None)
        symbol.setLabel("Board Name")
        symbol.setDefaultValue(self.__currentConfig.get('name'))
        symbol.setReadOnly(True)
        symbol.setVisible(False)
        symbol.setHelp(shdMainBoardHelp)

        self.__pioPeripheralID = getDeviceGPIOPeripheral(self.__atdf)
        symbol = boardInterface.createStringSymbol("SHD_MAINBOARD_PIO_PERIPH", None)
        symbol.setLabel("PIO Peripheral")
        symbol.setDefaultValue(self.__pioPeripheralID)
        symbol.setReadOnly(True)
        symbol.setVisible(False)
        symbol.setHelp(shdMainBoardHelp)
        
        # SETTING DEFINITIONS -------------------------------------------------
        boardSettings = self.__currentConfig.get('settings')
        if boardSettings != None:
            shdSettingsMenu = boardInterface.createMenuSymbol("SHD_MAINBOARD_SETTINGS", None)
            shdSettingsMenu.setLabel("Board Settings")
            shdSettingsMenu.setDescription("List of Board Settings")
            shdSettingsMenu.setHelp(shdMainBoardHelp)
            
            keySettingIndex = 0
            pinSettingIndex = 0
            intSettingIndex = 0
            strSettingIndex = 0
            for setting in boardSettings:
                settingType = setting['type']
                if settingType == 'integer':
                    symbolName = "SHD_MAINBOARD_SETTINGS_INT_{}_{}".format(intSettingIndex, setting['name'].replace(" ", ":"))
                    settingSymbol = boardInterface.createIntegerSymbol(symbolName, shdSettingsMenu)
                    settingSymbol.setLabel(setting['name'])
                    settingSymbol.setDescription(setting['description'])
                    settingSymbol.setDefaultValue(int(setting['value']))

                    intSettingIndex = intSettingIndex + 1
                    
                elif settingType == 'string':
                    symbolName = "SHD_MAINBOARD_SETTINGS_STR_{}_{}".format(strSettingIndex, setting['name'].replace(" ", ":"))
                    settingSymbol = boardInterface.createStringSymbol(symbolName, shdSettingsMenu)
                    settingSymbol.setLabel(setting['name'])
                    settingSymbol.setDescription(setting['description'])
                    settingSymbol.setDefaultValue(str(setting['value']))

                    strSettingIndex = strSettingIndex + 1
                    
                elif settingType == 'keyValue':
                    symbolName = "SHD_MAINBOARD_SETTINGS_KEY_{}_{}".format(keySettingIndex, setting['name'].replace(" ", ":"))
                    settingSymbol = boardInterface.createKeyValueSetSymbol(symbolName, shdSettingsMenu)
                    settingSymbol.setLabel(setting['name'])
                    settingSymbol.setDescription(setting['description'])
                    settingSymbol.setDefaultValue(0)
                    settingSymbol.setOutputMode("Key")
                    settingSymbol.setDisplayMode("Description")
                    settingSymbol.setHelp(shdMainBoardHelp)
                    # Add key values
                    for keyValue in setting['keyValues']:
                        settingSymbol.addKey(keyValue['key'], "0", keyValue['description'])

                    keySettingIndex = keySettingIndex + 1
                    
                elif settingType == 'pinSelect':
                    settingSymbolName = "SHD_MAINBOARD_SETTINGS_PIN_{}".format(pinSettingIndex)
                    settingSymbol = boardInterface.createKeyValueSetSymbol(settingSymbolName, shdSettingsMenu)
                    settingSymbol.setLabel(setting['name'])
                    settingSymbol.setDefaultValue(0)
                    settingSymbol.setOutputMode("Value")
                    settingSymbol.setDisplayMode("Description")
                    settingSymbol.setHelp(shdMainBoardHelp)
                    self.__symbolInterfaces.setdefault(settingSymbolName, settingSymbol)
                    # Add key values
                    pinValueIndex = 0
                    for pinValue in setting['pinValues']:
                        settingSymbol.addKey(pinValue['name'], str(pinValueIndex), pinValue['description'])

                        pinCtrl = pinValue.get('pinctrl')
                        if pinCtrl != None:
                            pinSymbolName = "{}_{}".format(settingSymbolName, pinValueIndex)
                            pinSettingSymbol = boardInterface.createCommentSymbol(pinSymbolName, settingSymbol)
                            pinSettingSymbol.setLabel(pinCtrl['function'].upper() + ": " + pinCtrl['pinId'].upper())
                            pinSettingSymbol.setVisible(pinValueIndex == 0)
                            pinSettingSymbol.setDependencies(self.__showSettingSymbol, [settingSymbolName])
                            # Activar la configuracion del PIN (pinctrl)

                        pinValueIndex = pinValueIndex + 1
                        
                    pinSettingIndex = pinSettingIndex + 1

                # else:

        # INTERFACE DEFINITIONS -----------------------------------------------
        boardInterfaces = self.__currentConfig.get('interfaces')
        # self.__log.writeInfoMessage("SHD >> boardInterfaces: {}".format(boardInterfaces))
        if boardInterfaces != None:
            shdInterfaceList = boardInterface.createMenuSymbol("SHD_MAINBOARD_INTERFACES", None)
            shdInterfaceList.setLabel("Interfaces")
            shdInterfaceList.setDescription("List of interfaces")
            shdInterfaceList.setVisible(False)
            shdInterfaceList.setHelp(shdMainBoardHelp)

            interfaceDependencies = []
            interfaceList = self.getInterfaceList()
            interfaceIndex = 0
            for interface in self.__currentConfig.get('interfaces'):
                # self.__log.writeInfoMessage("SHD >> boardInterfaces interface: {}".format(interface))
                hasOptions = interface.get('options') != None
                if hasOptions:
                    interfaceName = "SHD_MAINBOARD_INTERFACE_{}".format(interfaceIndex)
                    shdInterfaceGroup = boardInterface.createMenuSymbol(interfaceName, None)
                    shdInterfaceGroup.setLabel(interface.get('name'))
                    shdInterfaceGroup.setDescription(interface.get('description'))
                    shdInterfaceGroup.setHelp(shdMainBoardHelp)

                    optionIndex = 0
                    for option in self.__currentConfig['interfaces'][interfaceIndex]['options']:
                        optionSymbolName = "SHD_MAINBOARD_INTERFACE_{}_OPT_{}".format(interfaceIndex, optionIndex)
                        symbol = boardInterface.createBooleanSymbol(optionSymbolName, shdInterfaceGroup)
                        symbol.setLabel(option.get('name'))
                        symbol.setDescription(option.get('description'))
                        symbol.setDefaultValue(False)
                        symbol.setHelp(shdMainBoardHelp)
                        self.__symbolInterfaces.setdefault(optionSymbolName, symbol)

                        warnComment = option.get('warning')
                        if warnComment is not None:
                            warnSymbolName = "{}_WARN".format(optionSymbolName)
                            warnSymbol = boardInterface.createCommentSymbol(warnSymbolName, symbol)
                            warnSymbol.setLabel("WARNING!! {}".format(warnComment))
                            warnSymbol.setVisible(False)
                            warnSymbol.setDependencies(self.__showSymbol, [optionSymbolName])

                        pinControlList = self.getDescriptionListByInterface(interfaceIndex, optionIndex)
                        # self.__log.writeInfoMessage("SHD >> option pinControlList: {}".format(pinControlList))
                        for pinControl in pinControlList:
                            # self.__log.writeInfoMessage("SHD >> option pinControl: {}".format(pinControl))
                            pinControlIndex, function, pinId = pinControl
                            symbolName = "{}_{}_{}".format(optionSymbolName, pinControlIndex, pinId)
                            shdConfigComment = boardInterface.createCommentSymbol(symbolName, symbol)
                            shdConfigComment.setLabel(function.upper() + ": " + pinId.upper())
                            shdConfigComment.setVisible(False)
                            shdConfigComment.setDependencies(self.__showSymbol, [optionSymbolName])

                            if self.__symbolPinByParent.get(optionSymbolName) != None:
                                self.__symbolPinByParent[optionSymbolName].append(symbolName)
                            else:
                                self.__symbolPinByParent.setdefault(optionSymbolName, [symbolName])

                            if self.__symbolInterfaceByPin.get(pinId) != None:
                                self.__symbolInterfaceByPin[pinId].append(optionSymbolName)
                            else:
                                self.__symbolInterfaceByPin.setdefault(pinId, [optionSymbolName])
                        
                        interfaceDependencies.append(optionSymbolName)

                        optionIndex = optionIndex + 1
                        
                else:
                    interfaceSymbolName = "SHD_MAINBOARD_INTERFACE_{}".format(interfaceIndex)
                    symbol = boardInterface.createBooleanSymbol(interfaceSymbolName, None)
                    symbol.setLabel(interface.get('name'))
                    symbol.setDescription(interface.get('description'))
                    symbol.setDefaultValue(False)
                    symbol.setHelp(shdMainBoardHelp)
                    self.__symbolInterfaces.setdefault(interfaceSymbolName, symbol)

                    warnComment = interface.get('warning')
                    if warnComment is not None:
                        warnSymbolName = "{}_WARN".format(interfaceSymbolName)
                        warnSymbol = boardInterface.createCommentSymbol(warnSymbolName, symbol)
                        warnSymbol.setLabel("WARNING!! {}".format(warnComment))
                        warnSymbol.setVisible(False)
                        warnSymbol.setDependencies(self.__showSymbol, [interfaceSymbolName])

                    pinControlList = self.getDescriptionListByInterface(interfaceIndex)
                    # self.__log.writeInfoMessage("SHD >> pinControlList: {}".format(pinControlList))
                    for pinControl in pinControlList:
                        # self.__log.writeInfoMessage("SHD >> pinControl: {}".format(pinControl))
                        pinControlIndex, function, pinId = pinControl
                        symbolName = "{}_{}_{}".format(interfaceSymbolName, pinControlIndex, pinId)
                        shdConfigComment = boardInterface.createCommentSymbol(symbolName, symbol)
                        shdConfigComment.setLabel(function.upper() + ": " + pinId.upper())
                        shdConfigComment.setVisible(False)
                        shdConfigComment.setDependencies(self.__showSymbol, [interfaceSymbolName])

                        if self.__symbolPinByParent.get(interfaceSymbolName) != None:
                            self.__symbolPinByParent[interfaceSymbolName].append(symbolName)
                        else:
                            self.__symbolPinByParent.setdefault(interfaceSymbolName, [symbolName])

                        if self.__symbolInterfaceByPin.get(pinId) != None:
                            self.__symbolInterfaceByPin[pinId].append(interfaceSymbolName)
                        else:
                            self.__symbolInterfaceByPin.setdefault(pinId, [interfaceSymbolName])
                            
                    interfaceDependencies.append(interfaceSymbolName)

                interfaceIndex = interfaceIndex + 1
                
            shdInterfaceList.setDependencies(self.__signalEnableCallback, interfaceDependencies)
            # self.__log.writeInfoMessage("SHD >> interfaceDependencies: {}".format(interfaceDependencies))
            
            # Add collision data
            self.__collisionsByPinID = deepcopy(self.__symbolInterfaceByPin)
                
        # EXTERNAL CONNECTORS DEFINITIONS -------------------------------------
        boardConnectors = self.__currentConfig.get('connectors')
        if boardConnectors != None:
            # self.__log.writeInfoMessage("SHD >> createMenuSymbol: SHD_MAINBOARD_CONNECTORS")
            shdConnectorList = boardInterface.createMenuSymbol("SHD_MAINBOARD_CONNECTORS", None)
            shdConnectorList.setLabel("External Connectors")
            shdConnectorList.setDescription("List of external connectors")
            shdConnectorList.setVisible(True)
            shdConnectorList.setHelp(shdMainBoardHelp)

            boardConnectorList = self.getConnectorList()
            for connector in boardConnectorList:
                connectorDependencies = []
                symbolNamesByPinId = dict()
                conIndex, conName, conDescription = connector

                # Filter clickBoard list by compatible data
                clickBoardList = []
                for clickBoardBaseName, (clickBoardName, clickBoardCompatible) in self.__clickBoardFileList.items():
                    addClickBoard = False
                    boardConnCompatible = boardConnectors[conIndex].get('compatible')
                    # clickBoardCompatible = interface.getConnectorCompatible()
                    if boardConnCompatible == clickBoardCompatible:
                        addClickBoard = True
                    # elif boardConnCompatible == 'mikrobus' and clickBoardCompatible == 'xplainpro':
                    #     addClickBoard = True
                    elif boardConnCompatible == 'xplainpro' and clickBoardCompatible == 'mikrobus':
                        addClickBoard = True

                    if addClickBoard == True:
                        clickBoardList.append(clickBoardName)
                
                if len(clickBoardList) == 0:
                    clickBoardList = ['No extension board available']
                else:
                    clickBoardList.sort()
                
                clickBoardSelection = ['Select extension board'] + clickBoardList
                
                connectorSymbolName = self.getConnectorSymbolName(conName)
                # self.__log.writeInfoMessage("SHD >> createMenuSymbol: {}".format(connectorSymbolName))
                shdConnectorSymbol = boardInterface.createComboSymbol(connectorSymbolName, shdConnectorList, clickBoardSelection)
                shdConnectorSymbol.setLabel(conName)            
                shdConnectorSymbol.setDefaultValue(clickBoardSelection[0])
                shdConnectorSymbol.setDescription(conDescription)
                shdConnectorSymbol.setVisible(True)
                if len(clickBoardSelection) == 1:
                    shdConnectorSymbol.setReadOnly(True)
                shdConnectorSymbol.setHelp(shdMainBoardHelp)
                self.__symbolConnectors.setdefault(connectorSymbolName, shdConnectorSymbol)

                if boardConnectors[conIndex].get('compatible') == 'xplainpro':
                    shdConnectorSymbolAdaptor = boardInterface.createCommentSymbol(connectorSymbolName + "_ADAPTOR", shdConnectorSymbol)
                    shdConnectorSymbolAdaptor.setLabel("Warning!! This connection requires an ATMBUSADAPTER-XPRO adapter board")
                    shdConnectorSymbolAdaptor.setVisible(False)
                    self.__connectorAdaptorSymbols.setdefault(conName, shdConnectorSymbolAdaptor)

                shdConnectorSymbolDummy = boardInterface.createMenuSymbol(connectorSymbolName + "_DUMMY", shdConnectorList)
                shdConnectorSymbolDummy.setLabel("")
                shdConnectorSymbolDummy.setVisible(False)
                shdConnectorSymbolDummy.setDependencies(self.__connectClickBoard, [connectorSymbolName])

                signalList = self.getSignalListByConnector(conIndex)
                for signal in signalList:
                    connectorSignalName = self.getConnectorSignalSymbolName(conName, signal)
                    # self.__log.writeInfoMessage("SHD >> createBooleanSymbol: {}".format(connectorSignalName))
                    shdConSignalSymbol = boardInterface.createBooleanSymbol(connectorSignalName, shdConnectorSymbol)
                    shdConSignalSymbol.setLabel(signal.upper())
                    shdConSignalSymbol.setDescription("Enable {} : {}".format(conName, signal.upper()))
                    shdConSignalSymbol.setDefaultValue(False)
                    shdConSignalSymbol.setHelp(shdMainBoardHelp)
                    self.__symbolInterfaces.setdefault(connectorSignalName, shdConSignalSymbol)
                    
                    pinDescriptionList = self.getDescriptionListByConnectorSignal(conName, signal)
                    for pinDescription in pinDescriptionList:
                        # self.__log.writeInfoMessage("SHD >> pinDescription: {}".format(pinDescription))
                        spiCSdetected = False
                        # Check if single signal or signal group
                        if len(pinDescription) == 4:
                            name, function, pinNumber, pinId = pinDescription
                            label = self.__getSymbolLabel(name, function, None, pinNumber, pinId)
                        else:
                            name, function, subSignal, pinNumber, pinId = pinDescription
                            label = self.__getSymbolLabel(name, function, subSignal, pinNumber, pinId)
                            if subSignal.lower() == 'cs' and function != "GPIO":
                                # Defined as peripheral CS, but it can be configured as GPIO.
                                # self.__log.writeInfoMessage("SHD >> Handle SPI CS exception: {} {} {} {} {}".format(name, function, subSignal, pinNumber, pinId))
                                # Handle SPI CS exception
                                spiCSdetected = True
                            
                        shdConPinControlSymbolName = self.getConnectorSignalPinSymbolName(conName, signal, pinId)
                        # Store the Symbol name to be used in click Boards connection events
                        listSymbolId = symbolNamesByPinId.get(pinId)
                        if listSymbolId == None:
                            symbolNamesByPinId.setdefault(pinId, {signal:shdConPinControlSymbolName})
                        else:
                            symbolNamesByPinId[pinId][signal] = shdConPinControlSymbolName

                        # self.__log.writeInfoMessage("SHD >> symbolNamesByPinId: {}".format(symbolNamesByPinId))

                        # self.__log.writeInfoMessage("SHD >> conPinControlName: ", conPinControlName)
                        # self.__log.writeInfoMessage("SHD >> createCommentSymbol: {}".format(shdConPinControlSymbolName))
                        shdConPinControlSymbol = boardInterface.createCommentSymbol(shdConPinControlSymbolName, shdConSignalSymbol)
                        shdConPinControlSymbol.setLabel(label)
                        shdConPinControlSymbol.setVisible(False)
                        shdConPinControlSymbol.setHelp(shdMainBoardHelp)

                        if self.__symbolPinByParent.get(connectorSignalName) != None:
                            self.__symbolPinByParent[connectorSignalName].append(shdConPinControlSymbolName)
                        else:
                            self.__symbolPinByParent.setdefault(connectorSignalName, [shdConPinControlSymbolName])

                        # Add collision data
                        if self.__collisionsByPinID.get(pinId) != None:
                            if connectorSignalName not in self.__collisionsByPinID[pinId]:
                                self.__collisionsByPinID[pinId].append(connectorSignalName)
                        else:
                            self.__collisionsByPinID.setdefault(pinId, [connectorSignalName])

                        # Check SPI CS exception. It could be handled as GPIO. Add configuration option.
                        if spiCSdetected == True:
                            shdSpiCSConfigSymbolName = "{}_{}".format(shdConPinControlSymbolName, "CSASGPIO")
                            # self.__log.writeInfoMessage("SHD >> createBooleanSymbol: {}".format(shdSpiCSConfigSymbolName))
                            shdSpiCSConfigSymbol = boardInterface.createBooleanSymbol(shdSpiCSConfigSymbolName, shdConPinControlSymbol)
                            shdSpiCSConfigSymbol.setLabel("Drive CS signal as GPIO")
                            shdSpiCSConfigSymbol.setDescription("Drive CS signal as GPIO")
                            shdSpiCSConfigSymbol.setDefaultValue(False)
                            shdSpiCSConfigSymbol.setHelp(shdMainBoardHelp)
                            self.__symbolInterfaces.setdefault(shdSpiCSConfigSymbolName, shdSpiCSConfigSymbol)

                            # self.__log.writeInfoMessage("SHD >> spiCSdetected connectorSignalName: {} shdSpiCSConfigSymbolName: {}".format(connectorSignalName, shdSpiCSConfigSymbolName))
                            shdConPinControlSymbol.setDependencies(self.__showSymbol, [connectorSignalName, shdSpiCSConfigSymbolName])

                        else:
                            shdConPinControlSymbol.setDependencies(self.__showSymbol, [connectorSignalName])
                            
                    connectorDependencies.append(connectorSignalName)
                    
                self.__symbolNamesByConnector.setdefault(conName, symbolNamesByPinId)
                shdConnectorSymbol.setDependencies(self.__signalEnableCallback, connectorDependencies)
                # self.__log.writeInfoMessage("SHD >> connectorDependencies: {}".format(connectorDependencies))

        # remove no collision data
        for key, value in self.__collisionsByPinID.items():
            if len(value) == 1:
                self.__collisionsByPinID.pop(key, value)

        # for key, symbolList in self.__symbolInterfaceByPin.items():
        #     self.__log.writeInfoMessage("SHD >> self.__symbolInterfaceByPin: {}: {}".format(key, symbolList))

        # for key, value in self.__symbolNamesByConnector.items():
        #     self.__log.writeInfoMessage("SHD >> self.__symbolNamesByConnector: {}: {}".format(key, value))

        # for key, value in self.__collisionsByPinID.items():
        #     self.__log.writeInfoMessage("SHD >> self.__collisionsByPinID: {}: {}".format(key, value))

        # for key, value in self.__symbolPinByParent.items():
        #     self.__log.writeInfoMessage("SHD >> self.__symbolPinByParent: {}: {}".format(key, value))

    def resetSignalConfiguration(self):
        # self.__log.writeInfoMessage("SHD >> resetSignalConfiguration: {}".format(self.__configuredPins))
        for pinId in self.__configuredPins:
            pinControl = self.__pinControlByPinId.get(pinId)
            if pinControl != None:
                self.__clearPinConfig(pinControl) 