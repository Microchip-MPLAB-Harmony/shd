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
    'pim_mc': {
        'led2': 1,
        'pwm1h3': 3,
        'mclr': 13,
        'fault': 18,
        'tx/flt': 19,
        'vm3': 20,
        'vm2': 21,
        'vm1': 22,
        'ibus/vbus': 23,
        'ib/pot': 24,
        'ia/pfc': 25,
        'pgc': 26,
        'pgd': 27,
        'recneutr': 28,
        'pot': 32,
        'gen2': 34,
        'vbus/dcbus': 35,
        'vacvol2': 38,
        'ipfcshunt': 39,
        'pfcl': 40,
        'mon1/pot': 41,
        'mon2': 42,
        'mon3/ibus': 43,
        'hallb/qeb': 47,
        'hallc/indx': 48,
        'usart': {
            'rx': 49,
            'tx': 50,
        },
        'usb': {
            'usbp': 51,
            'usbd': 52,
        },
        'fltout2': 58,
        'fltout1': 59,
        'led1': 60,
        'home': 61,
        'ibus+': 66,
        'ibus-': 67,
        'lincs/btn': 68,
        'linfault': 69,
        'rx1': 70,
        'pfcpwm': 71,
        'usbrx/ha/qea': 72,
        'ib+': 73,
        'ia+': 74,
        'usbtx/hb/qeb': 76,
        'cantx/hall c': 77,
        'canrx/pfc pwm': 78,
        'vaczx': 79,
        'halla/qea': 80,
        'gen1': 82,
        'btn1': 83,
        'btn2/tx1': 84,
        'can': {
            'rx': 87,
            'tx': 88,
        },
        'pwm1l1': 93,
        'pwm1h1': 94,
        'pwm1l2': 98,
        'pwm1h2': 99,
        'pwm1l3': 100
    },
    'pic32mx_eth_sk2_exp120': {
        'trace': {
            'sda': 5,
            'scl': 6,
        },
        'gpio': 3,
        'i2c': {
            'sda': 5,
            'scl': 6,
        }
    }
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
    'stdio': 'UART',
    'sys_console': 'UART',
    'X2CScope': 'UART',
    'pmsm_foc': 'ADC',
    'drvGmac': 'PHY',
    'le_gfx_lcdc': 'LCDC',
    'drvEmac': 'PHY'
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

def getAutoconnectTable(family, idDependency, idCapability):
    connectionTable = []
    print("CHRIS dbg >> getAutoconnectTable dep:{} cap:{}".format(idDependency, idCapability)) 
    for depId, capId in __drvDependencies.items():
        exception = False
        if depId in idDependency:
            connection = []
            # Add dependency
            connection.append(idDependency)
            # handle name exceptions
            if 'a_drv_i2s' == depId:
                depType = depId.replace('a_', '')
            elif 'audio_codec_ak495' in idDependency:
                depType = idCapability # could be I2C or I2S
            elif 'stdio' == depId:
                exception = True
                depType = "UART"
            elif 'X2CScope' == depId:
                exception = True
                depType = "x2cScopeUartDependency"
            elif 'pmsm_foc' == depId:
                exception = True
                plib = "".join(filter(lambda x: x.isalpha(), idCapability.lower()))
                if plib == 'adc' or plib == 'afec' or plib == 'adchs':
                    depType = "pmsmfoc_ADC"
                elif plib == 'tcc' or plib == "pwm" or plib == "mcpwm":
                    depType = "pmsmfoc_PWM"
                    capId = "PWM"
                elif plib == 'dsci':
                    depType = "pmsmfoc_X2CSCOPE"
                else:
                    print("CHRIS dbg >> getAutoconnectTable skip pmsm_foc: plib:{}".format(plib)) 
                    continue
                
                print("CHRIS dbg >> getAutoconnectTable check pmsm_foc: plib:{}, depType{}".format(plib, depType)) 
            elif 'drvGmac' == depId:
                exception = True
                # print("CHRIS dbg >> getAutoconnectTable drvGmac: family:{} - depId:{}".format(family, depId)) 
                if family == "SAMA":
                    instance = "".join(filter(lambda x: x.isdigit(), idDependency))
                    depType = "GMAC{}_PHY_Dependency".format(instance)
                else:
                    depType = "ETH_PHY_Dependency"
            elif 'le_gfx_lcdc' == depId:
                exception = True
                depType = "LCDC"
            elif 'drvEmac' == depId:
                exception = True
                # get Instance number
                instance = "".join(filter(lambda x: x.isdigit(), idDependency))
                depType = "MAC_PHY_Dependency{}".format(instance)
            else:
                depType = depId

            if exception == True:
                connection.append("{}".format(depType))
            else:
                connection.append("{}_{}_dependency".format(depType, capId))
            
            # Add capability
            # handle name exceptions
            exception = False
            connection.append(idCapability)
            if idCapability == "i2c_bb":
                idCapability = "I2C"
                exception = True
            elif family == "PIC32MX":
                if "a_i2s" in capId[:5]:
                    instance = idCapability[-1]
                    idCapability = "I2S{}_I2S".format(instance)
                    exception = True
            else:
                if idCapability[:2] == 'a_':
                    idCapability = idCapability.replace("a_", "")
                elif 'drvExtPhy' in idCapability:
                    exception = True
                    idCapability = "lib{}".format(idCapability)

            if exception == True:
                connection.append("{}".format(idCapability))
            else:
                connection.append("{}_{}".format(idCapability.upper(), capId))
            
            connectionTable.append(connection)

    print("CHRIS dbg >> getAutoconnectTable connectionTable:{}".format(connectionTable)) 
    return connectionTable

def getDriverDependencyFromPinName(pinName):
    dep = ""
    string = pinName.upper()
    if __checkSubstringList(['MCSPI'], string) == True:
        dep = ""
    elif __checkSubstringList(['I2C', 'TWI', 'SDA', 'SCL', 'TWD', 'TWCK'], string) == True:
        dep = "drv_i2c"
    elif __checkSubstringList(['SPI', 'MISO', 'MOSI', 'CS', 'SCK'], string) == True:
        if __checkSubstringList(['LIN'], string) == True:
            dep = ""
        else:
            dep = "drv_spi"
    elif __checkSubstringList(['UART', 'USART', 'VIRTUAL_COM'], string) == True:
        dep = "drv_usart"
        
    return dep

def checkPlibFromSignalConnector(plib, signal):
    if plib.lower() == signal.lower():
        return True
    elif __checkSubstringList(['i2c', 'uart', 'spi'], signal.lower()) == True:
        # Check if Plib supports these communication signals
        if __checkSubstringList(['i2c', 'twi', 'spi', 'sercom', 'flexcom'], plib.lower()) == True:
            return True

    return False
