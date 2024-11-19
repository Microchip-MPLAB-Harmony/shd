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

def getConnectorPinNumberFromSignal(connectorCompatible, **kwargs):
    # print("SHD >> getPinNumberFromConnectorSpec", connector, kwargs)
    connectorPins = __connectorSpec.get(connectorCompatible)
    if connectorPins != None:
        signalGroup = kwargs.get('signalGroup')
        signalPin = kwargs.get('signalPin')
        # print("SHD >> getPinNumberFromConnectorSpec {} {}".format(signalGroup, signalPin))
        if (signalGroup != None):
            pinNumber = __connectorSpec.get(connectorCompatible).get(signalGroup).get(signalPin)
        else:
            pinNumber = __connectorSpec.get(connectorCompatible).get(signalPin)
    else:
        pinNumber = None

    return pinNumber

def getConnectorSignalMapMikroToBUSXplainPro():
    # Signal Map : {mikroBus, XplainPro}
    signalMap = {}
    signalMap.setdefault('an', 'adc plus')
    signalMap.setdefault('rst', 'gpio1')
    signalMap.setdefault('pwm', 'pwm plus')
    signalMap.setdefault('int', 'irq')

    return signalMap
    
def getConnectorSignalMapXplainProToMikroBUS():
    # Signal Map : {XplainPro, mikroBus}
    signalMap = {}
    signalMap.setdefault('adc plus', 'an')
    signalMap.setdefault('gpio1', 'rst')
    signalMap.setdefault('pwm plus', 'pwm')
    signalMap.setdefault('irq', 'int')
    signalMap.setdefault('adc minus', None)
    signalMap.setdefault('gpio2', None)
    signalMap.setdefault('pwm minus', None)
    signalMap.setdefault('gpio ss', None)

    return signalMap
