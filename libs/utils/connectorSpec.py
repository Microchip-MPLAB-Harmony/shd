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
    },
    'rmii': {
        'ethphy': {
            'txen': 1,
            'txd0': 2,
            'txd1': 3,
            'refck': 8,
            'rxd1': 15,
            'rxd0': 16,
            'rxer': 17,
            'rxdv': 18,
            'mdc': 19,
            'mdio': 20,
        },
        'nint': 21,
        'nrst': 22,
        'spi': {
            'cs': 11,
            'sck': 12,
            'miso': 5,
            'mosi': 4
        },
        'gpio0': 23,
        'gpio1': 14,
        'gpio2': 13,
    },
    'rgmii': {
        'ethphy': {
            'gmdc': 45,
            'gmdio': 47,
            'g125ck': 62,
            'gtxen': 93,
            'gtxck': 97,
            'gtx0': 101,
            'gtx1': 105,
            'gtx2': 109,
            'gtx3': 113,
            'grxdv': 117,
            'grxck': 121,
            'grx0': 125,
            'grx1': 129,
            'grx2': 133,
            'grx3': 137,
        },
        'spi': {
            'miso': 31,
            'mosi': 33,
            'sck': 35,
            'cs': 38,
        },
        'i2c': {
            'scl': 39,
            'sda': 41,
        },
        'nrst': 42,
        'nint': 49,
    },
    'm2': {
        'usb': {
            'usb_dp': 3,
            'usb_dm': 5,
        },
        'pcm': {
            'clk': 8,
            'sync': 10,
            'out': 12,
            'in': 14,
        },
        'i2s': {
            'sck': 8,
            'ws': 10,
            'sdout': 12,
            'sdin': 14,
        },
        'spi': {
            'sck': 11,
            'miso': 13,
            'cs': 15,
            'mosi': 17
        },
        'sdio': {
            'ck': 9,
            'cmd': 11,
            'dat0': 13,
            'dat1': 15,
            'dat2': 17,
            'dat3': 19,
        },
        'host_wake': 21,
        'usart_wake': 20,
        'usart': {
            'tx': 22,
            'rx': 32,
            'rts': 34,
            'cts': 36
        },
        'vendor': {
            'strap1': 38,
            'wake': 40,
            'strap2': 42
        },
        'coex': {
            'coex3': 44,
            'txd': 46,
            'rxd': 48
        },
        'susclk': 50,
        'mbus': {
            'pta_bt_prio': 44,
            'pta_wlan_active': 46,
            'pta_bt_active': 48
        },
        'nrst': 54,
        'i2c': {
            'sda': 58,
            'scl': 60
        },
        'alert': 62
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
