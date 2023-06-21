import sys
from os import path
from copy import deepcopy
from utils.connectorSpec import getConnectorPinNumberFromSignal, getAutoconnectTable, getDriverDependencyFromPinName
from utils.deviceSpec import getDeviceFunctionListByPinId, getDevicePinMap, getDeviceGPIOPeripheral, getDeviceDriverConfigurationDBMessage
from clickBoard.clickBoard import ClickBoard

shdMainBoardHelp = 'shdMainBoardHelpKeyword'

shdMultiInstanceDrivers = ['drv_i2c', 'drv_spi', 'drv_usart', 'drv_sdmmc', 'a_drv_i2s', 'drv_sdspi']

shdCheckCollisionSymbol = None

class MainBoard:
    def __init__(self, yamlFileName, Database, ATDF):
        self.__currentConfig = {}
        for item in sys.path:
            if "shd\\boards" in item:
                boardYamlFile = path.join(item, yamlFileName)
                
            if "shd\\clickBoards" in item:
                clickBoardsFile = path.join(item, 'clickBoards.yml')

        if not path.isfile(boardYamlFile):
            return None

        self.__db = Database
        self.__atdf = ATDF
        self.__symbolNamesByInterface = {}
        self.__symbolNamesByConnector = {}
        self.__symbolPinByParent = {}
        self.__collisionsByPinID = {}
        self.__devicePinMap = getDevicePinMap(self.__db, ATDF)
        self.__configuredPins = []
        self.__symbolInterfaces = {}
        self.__pinCallbackBusy = False
        self.__depBindings = {}
        self.__shdDependenciesPlibMultiInstance = {}

        # print("CHRIS dbg >> __devicePinMap: {}".format(self.__devicePinMap))
        
        import yaml
        with open(boardYamlFile, 'r') as file:
            self.__defaultConfig = yaml.safe_load(file)
            self.__currentConfig = deepcopy(self.__defaultConfig)
            self.__interfaceID = "mainBoard_" + self.__defaultConfig['config'].split(".")[0].upper() 

        with open(clickBoardsFile, 'r') as file:
            clickBoardList = yaml.safe_load(file)

        # print("CHRIS dbg >> clickBoardList: {}".format(clickBoardList))

        self.__clickBoards = {}
        for clickBoard in clickBoardList:
            interface = ClickBoard(clickBoard)
            boardName = interface.getName()
            self.__clickBoards.setdefault(boardName, interface)

    def __str__(self):
        return "{}".format(self.__currentConfig)
        
    def __setDriverSettings(self, functionValue, nameValue, value):
        idActiveList = self.__db.getActiveComponentIDs()
        settings = (functionValue, nameValue, value)
        # print("CHRIS dbg >> __setDriverSettings : {}".format(settings))
        componentID, messageID, params = getDeviceDriverConfigurationDBMessage(self.__atdf, settings)
        if messageID != None and componentID in idActiveList:
            self.__db.sendMessage(componentID, messageID, params)
        #     print("CHRIS dbg >> __setDriverSettings dbMsg : {}, {}, {}".format(componentID, messageID, params))
        # else:
        #     print("CHRIS dbg >> __setDriverSettings : {} is not in the Active List {}".format(componentID, idActiveList))
        
    def __clearPinConfig(self, pinControl):
        # print("CHRIS dbg >> __clearPinConfig pinControl: {}".format(pinControl))
        pinNumber = self.__devicePinMap.get(pinControl.get('pinId'))

        for key, value in pinControl.items():
            if key == 'pinId':
                continue
            
            params = dict()
            params.setdefault('pinNumber', pinNumber)
            params.setdefault('setting', key)
            # print("CHRIS dbg >> send Message PIN_CLEAR_CONFIG_VALUE : {}".format(params))
            self.__db.sendMessage("core", "PIN_CLEAR_CONFIG_VALUE", params)

            if key == 'function':
                functionValue = value

            if key == 'name':
                nameValue = value

    def __handleFunctionPioManager(self, pinCtrlFunction, functionByPinId):
        print("CHRIS dbg: __handleFunctionPioManager {} : {}".format(pinCtrlFunction, functionByPinId))
        if 'MCSPI' in pinCtrlFunction:
            functionValues = functionByPinId.split('/')
            print("CHRIS dbg: __handleFunctionPioManager {}".format(functionValues))
            for function in functionValues:
                if pinCtrlFunction in function:
                    return function
            
        if pinCtrlFunction in functionByPinId:
            return functionByPinId

        return None

    def __setPinConfig(self, pinControl):
        # print("CHRIS dbg >> __setPinConfig pinControl: {}".format(pinControl))
        pinId = pinControl.get('pinId')
        pinNumber = self.__devicePinMap.get(pinId)

        # Get function values list from the pinNumber
        functionList = getDeviceFunctionListByPinId(self.__atdf, pinId)
        # print("CHRIS dbg: functionList {}".format(functionList))

        # Sort dictionary by key to set function as first setting
        sortedKeys = sorted(pinControl.keys())
        sortedPinControl = {key:pinControl[key] for key in sortedKeys}
        findFunction = False

        for key, value in sortedPinControl.items():
            if key == 'pinId':
                continue
            
            if key == 'function':
                for functionIndex in range(len(functionList)):
                    newValue = self.__handleFunctionPioManager(value, functionList[functionIndex])
                    if newValue != None:
                        value = newValue
                        findFunction = True
                        break
                    
                if findFunction == False:
                    print("SHD mainBoard: Error in function setting of pinId: {} - function: {}".format(pinId, value))
                    print("SHD mainBoard: Match function setting with one of these values: {}".format(functionList))
                    continue
                        
            if key in ['function', 'name', 'pinId']:
                value = value.upper()
            elif type(value).__name__ == 'bool':
                if key in ['pull up', 'pull down', 'open drain']:
                    value = "True" if value else "False"
            else:
                value = value.title()
                
            # Don't set any value in case of direction: input
            if key == 'direction' and value == 'In':
                continue

            params = dict()
            params.setdefault('pinNumber', pinNumber)
            params.setdefault('setting', key)
            params.setdefault('value', value)
            print("CHRIS dbg >> send Message PIN_SET_CONFIG_VALUE : {}".format(params))
            self.__db.sendMessage("core", "PIN_SET_CONFIG_VALUE", params)

            if key == 'function':
                functionValue = value

            if key == 'name':
                nameValue = value
              
    def __checkPinIsConfigured(self, pinId):
        params = dict()
        pinNumber = self.__devicePinMap.get(pinId)
        params.setdefault('pinNumber', pinNumber)
        params.setdefault('setting', 'function')
        retDict = self.__db.sendMessage("core", "PIN_GET_CONFIG_VALUE", params)
        functionValue = retDict.get('value')
        # print("CHRIS dbg >> __checkPinIsConfigured {} : {}".format(pinId, functionValue))
        if functionValue == "":
            return False
        else:
            return True
    
    def __showSymbol(self, symbol, event):
        eventSymbolID = event['id']
        eventValue = event['value']
        # print("CHRIS dbg >> __showSymbol eventSymbolID: {} - {}".format(eventSymbolID, eventValue))
        if "CSASGPIO" in eventSymbolID:
            # print("CHRIS dbg >> __showSymbol eventSymbolID: {}".format(eventSymbolID))
            global mainBoard
            connectorName = self.getConnectorNameFromSymbolName(eventSymbolID)
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
                if 'cs' in spiPinControl['name'].lower():
                    self.__clearPinConfig(spiPinControl)
                    self.__setPinConfig(spiPinControl)
                    newLabel = self.__updateFunctionInSymbolLabel(spiPinControl['function'], symbol.getLabel())
                    symbol.setLabel(newLabel)
        else:
            symbol.setVisible(eventValue)

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
                # print("CHRIS dbg >> __setVisibleSignals {} -> {}".format(symbol, enable))
                
    def __checkAllSignalsDisabled(self, symbol):
        symbolSignals = self.__symbolPinByParent.get(symbol)
        # print("CHRIS dbg >> __checkAllSignalsDisabled {}: {}".format(symbol, symbolSignals))
        for symbolId in symbolSignals:
            pinId = symbolId.split('_')[-1]
            if pinId in self.__configuredPins:
                # print("CHRIS dbg >> __checkAllSignalsDisabled {} PinId: {} is configured".format(symbolId, pinId))
                return False
            
        return True

    def __checkGlobalCollisions(self, symbol, event):
        enablePin = event['value']
        if enablePin == True:
            # Pin Callback selects TRUE. Set rest of the signals with the same Pin as Read Only
            for pinId in self.__configuredPins:
                # Get collision pins in configuredPins
                symbolList = self.__collisionsByPinID.get(pinId)
                if symbolList != None:
                    for symbolId in symbolList:
                        symbolInterface = self.__symbolInterfaces.get(symbolId)
                        if symbolInterface != None:
                            if symbolInterface.getValue() == False:
                                # print("CHRIS dbg >> __checkGlobalCollisions set Read Only - symbolId: {}".format(symbolId))
                                if symbolId.find('SPI') == -1:
                                    symbolInterface.setReadOnly(True)
                                self.__setVisibleSignals(True, symbolId, pinId)
        else:
            # Pin Callback selects False. Clear Read Only values
            for pinId, symbolList in self.__collisionsByPinID.items():
                if pinId in self.__configuredPins:
                    # print("CHRIS dbg >> __checkGlobalCollisions pind is still configured: {}".format(pinId))
                    continue
                
                # If collision Pin has not been configured. Free Symbol if all subsignals are disabled.
                for symbolId in symbolList:
                    symbolInterface = self.__symbolInterfaces.get(symbolId)
                    if symbolInterface != None:
                        if symbolInterface.getReadOnly() == True:
                            if self.__checkAllSignalsDisabled(symbolId) == True:
                                # print("CHRIS dbg >> __checkGlobalCollisions clear Read Only - symbolId: {}".format(symbolId))
                                symbolInterface.setReadOnly(False)
                                self.__setVisibleSignals(False, symbolId, pinId)
                        elif symbolId.find('SPI') != -1:
                            self.__setVisibleSignals(False, symbolId, pinId)

    def __connectComponentDependencies(self, componentIDs):
        if len(componentIDs) == 2:
            idDependency = componentIDs[0]
            idCapability = componentIDs[1]
            
            connectTable = getAutoconnectTable(idDependency, idCapability)
            # print("CHRIS dbg >> __connectComponentDependencies connectTable: {}".format(connectTable)) 

            if len(connectTable) > 0:
                self.__db.connectDependencies(connectTable)

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
            return drvInstancesUnused[0][-1]
        else:                
            return str(idActiveList).count(driver + "_")

    def __checkBindings(self, dependencies, connectorName):
        if len(dependencies) != 2:
            return dependencies
            
        depId, capId = dependencies
        bindings = self.__depBindings.get(connectorName)
        if bindings != None:
            for binding in bindings:
                driverId, signal = binding
                if signal in depId:
                    depId = driverId

        return [depId, capId]

    def __configureDriverSettings(self, enabledPinIdList, disabledPinIdList):
        for pinId in enabledPinIdList:
            pinFunction, pinName = enabledPinIdList[pinId]
            # print("CHRIS dbg >> __configureDriverSettings Set {}: {}, {}".format(pinId, pinFunction, pinName))
            self.__setDriverSettings(pinFunction, pinName, True)
        
        for pinId in disabledPinIdList:
            pinFunction, pinName = disabledPinIdList[pinId]
            # print("CHRIS dbg >> __configureDriverSettings Set {}: {}, {}".format(pinId, pinFunction, pinName))
            self.__setDriverSettings(pinFunction, pinName, False)

    def __getPinListByMultiPinDriver(self, dependency):
        pinIdList = []
        for pinId in self.__configuredPins:
            params = dict()
            pinNumber = self.__devicePinMap.get(pinId)
            params.setdefault('pinNumber', pinNumber)
            params.setdefault('setting', 'function')
            ret = self.__db.sendMessage("core", "PIN_GET_CONFIG_VALUE", params)
            pinFunction = ret.get("value")
            # print("CHRIS dbg >> __getPinListByMultiPinDriver {} in {}".format(dependency, pinFunction))
            if dependency.lower() in pinFunction.lower():
                pinIdList.append(pinId)

        return pinIdList
            
    def __updateDriverConnections(self, addDependency, dependencyList, connectorName):
        # print("CHRIS dbg >> __updateDriverConnections[{}]: {}".format(addDependency, dependencyList))

        # Check extra bindings
        dependencyList = self.__checkBindings(dependencyList, connectorName)

        # print("CHRIS dbg >> __updateDriverConnections new dependencyList: {}".format(dependencyList))
        
        # Check if capability is already in use (this is needed because setReadOnly triggers callback)
        if addDependency == True and len(dependencyList) == 2:
            depId, capId = dependencyList
            driverInstance = self.__shdDependenciesPlibMultiInstance.get(capId)
            if driverInstance != None:
                # print("CHRIS dbg >> __updateDriverConnections checking {} in {}".format(depId, driverInstance))
                if depId in driverInstance: 
                    # print("CHRIS dbg >> __updateDriverConnections already in use ({})".format(capId))
                    return

        # Get Active components    
        idActiveList = self.__db.getActiveComponentIDs()
        # print("CHRIS dbg >> __updateDriverConnections idActiveList: {}".format(idActiveList))

        newConnections = []
        newComponents = []
        multiInstanceComponent = []
        removeComponents = []
        updatePlibInstance = False
        
        for dep in dependencyList:
            if addDependency is True:
                if self.__checkIsMultiInstanceDriver(dep) == True:
                    # Add new component/connection (multi instance)
                    newInstanceNumber = self.__getDriverMultiInstanceNumber(idActiveList, dep)
                    newDep ="{}_{}".format(dep, newInstanceNumber)
                    newConnections.append(newDep)
                    if newInstanceNumber == 0:
                        newComponents.append(dep)
                    else:
                        if newDep not in idActiveList: 
                            multiInstanceComponent.append(dep)
                        
                    updatePlibInstance = True
                else:
                    if dep not in idActiveList:    
                        # Add new component/connection (single instance)
                        newConnections.append(dep)
                        newComponents.append(dep)
            else:
                if dep in idActiveList:
                    if self.__checkIsMultiInstanceDriver(dep) == False:
                        # MultiInstance drivers are removed in removeComponents loop (Deactivate components)
                        # Check MultiPin drivers (driver that uses more than 1 pin)
                        pinList = self.__getPinListByMultiPinDriver(dep)
                        # print("CHRIS dbg >> __updateDriverConnections MultiPinDriver pinList: {}".format(pinList))
                        if len(pinList) == 0:
                            removeComponents.append(dep)
                
        # This is needed because multiInstance components cannot be enabled with other components
        if len(multiInstanceComponent) > 0:
            self.__db.activateComponents(multiInstanceComponent)
            
        if len(newComponents) > 0:
            # print("CHRIS dbg >> __updateDriverConnections newComponents: {}".format(newComponents))
            self.__db.activateComponents(newComponents)

        # Add new dependencies (Activate components)
        if len(newConnections) > 1:
            # print("CHRIS dbg >> __updateDriverConnections newConnections: {}".format(newConnections))
            self.__connectComponentDependencies(newConnections)
            # Update PLIB MultiInstance information
            if updatePlibInstance == True:
                self.__shdDependenciesPlibMultiInstance.setdefault(newConnections[1], newConnections[0])

        # Remove Components (Deactivate components)
        for component in removeComponents:
            # print("CHRIS dbg >> __updateDriverConnections remove Components: {}".format(component))
            self.__db.deactivateComponents([component])
            # Check multiinstance driver connection
            driver = self.__shdDependenciesPlibMultiInstance.get(component)
            if driver != None:
                driverInstance = int(driver[-1])
                instancesNumber = self.__getDriverMultiInstanceNumber(idActiveList, driver[0:-2])
                # print("CHRIS dbg >> __updateDriverConnections remove multiInstance: {} {} {}".format(driver, driverInstance, instancesNumber))
                if instancesNumber == 1:
                    # print("CHRIS dbg >> __updateDriverConnections deactivate component 1: {}".format(driver[0:-2]))
                    self.__db.deactivateComponents([driver[0:-2]])
                elif driverInstance == (instancesNumber - 1):
                    # print("CHRIS dbg >> __updateDriverConnections deactivate component 2: {}".format(driver))
                    self.__db.deactivateComponents([driver])

                del self.__shdDependenciesPlibMultiInstance[component]
                
        # print("CHRIS dbg >> __updateDriverConnections self.__shdDependenciesPlibMultiInstance: {}".format(self.__shdDependenciesPlibMultiInstance))
        
    def __setPinEnableCallback(self, symbol, event):
        global shdCheckCollisionSymbol

        dependencies = []
        enabledPinIdList = {}
        disabledPinIdList = {}
        if self.__pinCallbackBusy == False:
            # print("CHRIS dbg >> __setPinEnableCallback id: {} = {} ------------ ".format(event['id'], event['value']))
            self.__pinCallbackBusy = True

            # Get Pin Control List
            srcSymbolSplit = event["id"].split('_')
            if "INTERFACE" in event["id"]:
                connectorName = None
                if "_OPT_" in event["id"]:
                    interfaceIndex = int(srcSymbolSplit[-3])
                    optionIndex = int(srcSymbolSplit[-1])
                    pinControlList = self.getPinControlListByInterface(interfaceIndex, optionIndex)
                    # Extract dependencies from configuration file
                    newDep = self.__currentConfig['interfaces'][interfaceIndex]['options'][optionIndex].get('dependencies')
                    # print("CHRIS dbg >> __setPinEnableCallback iface_{}: opt_{}".format(interfaceIndex, optionIndex))
                else:
                    interfaceIndex = int(srcSymbolSplit[-1])
                    pinControlList = self.getPinControlListByInterface(interfaceIndex)
                    # Extract dependencies from configuration file
                    newDep = self.__currentConfig['interfaces'][interfaceIndex].get('dependencies')
                    # print("CHRIS dbg >> __setPinEnableCallback iface_{}".format(interfaceIndex))

                if newDep != None:
                    dependencies += newDep
            else:
                connectorSignal = srcSymbolSplit[-1].lower()
                connectorName = srcSymbolSplit[-2].replace("-"," ")
                pinControlList = self.getPinControlListByConnectorSignal(connectorName, connectorSignal)
                # print("CHRIS dbg >> __setPinEnableCallback {}: {}".format(connectorName, connectorSignal))

            # print("CHRIS dbg >> __setPinEnableCallback pinControlList: {}".format(pinControlList))

            for pinControl in pinControlList:
                pinId = pinControl.get('pinId')
                pinFunction = pinControl.get('function')
                pinName = pinControl.get('name')
                
                # Autodetect dependencies if not found in configuration file
                if len(dependencies) == 0:
                    # Extract DRIVER dependencies from Pin Name
                    pinName = pinControl.get('name')
                    if pinName != None:
                        newDep = getDriverDependencyFromPinName(pinName);
                        if (newDep != "") and (newDep not in dependencies):
                            dependencies.append(newDep)
                        
                    # Extract PLIB capabilities from Pin Function
                    if pinFunction != None and pinFunction != 'GPIO':
                        newDep = pinFunction.upper().split('_')[0].lower()
                        # Check exceptions
                        if newDep not in ['gmac']:
                            if newDep not in dependencies:
                                dependencies.append(newDep)

                # Set/Clear PIN configuration               
                if event["value"] is True:
                    # Check if that pin is already added                    
                    if not pinId in self.__configuredPins:
                        # print("CHRIS dbg >> __setPinEnableCallback set Pin {}".format(pinId))
                        self.__configuredPins.append(pinId)
                        self.__setPinConfig(pinControl)
                        enabledPinIdList.setdefault(pinId, (pinFunction, pinName))
                else:
                    # Check if that pin has to be removed
                    if pinId in self.__configuredPins:
                        # print("CHRIS dbg >> __setPinEnableCallback clear Pin {}".format(pinId))
                        self.__configuredPins.remove(pinId)
                        self.__clearPinConfig(pinControl)
                        disabledPinIdList.setdefault(pinId, (pinFunction, pinName))

            # Activate/Deactivate components and create connections
            self.__updateDriverConnections(event["value"], dependencies, connectorName)

            # Configure settings of the drivers of each updated PinId if needed
            self.__configureDriverSettings(enabledPinIdList, disabledPinIdList)
                
            # Check PIN Collisions
            shdCheckCollisionSymbol.setValue(event["value"])
            
            self.__pinCallbackBusy = False
            print("CHRIS dbg >> __setPinEnableCallback __configuredPins: {}".format(self.__configuredPins))

    def __getSymbolLabel(self, name, function, subSignal, pinNumber, pinId):
        if subSignal is None:
            return "{}:{}:Pin[{}]:{}".format(name, function, pinNumber, pinId)
        else:
            return "{}:{}:{}:Pin[{}]:{}".format(name, function, subSignal, pinNumber, pinId)
        
    def __updateFunctionInSymbolLabel(self, function, label):
        labelSplit = label.split(":")
        labelSplit[1] = function
        return ":".join(labelSplit)

    def __connectClickBoard(self, symbol, event):
        clickBoardSelection = event['value']
        id = symbol.getID()
        connectorSymbolName = id.replace("_DUMMY", "")
        connectorName = self.getConnectorNameFromSymbolName(connectorSymbolName)
        # print("CHRIS dbg >> __connectClickBoard: {} - {}".format(id, clickBoardSelection))

        if clickBoardSelection == "Select click board":
            # print("CHRIS dbg >> __connectClickBoard: resetConnectorConfig - {}".format(connectorName))
            self.resetConnectorConfig(connectorName)
            if self.__depBindings.get(connectorName) != None:
                del self.__depBindings[connectorName]
        else:
            clickBoardInterface = self.__clickBoards.get(clickBoardSelection)
            pinControl = clickBoardInterface.getConnections()
            # print("CHRIS dbg >> __connectClickBoard: pinControl - {}".format(pinControl))
            bindings = clickBoardInterface.getDependencies()
            if bindings != None:
                self.__depBindings.setdefault(connectorName, bindings)
                # print("CHRIS dbg >> __connectClickBoard: __setAdditionalDependencies: {}".format(self.__depBindings))
            self.setConnectorConfig(connectorName, pinControl)
         
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
            pinList.append(pinControl)
        else:
            for key, value in pinControl.items():
                # Multi pin signal
                pinList.append(value)

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
            if connector['name'] == connectorName:
                signalControl = connector['pinctrl'].get(connectorSignal)
                if signalControl != None:
                    if self.isPinSignal(signalControl):
                        # Single pin signal
                        pinControlList.append(signalControl)
                    else:
                        for signal, pinControl in signalControl.items():
                            # Multi pin signal
                            pinControlList.append(pinControl)
                return pinControlList
        else:
            return None

    def updatePinControlByConnector(self, connectorName, newPinControl):
        for connector in self.__currentConfig['connectors']:
            # print("SHD updatePinControlByConnector {} == {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                pinControlCurrent = connector['pinctrl']
                break

        for signal, newConfig in newPinControl.items():
            if newConfig.get('name') != None:
                # Single Pin
                pinCtrl = newConfig
                for key in newConfig:
                    pinControlCurrent[signal][key] = newConfig[key]
            else:
                # Multi Pin
                for subSignal, newSubConfig in newConfig.items():
                    pinCtrl = newSubConfig
                    for key in newSubConfig:
                        pinControlCurrent[signal][subSignal][key] = newSubConfig[key]   

    def restorePinControlByConnector(self, connectorName):
        connectorIndex = 0
        for connector in self.__currentConfig['connectors']:
            if connector['name'] == connectorName:
                pinControlCurrent = connector['pinctrl']
                break
            else:
                connectorIndex = connectorIndex + 1
                
        pinControlDefault = self.__defaultConfig['connectors'][connectorIndex]['pinctrl']
        
        for signal in pinControlCurrent:
            defaultSignal = pinControlDefault.get(signal)
            if defaultSignal != None:
                pinControlCurrent[signal] = deepcopy(defaultSignal)
                
    def getConnectorSymbolName(self, connectorName):
        return "SHD_MAINBOARD_CONNECTOR_{}".format(connectorName.replace(" ","-"))

    def getConnectorNameFromSymbolName(self, connectorSymbolName):
        return connectorSymbolName.split("_")[3].replace("-", " ")

    def getConnectorSignalSymbolName(self, connectorName, signalName):
        connectorSymbolName = self.getConnectorSymbolName(connectorName)
        return "{}_{}".format(connectorSymbolName, signalName.upper())

    def getConnectorSignalPinSymbolName(self, connectorName, signalName, pinId):
        connectorSignalName = self.getConnectorSignalSymbolName(connectorName, signalName)
        return "{}_{}".format(connectorSignalName, pinId.upper())

    def setConnectorConfig(self, connectorName, pinCtrl):
        # print("SHD configureConnector connectorName: {}, pinCtrl: {}".format(connectorName, pinCtrl))
        board = self.__db.getComponentByID(self.__interfaceID)
        
        # Update Pin Control of the Main Board by Connector
        self.updatePinControlByConnector(connectorName, pinCtrl)

        # Update Configuration Options by Connector
        signalList = self.getSignalListByConnectorName(connectorName)
        # print("CHRIS dbg: setConnectorConfig signalList: {}".format(signalList))
        for signal in signalList:
            # Enable/Disable signals
            connectorSignalName = self.getConnectorSignalSymbolName(connectorName, signal)
            signalSymbol = board.getSymbolByID(connectorSignalName)
            if pinCtrl.get(signal) != None:
                # print("CHRIS dbg: Enable symbol: {}".format(connectorSignalName))
                signalSymbol.setValue(True)
                
                pinDescriptionList = self.getDescriptionListByConnectorSignal(connectorName, signal)
                # Update Symbol label
                for pinDescription in pinDescriptionList:
                    if len(pinDescription) == 4:
                        name, function, pinNumber, pinId = pinDescription
                        label = self.__getSymbolLabel(name, function, None, pinNumber, pinId)
                    else:
                        name, function, subSignal, pinNumber, pinId = pinDescription
                        label = self.__getSymbolLabel(name, function, subSignal, pinNumber, pinId)
                        # Handle SPI CS exception (configuration option is not allowed)
                        if subSignal.lower() == 'cs' and function != "GPIO":
                            # print("CHRIS dbg >> Handle SPI CS exception - subSignal: {}".format(subSignal.lower())) 
                            symbolName = self.__symbolNamesByConnector[connectorName][pinId]
                            shdSpiCSConfigSymbolName = "{}_{}".format(symbolName, "CSASGPIO")
                            # print("CHRIS dbg >> CS set Visible: {}".format(shdSpiCSConfigSymbolName))
                            signalSpiCsPinSymbol = board.getSymbolByID(shdSpiCSConfigSymbolName)
                            signalSpiCsPinSymbol.setVisible(True)

                    signalPinSymbol = board.getSymbolByID(self.__symbolNamesByConnector[connectorName][pinId])
                    signalPinSymbol.setLabel(label)

            # else:
            #     # print("CHRIS dbg: Disable symbol: {}".format(connectorSignalName))
            #     signalSymbol.setValue(False)
            #     signalSymbol.setVisible(False)

            # signalSymbol.setReadOnly(True)
            
    def resetConnectorConfig(self, connectorName):
        # print("SHD restoreConnections connectorName: {}".format(connectorName))
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
            
            # Update Symbol label
            pinDescriptionList = self.getDescriptionListByConnectorSignal(connectorName, signal)
            for pinDescription in pinDescriptionList:
                if len(pinDescription) == 4:
                    name, function, pinNumber, pinId = pinDescription
                    label = self.__getSymbolLabel(name, function, None, pinNumber, pinId)
                else:
                    name, function, subSignal, pinNumber, pinId = pinDescription
                    label = self.__getSymbolLabel(name, function, subSignal, pinNumber, pinId)
                    # Handle SPI CS exception (configuration option is not allowed)
                    if subSignal.lower() == 'cs' and function != "GPIO":
                        symbolName = self.__symbolNamesByConnector[connectorName][pinId]
                        shdSpiCSConfigSymbolName = "{}_{}".format(symbolName, "CSASGPIO")
                        signalSpiCsPinSymbol = board.getSymbolByID(shdSpiCSConfigSymbolName)
                        signalSpiCsPinSymbol.setVisible(True)

                signalPinSymbol = board.getSymbolByID(self.__symbolNamesByConnector[connectorName][pinId])
                signalPinSymbol.setLabel(label)

    def handleMessage(self, id, args):
        retDict = {}
        print("mainBoard handleMessage: {} args: {}".format(id, args))
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
        self.__boardComponent = boardInterface

        global shdCheckCollisionSymbol
        shdCheckCollisionSymbol = boardInterface.createBooleanSymbol("SHD_CHECK_COLLISIONS", None)
        shdCheckCollisionSymbol.setLabel("")
        shdCheckCollisionSymbol.setVisible(False)
        shdCheckCollisionSymbol.setDependencies(self.__checkGlobalCollisions, ["SHD_CHECK_COLLISIONS"])
        
        symbol = boardInterface.createStringSymbol("SHD_MAINBOARD_NAME", None)
        symbol.setLabel("Board Name")
        symbol.setDefaultValue(self.__currentConfig.get('name'))
        symbol.setReadOnly(True)
        symbol.setHelp(shdMainBoardHelp)
        
        symbol = boardInterface.createStringSymbol("SHD_MAINBOARD_PIO_PERIPH", None)
        symbol.setLabel("PIO Peripheral")
        symbol.setDefaultValue(getDeviceGPIOPeripheral(self.__atdf))
        symbol.setReadOnly(True)
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

                        pinControlList = self.getDescriptionListByInterface(interfaceIndex, optionIndex)
                        # print("CHRIS dbg >> option pinControlList: {}".format(pinControlList))
                        for pinControl in pinControlList:
                            # print("CHRIS dbg >> option pinControl: {}".format(pinControl))
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

                            if self.__symbolNamesByInterface.get(pinId) != None:
                                self.__symbolNamesByInterface[pinId].append(optionSymbolName)
                            else:
                                self.__symbolNamesByInterface.setdefault(pinId, [optionSymbolName])
                        
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

                    pinControlList = self.getDescriptionListByInterface(interfaceIndex)
                    # print("CHRIS dbg >> pinControlList: {}".format(pinControlList))
                    for pinControl in pinControlList:
                        # print("CHRIS dbg >> pinControl: {}".format(pinControl))
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

                        if self.__symbolNamesByInterface.get(pinId) != None:
                            self.__symbolNamesByInterface[pinId].append(interfaceSymbolName)
                        else:
                            self.__symbolNamesByInterface.setdefault(pinId, [interfaceSymbolName])
                            
                    interfaceDependencies.append(interfaceSymbolName)

                interfaceIndex = interfaceIndex + 1
                
            shdInterfaceList.setDependencies(self.__setPinEnableCallback, interfaceDependencies)
            # print("CHRIS dbg >> interfaceDependencies: {}".format(interfaceDependencies))
            
            # Add collision data
            self.__collisionsByPinID = deepcopy(self.__symbolNamesByInterface)
                
        # EXTERNAL CONNECTORS DEFINITIONS -------------------------------------
        boardConnectors = self.__currentConfig.get('connectors')
        if boardConnectors != None:
            # print("CHRIS dbg >> createMenuSymbol: SHD_MAINBOARD_CONNECTORS")
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
                clickBoardSelection = ['Select click board']
                for name, interface in self.__clickBoards.items():
                    if boardConnectors[conIndex].get('compatible') == interface.getConnectorCompatible():
                        clickBoardSelection.append(name)
                
                if len(clickBoardSelection) == 1:
                    clickBoardSelection = ['No click board available']
                
                connectorSymbolName = self.getConnectorSymbolName(conName)
                # print("CHRIS dbg >> createMenuSymbol: {}".format(connectorSymbolName))
                shdConnectorSymbol = boardInterface.createComboSymbol(connectorSymbolName, shdConnectorList, clickBoardSelection)
                shdConnectorSymbol.setLabel(conName)            
                shdConnectorSymbol.setDefaultValue(clickBoardSelection[0])
                shdConnectorSymbol.setDescription(conDescription)
                shdConnectorSymbol.setVisible(True)
                if len(clickBoardSelection) == 1:
                    shdConnectorSymbol.setReadOnly(True)       
                shdConnectorSymbol.setHelp(shdMainBoardHelp)

                shdConnectorSymbolDummy = boardInterface.createMenuSymbol(connectorSymbolName + "_DUMMY", shdConnectorList)
                shdConnectorSymbolDummy.setLabel("")
                shdConnectorSymbolDummy.setVisible(False)
                shdConnectorSymbolDummy.setDependencies(self.__connectClickBoard, [connectorSymbolName])

                signalList = self.getSignalListByConnector(conIndex)
                for signal in signalList:
                    connectorSignalName = self.getConnectorSignalSymbolName(conName, signal)
                    # print("CHRIS dbg >> createBooleanSymbol: {}".format(connectorSignalName))
                    shdConSignalSymbol = boardInterface.createBooleanSymbol(connectorSignalName, shdConnectorSymbol)
                    shdConSignalSymbol.setLabel(signal.upper())
                    shdConSignalSymbol.setDescription("Enable {} : {}".format(conName, signal.upper()))
                    shdConSignalSymbol.setDefaultValue(False)
                    shdConSignalSymbol.setHelp(shdMainBoardHelp)
                    self.__symbolInterfaces.setdefault(connectorSignalName, shdConSignalSymbol)
                    
                    pinDescriptionList = self.getDescriptionListByConnectorSignal(conName, signal)
                    for pinDescription in pinDescriptionList:
                        # print("CHRIS dbg >> pinDescription: {}".format(pinDescription))
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
                                # print("CHRIS dbg >> Handle SPI CS exception: {} {} {} {} {}".format(name, function, subSignal, pinNumber, pinId))
                                # Handle SPI CS exception
                                spiCSdetected = True
                            
                        shdConPinControlSymbolName = self.getConnectorSignalPinSymbolName(conName, signal, pinId)
                        # Store the Symbol name to be used in click Boards connection events
                        symbolNamesByPinId.setdefault(pinId, shdConPinControlSymbolName)
                        # print("CHRIS dbg >> symbolNamesByPinId: {}".format(symbolNamesByPinId))

                        # print("CHRIS dbg >> conPinControlName: ", conPinControlName)
                        # print("CHRIS dbg >> createCommentSymbol: {}".format(shdConPinControlSymbolName))
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
                            # print("CHRIS dbg >> createBooleanSymbol: {}".format(shdSpiCSConfigSymbolName))
                            shdSpiCSConfigSymbol = boardInterface.createBooleanSymbol(shdSpiCSConfigSymbolName, shdConPinControlSymbol)
                            shdSpiCSConfigSymbol.setLabel("Drive CS signal as GPIO")
                            shdSpiCSConfigSymbol.setDescription("Drive CS signal as GPIO")
                            shdSpiCSConfigSymbol.setDefaultValue(False)
                            shdSpiCSConfigSymbol.setHelp(shdMainBoardHelp)
                            self.__symbolInterfaces.setdefault(shdSpiCSConfigSymbolName, shdSpiCSConfigSymbol)

                            # print("CHRIS dbg >> spiCSdetected connectorSignalName: {} shdSpiCSConfigSymbolName: {}".format(connectorSignalName, shdSpiCSConfigSymbolName))
                            shdConPinControlSymbol.setDependencies(self.__showSymbol, [connectorSignalName, shdSpiCSConfigSymbolName])

                        else:
                            shdConPinControlSymbol.setDependencies(self.__showSymbol, [connectorSignalName])
                            
                    connectorDependencies.append(connectorSignalName)
                    
                self.__symbolNamesByConnector.setdefault(conName, symbolNamesByPinId)
                shdConnectorSymbol.setDependencies(self.__setPinEnableCallback, connectorDependencies)
                # print("CHRIS dbg >> connectorDependencies: {}".format(connectorDependencies))

        # remove no collision data
        for key, value in self.__collisionsByPinID.items():
            if len(value) == 1:
                self.__collisionsByPinID.pop(key, value)

        # for key, value in self.__symbolNamesByInterface.items():
        #     print("CHRIS dbg >> self.__symbolNamesByInterface: {}: {}".format(key, value))

        # for key, value in self.__symbolNamesByConnector.items():
        #     print("CHRIS dbg >> self.__symbolNamesByConnector: {}: {}".format(key, value))

        # for key, value in self.__collisionsByPinID.items():
        #     print("CHRIS dbg >> self.__collisionsByPinID: {}: {}".format(key, value))

        # for key, value in self.__symbolPinByParent.items():
        #     print("CHRIS dbg >> self.__symbolPinByParent: {}: {}".format(key, value))
 