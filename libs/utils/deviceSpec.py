def getDeviceFunctionListByPinId(ATDF, pinId):
    functionList = []
    peripheralList = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildrenByName("module")
    for module in peripheralList:
        moduleName = module.getAttribute("name")
        if 'PIO' in moduleName:
            continue

        instanceList = module.getChildrenByName("instance")
        for instance in instanceList:
            instanceName = instance.getAttribute("name")
            foundSignal = False
            signalsNodes = instance.getChildrenByName("signals")
            for signalsNode in signalsNodes:
                signalList = signalsNode.getChildrenByName("signal")
                signalFunctionPrev = None
                for signal in signalList:
                    if pinId == signal.getAttribute("pad"):
                        signalFunction = signal.getAttribute("function")
                        if signalFunction != signalFunctionPrev:
                            if signalFunctionPrev != None:
                                functionList.append(functionName)
                            functionName = "{}_".format(instanceName)
                            signalFunctionPrev = signalFunction
                            foundSignal = False
                        
                        if foundSignal:
                            functionName += '/'
                            # Handle MCSPI exception
                            if instanceName == 'MCSPI':
                                functionName += 'MCSPI_'
                            
                        groupName = signal.getAttribute("group")
                        groupNameSplitted = groupName.split("_")
                        if groupNameSplitted[0] == instanceName:
                            groupName = "_".join(groupNameSplitted[1:])

                        functionName += groupName
                        
                        index = signal.getAttribute("index")
                        if index != None:
                            functionName += index
                            
                        foundSignal = True

                        if "FLEXCOM" in instanceName:
                            functionList.append(functionName)
                            functionName = "{}_".format(instanceName)
                            foundSignal = False

            if foundSignal:
                functionList.append(functionName)

    functionList.append('GPIO')
            
    return sorted(functionList)

def getDevicePinMap(Database, ATDF):
    pinMap = dict()
    # Extract Device Pin Map from ATDF
    packageName = str(Database.getSymbolValue("core", "COMPONENT_PACKAGE"))
    variants = ATDF.getNode("/avr-tools-device-file/variants").getChildren()
    for variant in variants:
        if packageName in variant.getAttribute("package"):
            pinOutName = variant.getAttribute("pinout")

    pinOut = ATDF.getNode("/avr-tools-device-file/pinouts/pinout@[name=\"" + str(pinOutName) + "\"]").getChildren()
    for pin in pinOut:
        pinMap[str(pin.getAttribute("pad"))] = int(pin.getAttribute("position"))

    return pinMap

def getDevicePeripheralList(ATDF):
    peripheralList = []
    # Extract Peripherals from ATDF
    peripherals = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildren()
    for peripheral in peripherals:
        pName = peripheral.getAttribute("name")
        pId = peripheral.getAttribute("id")
        if pId != None:
            periph = '{}_{}'.format(pName, pId)
        else:
            periph = pName
            
        peripheralList.append(periph)

    return peripheralList    

def getDeviceGPIOPeripheral(ATDF):
    pioPeripheral = 'NOT_SUPPORTED'
    # Extract Peripherals from ATDF
    peripheralList = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildren()
    for peripheral in peripheralList:
        peripheralName = peripheral.getAttribute("name")
        if peripheralName in ['PIO', 'PORT']:
            pioPeripheral = "{}_{}".format(peripheralName, peripheral.getAttribute("id"))
            break

    return pioPeripheral    

def getDeviceFLEXCOMPeripheral(ATDF):
    pioPeripheral = 'NOT_SUPPORTED'
    # Extract Peripherals from ATDF
    peripheralList = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals").getChildren()
    for peripheral in peripheralList:
        peripheralName = peripheral.getAttribute("name")
        if peripheralName in ['FLEXCOM']:
            pioPeripheral = "{}_{}".format(peripheralName, peripheral.getAttribute("id"))
            break

    return pioPeripheral  

