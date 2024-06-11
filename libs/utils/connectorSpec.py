__connectorSpec = {
    'mikrobus': {
        'an': 1, 
        'rst':2, 
        'spi': {
            'cs': 3, 
            'sck':4, 
            'miso': 5, 
            'mosi': 6
        }, 
        'pwm': 16, 
        'int': 15, 
        'uart': {
            'tx': 13, 
            'rx': 14,
        }, 
        'i2c': {
            'sda': 11, 
            'scl': 12
        }
    },
    'xplainpro': {
        'adc plus': 3,
        'adc minus': 4,
        'gpio1': 5,
        'gpio2': 6,
        'pwm plus': 7,
        'pwm minus': 8,
        'irq': 9,
        'gpio ss': 10,
        'spi': {
            'cs': 15,
            'sck': 18,
            'miso': 17,
            'mosi': 16
        }, 
        'uart': {
            'tx': 14,
            'rx': 13,
        }, 
        'i2c': {
            'sda': 11,
            'scl': 12,
        }
    },
    'arduino': {
        'adc0': 9,
        'adc1': 10,
        'adc2': 11,
        'adc3': 12,
        'adc4': 13,
        'adc5': 14,
        'spi': {
            'cs': 25,
            'sck': 28,
            'miso': 27,
            'mosi': 26
        }, 
        'uart': {
            'tx': 16,
            'rx': 15,
        }, 
        'i2c': {
            'sda': 31,
            'scl': 32,
        },
        'd2': 17,
        'd3': 18,
        'd4': 19,
        'd5': 20,
        'd6': 21,
        'd7': 22,
        'd8': 23,
        'd9': 24
    },
    'highspeedI2Cslave': {
        'gpio': 3,
        'i2c': {
            'sda': 5,
            'scl': 6,
        }
    },
}
__drvDependencies = {
    'drv_i2c': 'I2C',
    'drv_spi': 'SPI',
    'drv_usart': 'UART',
    'drv_sst26': 'SQI',
    'drv_mx25l': 'SQI',
    'drv_at24': 'I2C',
    'drv_at25': 'SPI',
    'drv_at25df': 'SPI',
    'drv_sdmmc': 'SDHC',
    'a_drv_i2s': 'I2S',
    'drv_sdspi': 'SPI',
    'drvPlcPhy': 'SPI',
    'stdio': 'UART'
}

def __checkSubstringList(substringList, string):
    for substring in substringList:
        if substring in string:
            return True

    return False

def getConnectorPinNumberFromSignal(connectorCompatible, **kwargs):
    # print("CHRIS dbg: getPinNumberFromConnectorSpec", connector, kwargs)
    connectorPins = __connectorSpec.get(connectorCompatible)
    if connectorPins != None:
        signalGroup = kwargs.get('signalGroup')
        signalPin = kwargs.get('signalPin')
        # print("CHRIS dbg: getPinNumberFromConnectorSpec {} {}".format(signalGroup, signalPin))
        if (signalGroup != None):
            pinNumber = __connectorSpec.get(connectorCompatible).get(signalGroup).get(signalPin)
        else:
            pinNumber = __connectorSpec.get(connectorCompatible).get(signalPin)
    else:
        pinNumber = None

    return pinNumber

def getConnectorSignalMapMikroBUSXplainPro():
    # Signal Map : {mikroBus, XplainPro}
    signalMap = {}
    signalMap.setdefault('an', 'adc plus')
    signalMap.setdefault('rst', 'gpio1')
    signalMap.setdefault('pwm', 'pwm plus')
    signalMap.setdefault('int', 'irq')

    return signalMap

def getAutoconnectTable(idDependency, idCapability):
    connectionTable = []
    for dep, signal in __drvDependencies.items():
        exception = False
        if dep in idDependency:
            connection = []
            # Add dependency
            connection.append(idDependency)
            # handle name exceptions
            if 'a_drv_i2s' == dep:
                depType = dep.replace('a_', '')
            elif 'audio_codec_ak495' in idDependency:
                depType = idCapability # could be I2C or I2S
            elif 'stdio' == dep:
                exception = True
                depType = "UART"
            else:
                depType = dep

            if exception == True:
                connection.append("{}".format(depType))
            else:
                connection.append("{}_{}_dependency".format(depType, signal))
            
            # Add capability
            # handle name exceptions
            connection.append(idCapability)
            if idCapability[:2] == 'a_':
                idCapability = idCapability.replace("a_", "")
            connection.append("{}_{}".format(idCapability.upper(), signal))
            
            connectionTable.append(connection)
    
    return connectionTable

def getDriverDependencyFromPinName(pinName):
    dep = ""
    string = pinName.upper()
    if __checkSubstringList(['MCSPI'], string) == True:
        dep = ""
    elif __checkSubstringList(['I2C', 'TWI', 'SDA', 'SCL'], string) == True:
        dep = "drv_i2c"
    elif __checkSubstringList(['SPI', 'MISO', 'MOSI', 'CS', 'SCK'], string) == True:
        dep = "drv_spi"
    elif __checkSubstringList(['UART', 'USART', 'VIRTUAL_COM'], string) == True:
        dep = "drv_usart"
        
    return dep
