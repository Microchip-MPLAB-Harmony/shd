import sys
from os import path
import glob
from copy import deepcopy
from utils.connectorSpec import getConnectorPinNumberFromSignal
from utils.deviceSpec import getDeviceFunctionListByPinId, getDevicePinMap, getDeviceGPIOPeripheral, adaptDevicePeripheralDependencies
from utils.dBMsgInterface import getDBMsgPLIBConfiguration, getDBMsgDriverConfiguration, getAutoconnectTable, getDriverDependencyFromPinName, checkPlibFromSignalConnector
from clickBoard.clickBoard import ClickBoard

shdMainBoardHelp = 'shdMainBoardHelpKeyword'
shdMultiInstanceDrivers = ['drv_i2c', 'drv_spi', 'drv_usart', 'drv_sdmmc', 'a_drv_i2s', 'drv_sdspi', 'sys_console']

class MainBoard:
    def __init__(self, context):
        self.__currentConfig = {}
        for item in sys.path:
            if "shd\\boards" in item:
                boardYamlFile = path.join(item, context["configuration"])
                
            if "shd\\clickBoards" in item:
                clickBoardsPath = item

        if not path.isfile(boardYamlFile):
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
        self.__signalCallbackBusy = False
        self.__depBindings = {}
        self.__shdDependenciesPlibMultiInstance = {}
        self.__connections = {}
        self.__shdCheckCollisionSymbol = None
        self.__architecture = self.__atdf.getNode("/avr-tools-device-file/devices/device").getAttribute("architecture")
        self.__family = self.__atdf.getNode("/avr-tools-device-file/devices/device").getAttribute("family")

        # self.__log.writeDebugMessage("CHRIS dbg >> __devicePinMap: {}".format(self.__devicePinMap))
        # self.__log.writeDebugMessage("CHRIS dbg >> __architecture: {}".format(self.__architecture))
        # self.__log.writeDebugMessage("CHRIS dbg >> __family: {}".format(self.__family))
        
        import yaml
        with open(boardYamlFile, 'r') as file:
            self.__defaultConfig = yaml.safe_load(file)
            self.__currentConfig = deepcopy(self.__defaultConfig)
            self.__interfaceID = "mainBoard_" + self.__defaultConfig['config'].split(".")[0].upper() 

        clickBoardFileList = glob.glob(path.join(clickBoardsPath, '*.yml'))
        self.__clickBoards = {}
        for clickBoard in clickBoardFileList:
            clickBoardFile = path.basename(clickBoard)
            try:
                interface = ClickBoard(clickBoardFile)
                boardName = interface.getName()
                self.__clickBoards.setdefault(boardName, interface)
            except:
                continue

    def __del__(self):
        # self.__log.writeDebugMessage("CHRIS dbg >> __del__ MainBoard")
        self.resetSignalConfiguration()
        
    def __str__(self):
        return "{}".format(self.__currentConfig)
        
    def __setPLIBSettings(self, pinDescr, value):
        idActiveList = self.__db.getActiveComponentIDs()
        for signalId, (pinId, functionValue, nameValue) in pinDescr.items():
            settings = (signalId, pinId, functionValue, nameValue, value)
            # self.__log.writeDebugMessage("CHRIS dbg >> __setPLIBSettings : {}".format(settings))
            componentID, messageID, params = getDBMsgPLIBConfiguration(self.__atdf, settings)
            if messageID != None and componentID in idActiveList:
                # self.__log.writeDebugMessage("CHRIS dbg >> __setPLIBSettings: sending message to {} : {}. params: {}".format(componentID, messageID, params))
                res = self.__db.sendMessage(componentID, messageID, params)
                if res != None and res.get("Result") != "Success":
                    self.__log.writeDebugMessage("SHD mainBoard: Error in sending message to PLIB {} : {}. Error: {}".format(componentID, messageID, res.get("Result")))
            # else:
            #     self.__log.writeDebugMessage("CHRIS dbg >> __setPLIBSettings skip {} messageID:{} idActiveList{}".format(componentID, messageID, idActiveList))

    def __setDriverSettings(self, pinDescr, value):
        # self.__log.writeDebugMessage("CHRIS dbg >> __setDriverSettings pinDescr: {}".format(pinDescr))
        # Find driver connection
        for signalId, (pinId, functionValue, nameValue) in pinDescr.items():
            for plib, driver in self.__connections.items():
                settings = (driver, signalId, pinId, functionValue, nameValue, value)
                # self.__log.writeDebugMessage("CHRIS dbg >> __setDriverSettings : {}".format(settings))
                componentID, messageID, params = getDBMsgDriverConfiguration(settings)
                if messageID != None:
                    # self.__log.writeDebugMessage("CHRIS dbg >> __setDriverSettings: sending message - {} : {}. params: {}".format(componentID, messageID, params))
                    res = self.__db.sendMessage(componentID, messageID, params)
                    if res != None and res.get("Result") != "Success":
                        self.__log.writeDebugMessage("SHD mainBoard: skip sending message to DRV {} : {}. Error: {}".format(componentID, messageID, res.get("Result")))
                # else:
                #     self.__log.writeDebugMessage("CHRIS dbg >> __setDriverSettings ERROR : {} {} {}".format(componentID, messageID, params))

    def __clearPinConfig(self, pinControl):
        # self.__log.writeDebugMessage("CHRIS dbg >> __clearPinConfig pinControl: {}".format(pinControl))
        pinNumber = self.__devicePinMap.get(pinControl.get('pinId'))

        for key, value in pinControl.items():
            if key == 'pinId':
                continue
            
            params = dict()
            params.setdefault('pinNumber', pinNumber)
            params.setdefault('setting', key)
            # self.__log.writeDebugMessage("CHRIS dbg >> send Message PIN_CLEAR_CONFIG_VALUE : {}".format(params))
            self.__db.sendMessage("core", "PIN_CLEAR_CONFIG_VALUE", params)

    def __handleFunctionPioManager(self, pinCtrlFunction, functionByPinId):
        # self.__log.writeDebugMessage("CHRIS dbg: __handleFunctionPioManager {} : {}".format(pinCtrlFunction, functionByPinId))
        if 'MCSPI' in pinCtrlFunction:
            functionValues = functionByPinId.split('/')
            # self.__log.writeDebugMessage("CHRIS dbg: __handleFunctionPioManager {}".format(functionValues))
            for function in functionValues:
                if pinCtrlFunction in function:
                    return function

        # Adapt function name for some family devices (WBZ)
        if "WBZ" in self.__family:
            if "ADCHS" in pinCtrlFunction:
                pinCtrlFunction = pinCtrlFunction.split("_")[-1]
                
            return pinCtrlFunction

        # Adapt function name for MIPS architecture
        if self.__architecture == "MIPS":
            pinCtrlFunction = pinCtrlFunction.split("_")[-1]
            # self.__log.writeDebugMessage("CHRIS dbg: __handleFunctionPioManager MIPS: {}".format(pinCtrlFunction))

        if pinCtrlFunction in functionByPinId:
            return functionByPinId

        return None

    def __setPinConfig(self, pinControl):
        # self.__log.writeDebugMessage("CHRIS dbg >> __setPinConfig pinControl: {}".format(pinControl))
        pinId = pinControl.get('pinId')
        pinNumber = self.__devicePinMap.get(pinId)

        # Get function values list from the pinNumber
        functionList = getDeviceFunctionListByPinId(self.__db, self.__atdf, pinId)
        # self.__log.writeDebugMessage("CHRIS dbg: functionList {}".format(functionList))

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
                    self.__log.writeDebugMessage("SHD mainBoard: Error in function setting of pinId: {} - function: {}".format(pinId, value))
                    self.__log.writeDebugMessage("SHD mainBoard: Match function setting with one of these values: {}".format(functionList))
                    continue
                        
            if key in ['function', 'name', 'pinId']:
                value = value.upper()
            elif type(value).__name__ == 'bool':
                if key in ['pull up', 'pull down', 'open drain', 'change notification']:
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
            # self.__log.writeDebugMessage("CHRIS dbg >> send Message PIN_SET_CONFIG_VALUE : {}".format(params))
            self.__db.sendMessage("core", "PIN_SET_CONFIG_VALUE", params)

    def __checkPinIsConfigured(self, pinId):
        params = dict()
        pinNumber = self.__devicePinMap.get(pinId)
        params.setdefault('pinNumber', pinNumber)
        params.setdefault('setting', 'function')
        retDict = self.__db.sendMessage("core", "PIN_GET_CONFIG_VALUE", params)
        functionValue = retDict.get('value')
        # self.__log.writeDebugMessage("CHRIS dbg >> __checkPinIsConfigured {} : {}".format(pinId, functionValue))
        if functionValue == "":
            return False
        else:
            return True
    
    def __showSymbol(self, symbol, event):
        eventSymbolID = event['id']
        eventValue = event['value']
        # self.__log.writeDebugMessage("CHRIS dbg >> __showSymbol eventSymbolID: {} - {}".format(eventSymbolID, eventValue))
        if "CSASGPIO" in eventSymbolID:
            # self.__log.writeDebugMessage("CHRIS dbg >> __showSymbol eventSymbolID: {}".format(eventSymbolID))
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
                signal, pinControl = spiPinControl
                if signal == 'cs':
                    self.__clearPinConfig(pinControl)
                    self.__setPinConfig(pinControl)
                    newLabel = self.__updateFunctionInSymbolLabel(pinControl['function'], symbol.getLabel())
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
                # self.__log.writeDebugMessage("CHRIS dbg >> __setVisibleSignals {} -> {}".format(symbol, enable))
                
    def __checkAllSignalsDisabled(self, symbol):
        symbolSignals = self.__symbolPinByParent.get(symbol)
        # self.__log.writeDebugMessage("CHRIS dbg >> __checkAllSignalsDisabled {}: {}".format(symbol, symbolSignals))
        for symbolId in symbolSignals:
            pinId = symbolId.split('_')[-1]
            if pinId in self.__configuredPins:
                # self.__log.writeDebugMessage("CHRIS dbg >> __checkAllSignalsDisabled {} PinId: {} is configured".format(symbolId, pinId))
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
                                # self.__log.writeDebugMessage("CHRIS dbg >> __checkGlobalCollisions set Read Only - symbolId: {}".format(symbolId))
                                if symbolId.find('SPI') == -1:
                                    symbolInterface.setReadOnly(True)
                                self.__setVisibleSignals(True, symbolId, pinId)
        else:
            # Pin Callback selects False. Clear Read Only values
            for pinId, symbolList in self.__collisionsByPinID.items():
                if pinId in self.__configuredPins:
                    # self.__log.writeDebugMessage("CHRIS dbg >> __checkGlobalCollisions pind is still configured: {}".format(pinId))
                    continue
                
                # If collision Pin has not been configured. Free Symbol if all subsignals are disabled.
                for symbolId in symbolList:
                    symbolInterface = self.__symbolInterfaces.get(symbolId)
                    if symbolInterface != None:
                        if symbolInterface.getReadOnly() == True:
                            if self.__checkAllSignalsDisabled(symbolId) == True:
                                # self.__log.writeDebugMessage("CHRIS dbg >> __checkGlobalCollisions clear Read Only - symbolId: {}".format(symbolId))
                                symbolInterface.setReadOnly(False)
                                self.__setVisibleSignals(False, symbolId, pinId)
                        elif symbolId.find('SPI') != -1:
                            self.__setVisibleSignals(False, symbolId, pinId)

    def __connectComponentDependencies(self, connection):
        depId, capId = connection
            
        connectTable = getAutoconnectTable(self.__family, depId, capId)
        # self.__log.writeDebugMessage("CHRIS dbg >> __connectComponentDependencies connectTable: {}".format(connectTable)) 

        if len(connectTable) > 0:
            res = self.__db.connectDependencies(connectTable)
            if res == True:
                # detect if it is multi-instance dep
                if depId[-2] == "_":
                    self.__connections.setdefault(capId, depId[:-2])
                else:
                    self.__connections.setdefault(capId, depId)

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
        newDeps = {}

        for depId, capId in dependencies.items():
            if capId == "":
                newDeps.setdefault(depId, capId)
                continue

            # Only for dependencies on Connectors (click Boards)
            bindings = self.__depBindings.get(connectorName)
            # self.__log.writeDebugMessage("CHRIS dbg >> __overlapDependencies ({},{}): {}".format(depId, capId, bindings))
            if bindings != None:
                for binding in bindings:
                    driver, signal = binding
                    # Check if Plib supports the signal in bindings
                    if checkPlibFromSignalConnector(capId, signal) == True:
                        # self.__log.writeDebugMessage("CHRIS dbg >> __overlapDependencies checkPlibFromSignalConnector:TRUE {} {}".format(capId, signal))
                        depId = driver
                        
            newDeps.setdefault(depId, capId)

        return newDeps

    def __configureDriverSettings(self, enabledPinIdList, disabledPinIdList):
        for pinId, pinDescr in enabledPinIdList.items():
            # signal, (pinFunction, pinName) = enabledPinIdList[pinId]
            # self.__log.writeDebugMessage("CHRIS dbg >> __configureDriverSettings Set {}: {}, {}".format(pinId, signal, pinFunction, pinName))
            self.__setPLIBSettings(pinDescr, True)
            self.__setDriverSettings(pinDescr, True)
        
        for pinId, pinDescr  in disabledPinIdList.items():
            # signal, (pinFunction, pinName) = disabledPinIdList[pinId]
            # self.__log.writeDebugMessage("CHRIS dbg >> __configureDriverSettings Set {}: {}, {}".format(pinId, signal, pinFunction, pinName))
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
            # self.__log.writeDebugMessage("CHRIS dbg >> __getPinListByMultiPinDriver {}: {} in {}".format(pinId, dependency, pinFunction))
            # Handle exceptions: MCPWM, ADCHS
            if dependency == 'mcpwm':
                dependency = 'pwm'
            if dependency == 'adchs':
                dependency = 'an'
            if dependency.lower() in pinFunction.lower():
                pinIdList.append(pinId)

        return pinIdList

    def __updateDriverConnections(self, addDependency, dependencyList, connectorName):
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections[{}]: {}".format(addDependency, dependencyList))

        # Check overlap bindings
        dependencyList = self.__overlapDependencies(dependencyList, connectorName)
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections new dependencyList: {}".format(dependencyList))
        
        # Check if capability is already in use (this is needed because setReadOnly triggers callback)
        dependencyListFiltered = {}
        if addDependency == True:
            for depId, capId in dependencyList.items():
                if capId == "":
                    dependencyListFiltered.setdefault(depId, capId)
                    continue
                
                driverInstance = self.__shdDependenciesPlibMultiInstance.get(capId)
                if driverInstance != None:
                    # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections checking {} in {}".format(depId, driverInstance))
                    if depId in driverInstance: 
                        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections already in use ({})".format(capId))
                        continue

                dependencyListFiltered.setdefault(depId, capId)
        else:
            dependencyListFiltered = dependencyList

        # Get Active components    
        idActiveList = self.__db.getActiveComponentIDs()
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections idActiveList: {}".format(idActiveList))

        # Adapt Dependency List according to PIO peripheral ID 
        dependencyList = adaptDevicePeripheralDependencies(self.__atdf, dependencyListFiltered)
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections PIO adapted dependencyList: {}".format(dependencyList))

        # if addDependency == True and self.__checkExistConnection(dependencyList):
        #     self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections connections already created: {}".format(dependencyList))
        #     return

        newConnections = []
        newComponents = []
        multiInstanceComponent = []
        removeComponents = []
        updatePlibInstance = False
        
        for depId, capId in dependencyList.items():
            if addDependency is True:
                if self.__checkIsMultiInstanceDriver(depId) == True:
                    # Add new component/connection (multi instance)
                    newInstanceNumber = self.__getDriverMultiInstanceNumber(idActiveList, depId)
                    newDep ="{}_{}".format(depId, newInstanceNumber)
                    newConnections.append((newDep, capId))
                    newComponents.append(capId)
                    if newInstanceNumber == 0:
                        newComponents.append(depId)
                    else:
                        if newDep not in idActiveList: 
                            multiInstanceComponent.append(depId)
                        
                    updatePlibInstance = True
                else:
                    if depId not in idActiveList:    
                        # Add new component/connection (single instance)
                        newComponents.append(depId)
                        
                    if capId != "" and capId not in idActiveList:
                        newConnections.append((depId, capId))
                        newComponents.append(capId)
            else:
                if capId in idActiveList:
                    # Check MultiPin drivers (driver that uses more than 1 pin)
                    pinList = self.__getPinListByMultiPinDriver(capId)
                    # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections MultiPinDriver pinList: {}".format(pinList))
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
                        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections MultiPinDriver pinList: {}".format(pinList))
                        if len(pinList) == 0:
                            removeComponents.append(depId)
                
        # This is needed because multiInstance components cannot be enabled with other components
        if len(multiInstanceComponent) > 0:
            self.__db.activateComponents(multiInstanceComponent)
            
        if len(newComponents) > 0:
            # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections newComponents: {}".format(newComponents))
            self.__db.activateComponents(newComponents)

        # Add new dependencies (Activate components)
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections newConnections: {}".format(newConnections))
        for connection in newConnections:
            self.__connectComponentDependencies(connection)
            # Update PLIB MultiInstance information
            if updatePlibInstance == True:
                depId, capId = connection
                self.__shdDependenciesPlibMultiInstance.setdefault(capId, depId)

        # Remove Components (Deactivate components)
        for component in removeComponents:
            # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections remove Components: {}".format(component))
            res = self.__db.deactivateComponents([component])
            if res == True and self.__connections.get(component) != None:
                del self.__connections[component]
            # Check multiinstance driver connection
            driver = self.__shdDependenciesPlibMultiInstance.get(component)
            if driver != None:
                driverInstance = int(driver[-1])
                instancesNumber = self.__getDriverMultiInstanceNumber(idActiveList, driver[0:-2])
                # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections remove multiInstance: {} {} {}".format(driver, driverInstance, instancesNumber))
                if instancesNumber == 1:
                    # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections deactivate component 1: {}".format(driver[0:-2]))
                    self.__db.deactivateComponents([driver[0:-2]])
                elif driverInstance == (instancesNumber - 1):
                    # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections deactivate component 2: {}".format(driver))
                    self.__db.deactivateComponents([driver])

                del self.__shdDependenciesPlibMultiInstance[component]
                
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections self.__shdDependenciesPlibMultiInstance: {}".format(self.__shdDependenciesPlibMultiInstance))
        # self.__log.writeDebugMessage("CHRIS dbg >> __updateDriverConnections self.__connections: {}".format(self.__connections))
        
    def __signalEnableCallback(self, symbol, event):
        dependencies = {}
        enabledPinIdList = {}
        disabledPinIdList = {}
        if self.__signalCallbackBusy == False:
            # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback id: {} = {} ------------ ".format(event['id'], event['value']))
            self.__signalCallbackBusy = True

            # Get Pin Control List
            srcSymbolSplit = event["id"].split('_')
            # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback srcSymbolSplit: {}".format(srcSymbolSplit))
            if "INTERFACE" in event["id"]:
                connectorName = None
                if "_OPT_" in event["id"]:
                    interfaceIndex = int(srcSymbolSplit[-3])
                    optionIndex = int(srcSymbolSplit[-1])
                    pinControlList = self.getPinControlListByInterface(interfaceIndex, optionIndex)
                    # Extract dependencies from configuration file
                    newDepList = self.__currentConfig['interfaces'][interfaceIndex]['options'][optionIndex].get('dependencies')
                    # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback iface_{}: opt_{}".format(interfaceIndex, optionIndex))
                else:
                    interfaceIndex = int(srcSymbolSplit[-1])
                    pinControlList = self.getPinControlListByInterface(interfaceIndex)
                    # Extract dependencies from configuration file
                    newDepList = self.__currentConfig['interfaces'][interfaceIndex].get('dependencies')
                    # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback iface_{}".format(interfaceIndex))

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
                # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback {}: {}".format(connectorName, connectorSignal))
                pinControlList = self.getPinControlListByConnectorSignal(connectorName, connectorSignal)

            # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback pinControlList: {}".format(pinControlList))

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
                    newDep = getDriverDependencyFromPinName(pinName);
                    if (newDep != ""):
                        depId = newDep
                    
                # Extract PLIB capabilities from Pin Function
                if pinFunction != None and pinFunction != 'GPIO':
                    newCap = pinFunction.upper().split('_')[0].lower()
                    # Check exceptions
                    if newCap not in ['gmac']:
                        capId = newCap

                # GPIOs don't have dependencies, except I2C_BB
                # Extract PLIB capabilities from Pin Name (I2C_BB)
                if (pinFunction == 'GPIO'):
                    if (signalId in ['sda', 'scl']):
                        capId = "i2c_bb"
                    else:
                        autodetectDeps = False

                if autodetectDeps == True:
                    # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback Autodetect dependency [{},{}]".format(depId, capId))
                    # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback dependencies tmp: {}".format(dependencies))
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
                        # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback set Pin {}".format(pinId))
                        self.__configuredPins.append(pinId)
                        self.__pinControlByPinId.setdefault(pinId, pinCtrl)
                        self.__setPinConfig(pinCtrl)
                        enabledPinIdList.setdefault(pinId, pinDescr)
                else:
                    # Check if that pin has to be removed
                    if pinId in self.__configuredPins:
                        # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback clear Pin {}".format(pinId))
                        self.__configuredPins.remove(pinId)
                        del self.__pinControlByPinId[pinId]
                        self.__clearPinConfig(pinCtrl)
                        disabledPinIdList.setdefault(pinId, pinDescr)

            # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback dependencies: {}".format(dependencies))

            # Activate/Deactivate components and create connections
            self.__updateDriverConnections(event["value"], dependencies, connectorName)

            # Configure settings of the drivers of each updated PinId if needed
            self.__configureDriverSettings(enabledPinIdList, disabledPinIdList)
                
            # Check PIN Collisions
            self.__shdCheckCollisionSymbol.setValue(event["value"])

            self.__signalCallbackBusy = False
            # self.__log.writeDebugMessage("CHRIS dbg >> __signalEnableCallback __configuredPins: {}".format(self.__configuredPins))

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
        # self.__log.writeDebugMessage("CHRIS dbg >> __connectClickBoard: {} - {}".format(id, clickBoardSelection))

        self.resetConnectorConfig(connectorName)

        if clickBoardSelection == "Select click board":
            if self.__depBindings.get(connectorName) != None:
                del self.__depBindings[connectorName]
            # self.__log.writeDebugMessage("CHRIS dbg >> __connectClickBoard: resetConnectorConfig - {} self.__depBindings:{}".format(connectorName, self.__depBindings))
        else:
            clickBoardInterface = self.__clickBoards.get(clickBoardSelection)
            pinControlClickBoard = clickBoardInterface.getConnections()
            # self.__log.writeDebugMessage("CHRIS dbg >> __connectClickBoard: pinControlClickBoard - {}".format(pinControlClickBoard))
            
            bindingList = clickBoardInterface.getDependencies()
            # self.__log.writeDebugMessage("CHRIS dbg >> __connectClickBoard: bindingList - {}".format(bindingList))
            index = 0
            for depIdCon, signalCon in bindingList:
                pinControlConnector = self.getPinControlByConnectorName(connectorName)
                pinControlSignal = pinControlConnector.get(signalCon)
                if pinControlSignal != None:
                    pinFunction = pinControlSignal.get("function")
                    if pinFunction == None: # this is a bus signals (usart, i2c, spi)
                        if signalCon == 'spi':
                            pinFunction = pinControlSignal.get("mosi").get("function")
                        elif signalCon == 'uart':
                            pinFunction = pinControlSignal.get("tx").get("function")
                        elif signalCon == 'i2c':
                            pinFunction = pinControlSignal.get("sda").get("function")

                    if pinFunction != None:
                        pinFunction = pinFunction.upper()
                        if pinFunction != 'GPIO':
                            plib = pinFunction.split("_")
                            if len(plib) > 1:
                                plib = plib[0]
                            # Overwrite the current element of the bindingList
                            bindingList[index] = [depIdCon, plib.lower()]
                            # self.__log.writeDebugMessage("CHRIS dbg >> __connectClickBoard added bindingList[{}]: {}".format(index, bindingList[index]))

                index = index + 1
                            
                self.__depBindings.setdefault(connectorName, bindingList)
                # self.__log.writeDebugMessage("CHRIS dbg >> __connectClickBoard: __setAdditionalDependencies: {}".format(self.__depBindings))
                
            self.setConnectorConfig(connectorName, pinControlClickBoard)
         
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
            # self.__log.writeDebugMessage("CHRIS dbg >> getPinControlListByConnectorSignal: {} - {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                signalControl = connector['pinctrl'].get(connectorSignal)
                if signalControl != None:
                    if self.isPinSignal(signalControl):
                        # Single pin signal
                        pinControlList.append(('gpio', signalControl))
                    else:
                        for signalId, pinControl in signalControl.items():
                            # Multi pin signal
                            pinControlList.append((signalId, pinControl))
                return pinControlList
        else:
            return None

    def updatePinControlByConnector(self, connectorName, newPinControl):
        for connector in self.__currentConfig['connectors']:
            # self.__log.writeDebugMessage("SHD updatePinControlByConnector {} == {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                pinControlCurrent = connector['pinctrl']
                break

        # self.__log.writeDebugMessage("SHD updatePinControlByConnector pinControlCurrent 1: {}".format(pinControlCurrent))
        for signal, newConfig in newPinControl.items():
            if newConfig.get('name') != None:
                # Single Pin
                for key in newConfig:
                    conSignal = pinControlCurrent.get(signal)
                    if conSignal != None:
                        conValue = conSignal.get(key)
                        if conValue != None:
                            pinControlCurrent[signal][key] = newConfig[key]
            else:
                # Multi Pin
                for subSignal, newSubConfig in newConfig.items():
                    for key in newSubConfig:
                        pinControlCurrent[signal][subSignal][key] = newSubConfig[key]   

        # self.__log.writeDebugMessage("SHD updatePinControlByConnector pinControlCurrent 2: {}".format(pinControlCurrent))

    def restorePinControlByConnector(self, connectorName):
        connectorIndex = 0
        for connector in self.__currentConfig['connectors']:
            # self.__log.writeDebugMessage("CHRIS dbg >> restorePinControlByConnector: {} - {}".format(connector['name'], connectorName))
            if connector['name'] == connectorName:
                pinControlCurrent = connector['pinctrl']
                break
            else:
                connectorIndex = connectorIndex + 1

        # self.__log.writeDebugMessage("CHRIS dbg >> restorePinControlByConnector: connectorIndex: {}".format(connectorIndex))
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
        # self.__log.writeDebugMessage("SHD setConnectorConfig connectorName: {}, pinCtrl: {}".format(connectorName, pinCtrl))
        board = self.__db.getComponentByID(self.__interfaceID)
        
        # Update Pin Control of the Main Board by Connector
        self.updatePinControlByConnector(connectorName, pinCtrl)

        # Update Configuration Options by Connector
        signalList = self.getSignalListByConnectorName(connectorName)
        signalList.sort(reverse=True)
        # self.__log.writeDebugMessage("CHRIS dbg: setConnectorConfig signalList: {}".format(signalList))
        for signal in signalList:
            # Enable/Disable signals
            connectorSignalName = self.getConnectorSignalSymbolName(connectorName, signal)
            signalSymbol = board.getSymbolByID(connectorSignalName)
            if pinCtrl.get(signal) != None:
                # self.__log.writeDebugMessage("CHRIS dbg: setConnectorConfig Enable symbol: {}".format(connectorSignalName))
                signalSymbol.setValue(True)
                
                pinDescriptionList = self.getDescriptionListByConnectorSignal(connectorName, signal)
                # self.__log.writeDebugMessage("CHRIS dbg: setConnectorConfig pinDescriptionList: {}".format(pinDescriptionList))
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
                            # self.__log.writeDebugMessage("CHRIS dbg >> Handle SPI CS exception - subSignal: {}".format(subSignal.lower())) 
                            symbolName = self.__symbolNamesByConnector[connectorName][pinId]
                            shdSpiCSConfigSymbolName = "{}_{}".format(symbolName, "CSASGPIO")
                            # self.__log.writeDebugMessage("CHRIS dbg >> CS set Visible: {}".format(shdSpiCSConfigSymbolName))
                            signalSpiCsPinSymbol = board.getSymbolByID(shdSpiCSConfigSymbolName)
                            signalSpiCsPinSymbol.setVisible(True)

                    signalPinSymbol = board.getSymbolByID(self.__symbolNamesByConnector[connectorName][pinId])
                    signalPinSymbol.setLabel(label)

            # else:
            #     # self.__log.writeDebugMessage("CHRIS dbg: Disable symbol: {}".format(connectorSignalName))
            #     signalSymbol.setValue(False)
            #     signalSymbol.setVisible(False)

            # signalSymbol.setReadOnly(True)
            
    def resetConnectorConfig(self, connectorName):
        # self.__log.writeDebugMessage("SHD restoreConnections connectorName: {}".format(connectorName))
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
        # self.__log.writeDebugMessage("mainBoard handleMessage: {} args: {}".format(id, args))
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

        self.__db.activateComponents(["HarmonyCore"])

        self.__shdCheckCollisionSymbol = boardInterface.createBooleanSymbol("SHD_CHECK_COLLISIONS", None)
        self.__shdCheckCollisionSymbol.setLabel("")
        self.__shdCheckCollisionSymbol.setVisible(False)
        self.__shdCheckCollisionSymbol.setDependencies(self.__checkGlobalCollisions, ["SHD_CHECK_COLLISIONS"])
        
        symbol = boardInterface.createStringSymbol("SHD_MAINBOARD_NAME", None)
        symbol.setLabel("Board Name")
        symbol.setDefaultValue(self.__currentConfig.get('name'))
        symbol.setReadOnly(True)
        symbol.setHelp(shdMainBoardHelp)

        self.__pioPeripheralID = getDeviceGPIOPeripheral(self.__atdf)
        symbol = boardInterface.createStringSymbol("SHD_MAINBOARD_PIO_PERIPH", None)
        symbol.setLabel("PIO Peripheral")
        symbol.setDefaultValue(self.__pioPeripheralID)
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
        # self.__log.writeDebugMessage("CHRIS dbg >> boardInterfaces: {}".format(boardInterfaces))
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
                # self.__log.writeDebugMessage("CHRIS dbg >> boardInterfaces interface: {}".format(interface))
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
                        # self.__log.writeDebugMessage("CHRIS dbg >> option pinControlList: {}".format(pinControlList))
                        for pinControl in pinControlList:
                            # self.__log.writeDebugMessage("CHRIS dbg >> option pinControl: {}".format(pinControl))
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

                    pinControlList = self.getDescriptionListByInterface(interfaceIndex)
                    # self.__log.writeDebugMessage("CHRIS dbg >> pinControlList: {}".format(pinControlList))
                    for pinControl in pinControlList:
                        # self.__log.writeDebugMessage("CHRIS dbg >> pinControl: {}".format(pinControl))
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
            # self.__log.writeDebugMessage("CHRIS dbg >> interfaceDependencies: {}".format(interfaceDependencies))
            
            # Add collision data
            self.__collisionsByPinID = deepcopy(self.__symbolInterfaceByPin)
                
        # EXTERNAL CONNECTORS DEFINITIONS -------------------------------------
        boardConnectors = self.__currentConfig.get('connectors')
        if boardConnectors != None:
            # self.__log.writeDebugMessage("CHRIS dbg >> createMenuSymbol: SHD_MAINBOARD_CONNECTORS")
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
                # self.__log.writeDebugMessage("CHRIS dbg >> createMenuSymbol: {}".format(connectorSymbolName))
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
                    # self.__log.writeDebugMessage("CHRIS dbg >> createBooleanSymbol: {}".format(connectorSignalName))
                    shdConSignalSymbol = boardInterface.createBooleanSymbol(connectorSignalName, shdConnectorSymbol)
                    shdConSignalSymbol.setLabel(signal.upper())
                    shdConSignalSymbol.setDescription("Enable {} : {}".format(conName, signal.upper()))
                    shdConSignalSymbol.setDefaultValue(False)
                    shdConSignalSymbol.setHelp(shdMainBoardHelp)
                    self.__symbolInterfaces.setdefault(connectorSignalName, shdConSignalSymbol)
                    
                    pinDescriptionList = self.getDescriptionListByConnectorSignal(conName, signal)
                    for pinDescription in pinDescriptionList:
                        # self.__log.writeDebugMessage("CHRIS dbg >> pinDescription: {}".format(pinDescription))
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
                                # self.__log.writeDebugMessage("CHRIS dbg >> Handle SPI CS exception: {} {} {} {} {}".format(name, function, subSignal, pinNumber, pinId))
                                # Handle SPI CS exception
                                spiCSdetected = True
                            
                        shdConPinControlSymbolName = self.getConnectorSignalPinSymbolName(conName, signal, pinId)
                        # Store the Symbol name to be used in click Boards connection events
                        symbolNamesByPinId.setdefault(pinId, shdConPinControlSymbolName)
                        # self.__log.writeDebugMessage("CHRIS dbg >> symbolNamesByPinId: {}".format(symbolNamesByPinId))

                        # self.__log.writeDebugMessage("CHRIS dbg >> conPinControlName: ", conPinControlName)
                        # self.__log.writeDebugMessage("CHRIS dbg >> createCommentSymbol: {}".format(shdConPinControlSymbolName))
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
                            # self.__log.writeDebugMessage("CHRIS dbg >> createBooleanSymbol: {}".format(shdSpiCSConfigSymbolName))
                            shdSpiCSConfigSymbol = boardInterface.createBooleanSymbol(shdSpiCSConfigSymbolName, shdConPinControlSymbol)
                            shdSpiCSConfigSymbol.setLabel("Drive CS signal as GPIO")
                            shdSpiCSConfigSymbol.setDescription("Drive CS signal as GPIO")
                            shdSpiCSConfigSymbol.setDefaultValue(False)
                            shdSpiCSConfigSymbol.setHelp(shdMainBoardHelp)
                            self.__symbolInterfaces.setdefault(shdSpiCSConfigSymbolName, shdSpiCSConfigSymbol)

                            # self.__log.writeDebugMessage("CHRIS dbg >> spiCSdetected connectorSignalName: {} shdSpiCSConfigSymbolName: {}".format(connectorSignalName, shdSpiCSConfigSymbolName))
                            shdConPinControlSymbol.setDependencies(self.__showSymbol, [connectorSignalName, shdSpiCSConfigSymbolName])

                        else:
                            shdConPinControlSymbol.setDependencies(self.__showSymbol, [connectorSignalName])
                            
                    connectorDependencies.append(connectorSignalName)
                    
                self.__symbolNamesByConnector.setdefault(conName, symbolNamesByPinId)
                shdConnectorSymbol.setDependencies(self.__signalEnableCallback, connectorDependencies)
                # self.__log.writeDebugMessage("CHRIS dbg >> connectorDependencies: {}".format(connectorDependencies))

        # remove no collision data
        for key, value in self.__collisionsByPinID.items():
            if len(value) == 1:
                self.__collisionsByPinID.pop(key, value)

        # for key, symbolList in self.__symbolInterfaceByPin.items():
        #     self.__log.writeDebugMessage("CHRIS dbg >> self.__symbolInterfaceByPin: {}: {}".format(key, symbolList))

        # for key, value in self.__symbolNamesByConnector.items():
        #     self.__log.writeDebugMessage("CHRIS dbg >> self.__symbolNamesByConnector: {}: {}".format(key, value))

        # for key, value in self.__collisionsByPinID.items():
        #     self.__log.writeDebugMessage("CHRIS dbg >> self.__collisionsByPinID: {}: {}".format(key, value))

        # for key, value in self.__symbolPinByParent.items():
        #     self.__log.writeDebugMessage("CHRIS dbg >> self.__symbolPinByParent: {}: {}".format(key, value))

    def resetSignalConfiguration(self):
        # self.__log.writeDebugMessage("CHRIS dbg >> resetSignalConfiguration: {}".format(self.__configuredPins))
        for pinId in self.__configuredPins:
            pinControl = self.__pinControlByPinId.get(pinId)
            if pinControl != None:
                self.__clearPinConfig(pinControl) 