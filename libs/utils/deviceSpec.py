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
            functionName = "{}_".format(instanceName)
            signalsNodes = instance.getChildrenByName("signals")
            for signalsNode in signalsNodes:
                signalList = signalsNode.getChildrenByName("signal")
                for signal in signalList:
                    if pinId == signal.getAttribute("pad"):
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

def getConfigDatabaseADC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
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
    
    # elif periphID == 'ADC_00755':
    # elif periphID == 'ADC_02486':
    # elif periphID == 'ADC_02805':
    # elif periphID == 'ADC_03620':
    # elif periphID == 'ADC_6489':
    # elif periphID == 'ADC_44073':
    # elif periphID == 'ADC_u2204':
    # elif periphID == 'ADC_u2247':
    # elif periphID == 'ADCHS_02508':
    # elif periphID == 'AFEC_11147':
    else:
        print("CHRIS dbg >> getConfigDatabaseADC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseDAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()
    channel = int(setting[-1])

    configDB = dict()
    configDB.setdefault('msgID', 'DAC_CONFIG_HW_IO')

    periphID = periphID.upper()
    if periphID == 'DAC_U2502':
        configDB.setdefault('config', channel)

    # elif periphID == 'DAC_U2214':
    # elif periphID == 'DAC_U2244':
    # elif periphID == 'DAC_CTRL_05063':
    else:
        print("CHRIS dbg >> getConfigDatabaseDAC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'AC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'AC_U2501':
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

    # elif periphID == 'AC_U2245':
    # elif periphID == 'AC_U225':
    else:
        print("CHRIS dbg >> getConfigDatabaseAC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseACC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'ACC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'ACC_04597':
        # get data configuration from setting in{n/p}{chn}
        accIndex = int(setting[-1])
        accPin = setting[-2] #'n' or 'p'
            
        configDB.setdefault('config', (accIndex, accPin, enable))

    # elif periphID == 'ACC_6490':
    else:
        print("CHRIS dbg >> getConfigDatabaseAC {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabasePWM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'PWM_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'PWM_6343':
        # get data configuration from setting in{n/p}{chn}
        accIndex = int(setting[-1])
        polarity = setting[-2] #'l' or 'h'
            
        configDB.setdefault('config', (accIndex, polarity, enable))

    # elif periphID == 'PWM_54':
    # elif periphID == 'PWM_6044':
    else:
        print("CHRIS dbg >> getConfigDatabasePWM {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseFLEXCOM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
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

    # elif periphID == 'FLEXCOM_11277':
    else:
        print("CHRIS dbg >> getConfigDatabaseFLEXCOM {} NOT FOUND!!!".format(periphID))

    return configDB

def getConfigDatabaseMCSPI(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    fnValue, pinNameValue, enable = settings
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

def getDeviceDriverConfigurationDBMessage(ATDF, settings):
    periphList = getDevicePeripheralList(ATDF)

    fnValue, pinNameValue, enable = settings
    # fnValue format -> '{}_{}'.format(componentID, setting)
    componentID = fnValue.split('_')[0].lower()
    driver = "".join(filter(lambda x: x.isalpha(), componentID))

    periphID = ""
    configDB = dict()
    params = dict()
    
    for peripheral in periphList:
        pName = peripheral.split('_')[0].lower()
        print("CHRIS dbg >> checking periph {}: {} = {}".format(peripheral, driver, pName))
        if driver == pName:
            periphID = peripheral
            params.setdefault('peripheral', peripheral)
            break

    if driver == 'adc':
        configDB = getConfigDatabaseADC(periphID, settings)
        
    elif driver == 'dac':
        configDB = getConfigDatabaseDAC(periphID, settings)
        
    elif driver == 'ac':
        configDB = getConfigDatabaseAC(periphID, settings)
        
    elif driver == 'acc':
        configDB = getConfigDatabaseACC(periphID, settings) 
               
    elif driver == 'pwm':
        configDB = getConfigDatabasePWM(periphID, settings)

    elif driver == 'flexcom':
        configDB = getConfigDatabaseFLEXCOM(periphID, settings)

    elif driver == 'mcspi':
        configDB = getConfigDatabaseMCSPI(periphID, settings)
        
    else:
        print("CHRIS dbg >> getDeviceDriverConfigurationDBMessage {} NOT FOUND!!!".format(driver))
        
    config = configDB.get('config')
    if config != None:
        msgID = configDB.get('msgID')
        params.setdefault('config', config)
        params.setdefault('enable', enable)
    else:
        print("CHRIS dbg >> getDeviceDriverConfigurationDBMessage error config {}".format(configDB))
        msgID = None

    return (componentID, msgID, params)