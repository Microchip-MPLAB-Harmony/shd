# def getInstanceNameFromMIPS(Database, ATDF, function):
#     params = dict()
#     params.setdefault('pinFunction', function)
#     symbolDict = Database.sendMessage("core", "PIN_INSTANCE_NAME", params)
#     return symbolDict.get('instanceName')

def getDeviceFunctionListByPinId(Database, ATDF, pinId):
    functionList = []
    family = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("family")
    architecture = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("architecture")
    if architecture == "MIPS":
        params = dict()
        params.setdefault('pinName', pinId)
        symbolDict = Database.sendMessage("core", "PIN_FUNCTION_LIST", params)
        functionList = list(symbolDict.get('pinName'))
        
    else:
        peripheralList = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildrenByName("module")
        for module in peripheralList:
            moduleName = module.getAttribute("name")
            if 'PIO' in moduleName or 'GPIO' in moduleName or 'PORT' in moduleName:
                continue

            instanceList = module.getChildrenByName("instance")
            for instance in instanceList:
                instanceName = instance.getAttribute("name")
                # print("SHD >> getDeviceFunctionListByPinId instanceName:{}".format(instanceName))
                foundSignal = False
                signalsNodes = instance.getChildrenByName("signals")
                for signalsNode in signalsNodes:
                    signalList = signalsNode.getChildrenByName("signal")
                    signalFunctionPrev = None
                    for signal in signalList:
                        signalPad = signal.getAttribute("pad")
                        # print("SHD >> getDeviceFunctionListByPinId signalPad1:{}".format(signalPad))
                        
                        # Adapt nomeclature used in Pin Configurator (PlugIn) for WBZ devices
                        if "WBZ" in family:
                            signalPad = signalPad.replace("P", "R")

                        # print("SHD >> getDeviceFunctionListByPinId signalPad2:{} = {}".format(signalPad, pinId))
                             
                        # Handle multiple signals on the same pad
                        if pinId == signalPad:
                            signalFunction = signal.getAttribute("function")
                                
                            # print("SHD >> getDeviceFunctionListByPinId signalFunction:{} -> {}".format(signalFunctionPrev, signalFunction))
                            if signalFunction != signalFunctionPrev:
                                if signalFunctionPrev != None:
                                    functionList.append(functionName)
                                    # print("SHD >> getDeviceFunctionListByPinId functionList1:{}".format(functionList))
                                functionName = "{}_".format(instanceName)
                                signalFunctionPrev = signalFunction
                                foundSignal = False

                            # print("SHD >> getDeviceFunctionListByPinId functionName1:{}".format(functionName))
                            
                            if foundSignal:
                                functionName += '/'
                                # Handle MCSPI exception
                                if instanceName == 'MCSPI':
                                    functionName += 'MCSPI_'

                            # print("SHD >> getDeviceFunctionListByPinId functionName2:{}".format(functionName))
                                
                            groupName = signal.getAttribute("group")
                            groupNameSplitted = groupName.split("_")
                            if (len(groupNameSplitted) > 1) and (groupNameSplitted[0] == instanceName):
                                # Remove instance from group when they are the same word (ie: flexcom0, flexcom0_io)
                                groupName = "_".join(groupNameSplitted[1:])

                            functionName += groupName
                            
                            index = signal.getAttribute("index")
                            if index != None:
                                functionName += index
                                
                            # print("SHD >> getDeviceFunctionListByPinId functionName3:{}".format(functionName))
                            
                            foundSignal = True

                            if "FLEXCOM" in instanceName:
                                functionList.append(functionName)
                                # print("SHD >> getDeviceFunctionListByPinId Flexcom functionList:{}".format(functionList))
                                foundSignal = False

                if foundSignal:
                    functionList.append(functionName)
                    # print("SHD >> getDeviceFunctionListByPinId foundSignal functionList:{}".format(functionList))

    functionList.append('GPIO')
            
    return sorted(functionList)

def getDevicePinMap(Database, ATDF):
    pinMap = dict()
    # Send message to core to get available pins
    availablePinDictionary = {}
    availablePinDictionary = Database.sendMessage("core", "PIN_LIST", availablePinDictionary)
    for pinNumber, pinId in availablePinDictionary.items():
        pinMap[str(pinId)] = int(pinNumber)

    return pinMap

def getDeviceGPIOPeripheral(ATDF):
    pioPeripheral = 'NOT_SUPPORTED'
    # Extract Peripherals from ATDF
    peripheralList = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildren()
    for peripheral in peripheralList:
        peripheralName = peripheral.getAttribute("name")
        if peripheralName in ['PIO', 'PORT', 'GPIO']:
            pioPeripheral = "{}_{}".format(peripheralName, peripheral.getAttribute("id"))
            break

    return pioPeripheral    

def __getDeviceFLEXCOMPeripheral(ATDF):
    pioPeripheral = 'NOT_SUPPORTED'
    # Extract Peripherals from ATDF
    peripheralList = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildren()
    for peripheral in peripheralList:
        peripheralName = peripheral.getAttribute("name")
        if peripheralName in ['FLEXCOM']:
            pioPeripheral = "{}_{}".format(peripheralName, peripheral.getAttribute("id"))
            break

    return pioPeripheral  

def adaptDevicePeripheralDependencies(ATDF, dependencyList):
    architecture = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("architecture")
    if architecture == "MIPS":
        # family = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("family")
        # if family == "PIC32MK":
        return dependencyList
    else:
        newDependencyList = {}
        pioPeriphID = getDeviceGPIOPeripheral(ATDF)
        flexcomID = __getDeviceFLEXCOMPeripheral(ATDF)
        # print("CHRIS dbg >> adaptDevicePeripheralDependencies {} - {}".format(pioPeriphID, flexcomID))
        if pioPeriphID == "PIO_11004" and flexcomID != 'NOT_SUPPORTED':
            for depId, capId in dependencyList.items():
                if "usart" in capId[:5]:
                    capId = capId.replace("usart", "flexcom")
                elif "spi" in capId[:3]:
                    capId = capId.replace("spi", "flexcom")
                elif "twi" in capId[:3]:
                    capId = capId.replace("twi", "flexcom")

                newDependencyList.setdefault(depId, capId)

            return newDependencyList
        else:
            return dependencyList