def getConfigDatabaseADC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'ADC_CONFIG_HW_IO')

    periphID = periphID.upper()
    if periphID == 'ADC_U2500':
        if pinNameValue.split('_')[-1] == 'MINUS':
            muxInput = 'MUXNEG'
        else:
            muxInput = 'MUXPOS'

        if enable == True:
            # get ADC channel from setting
            channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        else:
            channel = -1

        configDB.setdefault('config', (channel, muxInput))

    elif periphID == 'ADC_44134':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        isNegInput = False
        if pinNameValue.split('_')[-1] == 'MINUS':
            isNegInput = True

        if isNegInput == True:
            if channel != 1 and channel != 3:
                print("ERROR in SHD Main Board configuration: Negative input is not permitted.[{}]".format(fnValue))
                return configDB
            
        configDB.setdefault('config', (channel, isNegInput, enable))

    elif periphID == 'AFEC_11147':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        isNegInput = False
        if pinNameValue.split('_')[-1] == 'MINUS':
            isNegInput = True

        if isNegInput == True:
            if channel % 2 == 0:
                print("ERROR in SHD Main Board configuration: Negative input is not permitted.[{}]".format(fnValue))
                return configDB
            
        configDB.setdefault('config', (channel, isNegInput, enable))
    
    elif periphID == 'ADC_U2204' or periphID == 'ADC_U2247':
        if pinNameValue.split('_')[-1] == 'MINUS':
            muxInput = 'MUXNEG'
        else:
            muxInput = 'MUXPOS'

        if enable == True:
            # get ADC channel from setting
            channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        else:
            channel = -1

        configDB.setdefault('config', (channel, muxInput, enable))
        
    elif periphID == 'ADC_6489':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        isNegInput = False
        if pinNameValue.split('_')[-1] == 'MINUS':
            isNegInput = True

        if isNegInput == True:
            if channel != 1 and channel != 3 and channel != 5 and channel != 7:
                print("ERROR in SHD Main Board configuration: Negative input is not permitted.[{}]".format(fnValue))
                return configDB
            
        configDB.setdefault('config', (channel, isNegInput, enable))

    
    # elif periphID == 'ADC_00755':
    # elif periphID == 'ADC_02486':
    # elif periphID == 'ADC_02805':
    # elif periphID == 'ADC_03620':
    # elif periphID == 'ADC_44073':
    # elif periphID == 'ADCHS_02508':
    # elif periphID == 'AFEC_11147':
    else:
        print("CHRIS dbg >> getConfigDatabaseADC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseDAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()
    channel = int("".join(filter(lambda x: x.isdigit(), setting)))

    configDB = dict()
    configDB.setdefault('msgID', 'DAC_CONFIG_HW_IO')

    periphID = periphID.upper()
    if periphID == 'DAC_U2502' or periphID == 'DAC_U2244' or periphID == 'DACC_11246' or periphID == 'DACC_6461':
        configDB.setdefault('config', channel)

    # elif periphID == 'DAC_U2214': # No need to send any config messages.
    # elif periphID == 'DAC_CTRL_05063':
    else:
        print("CHRIS dbg >> getConfigDatabaseDAC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'AC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'AC_U2501' or periphID == 'AC_U2245':
        # get AC comparator ID from pinNameValue
        comparatorID = int("".join(filter(lambda x: x.isdigit(), pinNameValue.split('_')[-2])))

        if pinNameValue.split('_')[-1] == 'MINUS':
            muxInput = 'MUXNEG'
        else:
            muxInput = 'MUXPOS'

        # get AC I/O pin from setting
        if enable == True:
            # get ADC channel from setting
            ioPin = int("".join(filter(lambda x: x.isdigit(), setting)))
        else:
            ioPin = -1
        
        configDB.setdefault('config', (comparatorID, muxInput, ioPin))

    # elif periphID == 'AC_U225':
    else:
        print("CHRIS dbg >> getConfigDatabaseAC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseACC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'ACC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'ACC_04597':
        # get data configuration from setting in{n/p}{chn}
        accIndex = int("".join(filter(lambda x: x.isdigit(), setting)))
        accPin = setting[-2] #'n' or 'p'
            
        configDB.setdefault('config', (accIndex, accPin, enable))

    # elif periphID == 'ACC_6490':
    else:
        print("CHRIS dbg >> getConfigDatabaseAC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabasePWM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'PWM_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'PWM_6343':
        # get data configuration from setting in{n/p}{chn}
        accIndex = int("".join(filter(lambda x: x.isdigit(), setting)))
        polarity = setting[-2] #'l' or 'h'
            
        configDB.setdefault('config', (accIndex, polarity, enable))

    # elif periphID == 'PWM_54':
    # elif periphID == 'PWM_6044':
    else:
        print("CHRIS dbg >> getConfigDatabasePWM {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseFLEXCOM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'FLEXCOM_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'FLEXCOM_11268':
        if setting == 'io3':
            configDB.setdefault('config', ('NPCS0', enable))
        elif setting == 'io4':
            configDB.setdefault('config', ('NPCS1', enable))
    elif periphID == 'FLEXCOM_11277':
        if 'npcs' in setting:
            configDB.setdefault('config', (setting.upper(), enable))
    else:
        print("CHRIS dbg >> getConfigDatabaseFLEXCOM {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseSERCOM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'SERCOM_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    mode = ""
    pinCtrl = dict()
    if periphID == 'SERCOM_U2201':
        pinCtrl.setdefault('signalId', signalId)
        pinCtrl.setdefault('padId', int(fnValue[-1]))
        
        if signalId in ['rx', 'tx', 'rts', 'cts', 'xck']:
            mode = "USART"
        elif signalId in ['cs', 'sck', 'miso', 'mosi']:
            mode = "SPI"

        if mode != "":
            configDB.setdefault('config', (mode, pinCtrl, enable))
    else:
        print("CHRIS dbg >> getConfigDatabaseSERCOM {} NOT FOUND!!!".format(periphID))
    
    return configDB

def getConfigDatabaseMCSPI(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'MCSPI_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'MCSPI_04462':
        if 'npcs' in setting:
            configDB.setdefault('config', (setting.upper(), enable))

    else:
        print("CHRIS dbg >> getConfigDatabaseMCSPI {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseEIC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'EIC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'EIC_U2254':
        channel = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (channel, enable))

    elif periphID == 'EIC_U2217' or periphID == 'EIC_U2804':
        channel = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (channel, enable))
        
    # elif periphID == 'EIC_44139':
    # elif periphID == 'EVIC_01166':
    # elif periphID == 'EVIC_02907':

    else:
        print("CHRIS dbg >> getConfigDatabaseEIC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseSUPC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'SUPC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'SUPC_U2407' or periphID == 'SUPC_U2117':
        output = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (output, enable))
        configDB.setdefault('compID', componentID)

    elif periphID == 'SUPC_04670':
        # Enable WKUP pins
        input = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (input, enable))
        configDB.setdefault('compID', "core")
        
    elif periphID == 'SUPC_11228' or periphID == 'SUPC_6452':
        # Enable WKUP pins
        input = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (input, enable))
        configDB.setdefault('compID', componentID)
        
    # elif periphID == 'SUPC_03926':
    # elif periphID == 'SUPC_44082':

    else:
        print("CHRIS dbg >> getConfigDatabaseSUPC {} NOT FOUND!!!".format(periphID))

    return configDB

def getDevicePLIBConfigurationDBMessage(ATDF, settings):
    periphList = getDevicePeripheralList(ATDF)

    signalId, fnValue, pinNameValue, enable = settings
    # fnValue format -> '{}_{}'.format(componentID, setting)
    componentID = fnValue.split('_')[0].lower()
    driver = "".join(filter(lambda x: x.isalpha(), componentID))

    # Adapt driver according to the peripheral PIO ID
    (componentID, driver) = adaptDevicePeripheralDependencies(ATDF, [componentID, driver])

    periphID = ""
    configDB = dict()
    params = dict()
    
    for peripheral in periphList:
        pName = peripheral.split('_')[0].lower()
        # print("CHRIS dbg >> checking periph {}: {} = {}".format(peripheral, driver, pName))
        if driver == pName:
            periphID = peripheral
            params.setdefault('peripheral', peripheral)
            break

    if driver == 'adc' or driver == 'afec':
        configDB = getConfigDatabaseADC(periphID, settings)
        
    elif driver == 'dac' or driver == 'dacc':
        configDB = getConfigDatabaseDAC(periphID, settings)
        
    elif driver == 'ac':
        configDB = getConfigDatabaseAC(periphID, settings)
        
    elif driver == 'acc':
        configDB = getConfigDatabaseACC(periphID, settings) 
               
    elif driver == 'pwm':
        configDB = getConfigDatabasePWM(periphID, settings)

    elif driver == 'flexcom':
        configDB = getConfigDatabaseFLEXCOM(periphID, settings)

    elif driver == 'sercom':
        configDB = getConfigDatabaseSERCOM(periphID, settings)

    elif driver == 'mcspi':
        configDB = getConfigDatabaseMCSPI(periphID, settings)
        
    elif driver == 'eic':
        configDB = getConfigDatabaseEIC(periphID, settings)
        
    elif driver == 'supc':
        configDB = getConfigDatabaseSUPC(periphID, settings)
        componentID = configDB.get('compID')
    # else:
    #     print("CHRIS dbg >> getDevicePLIBConfigurationDBMessage {} NOT FOUND!!!".format(driver))
        
    config = configDB.get('config')
    if config != None:
        msgID = configDB.get('msgID')
        params.setdefault('config', config)
        params.setdefault('enable', enable)
    else:
        # print("CHRIS dbg >> getDevicePLIBConfigurationDBMessage error config {}".format(configDB))
        msgID = None

    return (componentID, msgID, params)

def getConfigDatabaseDrvPlcPhy(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    if functionValue.lower() == "gpio" or signalId == "cs":
        configDB.setdefault('msgID', 'DRVPLCPHY_CONFIG_HW_IO')
        configDB.setdefault('config', (signalId, pinId, functionValue, nameValue, enable))
    
    return configDB

def getDeviceDriverConfigurationDBMessage(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings
    
    componentID = driver
    configDB = dict()
    params = dict()

    if driver == 'drvPlcPhy':
        configDB = getConfigDatabaseDrvPlcPhy(settings)
    # else:
    #     print("CHRIS dbg >> getDeviceDriverConfigurationDBMessage {} NOT FOUND!!!".format(driver))
        
    config = configDB.get('config')
    if config != None:
        msgID = configDB.get('msgID')
        params.setdefault('config', config)
    else:
        # print("CHRIS dbg >> getDeviceDriverConfigurationDBMessage error config {}".format(configDB))
        msgID = None

    return (componentID, msgID, params)

def adaptDevicePeripheralDependencies(ATDF, dependencyList):
    newDependencyList = []
    pioPeriphID = getDeviceGPIOPeripheral(ATDF)
    flexcomID = getDeviceFLEXCOMPeripheral(ATDF)
    # print("CHRIS dbg >> adaptDevicePeripheralDependencies {} - {}".format(pioPeriphID, flexcomID))
    if pioPeriphID == "PIO_11004" and flexcomID != 'NOT_SUPPORTED':
        for dependency in dependencyList:
            if "usart" in dependency[:5]:
                dependency = dependency.replace("usart", "flexcom")
            elif "spi" in dependency[:3]:
                dependency = dependency.replace("spi", "flexcom")
            elif "twi" in dependency[:3]:
                dependency = dependency.replace("twi", "flexcom")

            newDependencyList.append(dependency)

        return newDependencyList
    else:
        return dependencyList
