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
from deviceSpec import adaptDevicePeripheralDependencies

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
    'drvG3MacRt': 'SPI',
    'stdio': 'UART',
    'sys_console': 'UART',
    'X2CScope': 'UART',
    'pmsm_foc': 'ADC',
    'le_gfx_lcdc': 'LCDC',
    'drvPic32mEthmac': 'PHY',
    'ethmac': 'PHY',
    'gmac': 'PHY',
    'drvEmac': 'PHY',
    'drvGmac': 'PHY',
    'le_gfx_slcdc': 'SLCDC',
    'le_gfx_slcd': 'SLCD',
    'ptc': 'ADC',
    'drvWifiWincS02': 'SPI',
    'drvWifiWinc': 'SPI',
    'RNBD_Dependency' : 'UART',
    'atecc108a': 'I2C',
    'atecc508a': 'I2C',
    'atecc608': 'I2C',
    'atsha204a': 'I2C',
    'atsha206a': 'SWI',
    'ecc204': 'I2C',
    'sha104': 'I2C',
    'sha105': 'I2C',
    'ta010': 'I2C',
    'srv_pvddmon': 'ADC'
}

def __checkSubstringList(substringList, string):
    for substring in substringList:
        if substring in string:
            return True

    return False

def __getDevicePeripheralList(ATDF):
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

def __getConfigDatabaseADC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
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
            
        # get ADC channel from setting
        if setting[0] == "x":
            # PTC connection
            channel = "PTC"
        else:
            channel = int("".join(filter(lambda x: x.isdigit(), setting)))

        configDB.setdefault('config', (channel, muxInput, enable))
        
    elif periphID == 'ADC_U2204' or periphID == 'ADC_U2247':
        if "VREF" in pinNameValue:
            setting = fnValue.split('_')[-1]
        else:
            setting = fnValue.split('_')[-1].split('/')[0]
            
        if pinNameValue.split('_')[-1] == 'MINUS':
            muxInput = 'MUXNEG'
        else:
            muxInput = 'MUXPOS'
            
        configDB.setdefault('config', (setting, muxInput, enable))

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

    elif periphID == 'ADCHS_02508':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))

        configDB.setdefault('config', (channel, enable))

    elif periphID == 'ADC_03620':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
            
        configDB.setdefault('config', (channel, enable))
    
    elif periphID == 'ADC_44073':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        isNegInput = False
        if pinNameValue.split('_')[-1] == 'MINUS':
            isNegInput = True

        if isNegInput == True:
            if (channel % 2) == 1:
                print("ERROR in SHD Main Board configuration: Negative input is not permitted.[{}]".format(fnValue))
                return configDB
            
        configDB.setdefault('config', (channel, isNegInput, enable))
        
    elif periphID == 'ADC_00755':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        isNegInput = False
        if pinNameValue.split('_')[-1] == 'MINUS':
            isNegInput = True

        if isNegInput == True and channel != 1:
            print("ERROR in SHD Main Board configuration: Negative input is not permitted.[{}]".format(fnValue))
            return configDB
            
        configDB.setdefault('config', (channel, isNegInput, enable))

    elif periphID == 'ADC_02805':
        # get ADC channel from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        configDB.setdefault('config', (channel, enable))

    elif periphID == 'ADC_03459':
        channel = setting.split("an")[-1]
        configDB.setdefault('config', (channel, enable))

    # elif periphID == 'ADC_02486':
    # else:
        # print("SHD >> getConfigDatabaseADC {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseDAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'DAC_CONFIG_HW_IO')

    periphID = periphID.upper()
    if periphID == 'DACC_11246' or periphID == 'DACC_6461':
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        configDB.setdefault('config', channel)
    elif periphID == 'DAC_U2502' or periphID == 'DAC_U2244' or periphID == 'DAC_U2214':
        configDB.setdefault('config', setting)

    # elif periphID == 'DAC_CTRL_05063':
    # else:
    #     print("SHD >> getConfigDatabaseDAC {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
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
    # else:
    #     print("SHD >> getConfigDatabaseAC {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseACC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
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
    # else:
    #     print("SHD >> getConfigDatabaseAC {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabasePWM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'PWM_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'PWM_6343':
        # get data configuration from setting in{n/p}{chn}
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        polarity = setting[-2] #'l' or 'h'
            
        configDB.setdefault('config', (channel, polarity, enable))

    elif periphID == 'MCPWM_01477':
        # get data configuration from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        polarity = setting[-1] #'l' or 'h'
            
        configDB.setdefault('config', (channel, polarity, enable))

    elif periphID == 'PWM_6044':
        # get pwm channel
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
            
        configDB.setdefault('config', (channel, enable))

    elif periphID == 'PWM_04302':
        # get data configuration from setting
        channel = int("".join(filter(lambda x: x.isdigit(), setting)))
        polarity = setting[-1] #'l' or 'h'
            
        configDB.setdefault('config', (channel, polarity, enable))
        
    # elif periphID == 'PWM_54':

    # else:
    #     print("SHD >> getConfigDatabasePWM {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseFLEXCOM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()

    mode = ""
    cs = ""
    if signalId in ['rx', 'tx', 'rts', 'cts', 'xck']:
        mode = "USART"
    elif signalId in ['cs', 'sck', 'miso', 'mosi']:
        mode = "SPI"
    elif signalId in ['sda', 'scl']:
        mode = "I2C"
    
    periphID = periphID.upper()
    if periphID == 'FLEXCOM_11268':
        if setting == 'io3':
            cs = 'NPCS0'
        elif setting == 'io4':
            cs = 'NPCS1'
    elif periphID == 'FLEXCOM_11277':
        if 'npcs' in setting:
            cs = setting.upper()
    # else:
    #     print("SHD >> getConfigDatabaseFLEXCOM {} NOT FOUND!!!".format(periphID))

    configDB.setdefault('msgID', 'FLEXCOM_CONFIG_HW_IO')
    configDB.setdefault('config', (mode, cs, enable))

    return configDB

def __getConfigDatabaseSERCOM(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'SERCOM_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    mode = ""
    pinCtrl = dict()
    if periphID == 'SERCOM_U2201' or periphID == 'SERCOM_03715'  or periphID == 'SERCOM_04707':
        # Add exceptions for SERCOM_SDL/SDA in WBZ family
        # if setting == 'sda' or setting == 'scl':
        #     return configDB
        
        pinCtrl.setdefault('signalId', signalId)
        pinCtrl.setdefault('padId', int(fnValue[-1]))
        
        if signalId in ['rx', 'tx', 'rts', 'cts', 'xck']:
            mode = "USART"
        elif signalId in ['cs', 'sck', 'miso', 'mosi']:
            mode = "SPI"
        elif signalId in ['sda', 'scl']:
            mode = "I2C"

        if mode != "":
            configDB.setdefault('config', (mode, pinCtrl, enable))
    # else:
    #     print("SHD >> getConfigDatabaseSERCOM {} NOT FOUND!!!".format(periphID))
    
    return configDB

def __getConfigDatabaseMCSPI(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'MCSPI_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'MCSPI_04462':
        if 'npcs' in setting:
            configDB.setdefault('config', (setting.upper(), enable))

    # else:
    #     print("SHD >> getConfigDatabaseMCSPI {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseEIC(periphID, settings, intMode):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    
    periphID = periphID.upper()
    channel = ""
    if periphID == 'EIC_U2254' or periphID == 'EIC_04714':
        if "NMI" in setting.upper():
            channel = "NMI"
        else:
            channel = "".join(filter(lambda x: x.isdigit(), setting))
        
    elif periphID == 'EIC_U2217' or periphID == 'EIC_U2804' or periphID == 'EIC_03706':
        if "NMI" in setting.upper():
            channel = "NMI"
        else:
            channel = "".join(filter(lambda x: x.isdigit(), setting))
        
    elif periphID == 'EIC_44139':
        channel = "".join(filter(lambda x: x.isdigit(), setting))

    # else:
    #     print("SHD >> getConfigDatabaseEIC {} NOT FOUND!!!".format(periphID))

    if channel != "":
        configDB.setdefault('msgID', 'EIC_CONFIG_HW_IO')
        configDB.setdefault('config', (channel, intMode, enable))

    return configDB

def __getConfigDatabaseAIC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'AIC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'AIC_11051':
        configDB.setdefault('config', (pinId, enable))
        componentID = "core"
        
    # else:
    #     print("SHD >> getConfigDatabaseAIC {} NOT FOUND!!!".format(periphID))

    return componentID, configDB

def __getConfigDatabaseSUPC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'SUPC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'SUPC_U2407' or periphID == 'SUPC_U2117':
        output = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (output, enable))

    elif periphID == 'SUPC_04670':
        # Enable WKUP pins
        input = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (input, enable))
        componentID = "core"
        
    elif periphID == 'SUPC_11228' or periphID == 'SUPC_6452':
        # Enable WKUP pins
        input = "".join(filter(lambda x: x.isdigit(), setting))
        configDB.setdefault('config', (input, enable))
        
    # elif periphID == 'SUPC_03926': # Not needed
    # elif periphID == 'SUPC_44082':

    # else:
    #     print("SHD >> getConfigDatabaseSUPC {} NOT FOUND!!!".format(periphID))

    return componentID, configDB

def __getConfigDatabaseOCMP(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'OCMP_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'OCMP_00749':
        output = "pwm"
        configDB.setdefault('config', (output, enable))
        configDB.setdefault('compID', componentID)

    # else:
    #     print("SHD >> getConfigDatabaseOCMP {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseI2CBB(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = "i2c_bb"
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'I2CBB_CONFIG_HW_IO')
    configDB.setdefault('config', (signalId, pinId, enable))
    configDB.setdefault('compID', componentID)

    return configDB

def __getConfigDatabaseCCP(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'CCP_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'CCP_01512':
        opMode = "Compare"
        outputPin = setting[-1].upper()
        if outputPin.isalpha() == False:
            outputPin = "A"
            
        configDB.setdefault('config', (opMode, outputPin, enable))
        configDB.setdefault('compID', componentID)

    # else:
    #     print("SHD >> getConfigDatabaseOCMP {} NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseINT(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signal, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'INT_CONFIG_HW_IO')
    
    # 'INT_02610', 'INT_01166', 'INT_02907', 'INT_02481', 'INT_01423', 
    # 'INT_02495', 'INT_00868', 'INT_01618', 'INT_02922'
    periphID = periphID.upper()
    componentID = "core"
    extIntId = "".join(filter(lambda x: x.isdigit(), setting))
    configDB.setdefault('config', (extIntId, enable))
    
    return componentID, configDB

def __getConfigDatabaseSPI(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'SPI_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    if periphID == 'SPI_6088':
        if 'npcs' in setting:
            npcs = setting.upper()
            configDB.setdefault('config', (npcs, enable))
    # elif periphID == 'SPI_00753':
    # elif periphID == 'SPI_01329':
    # else:
    #     print("SHD >> getConfigDatabaseSPI {} - NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseI2S(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = "a_i2s"
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'I2S_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    
    if periphID == 'I2S_U2224':
        if 'fs' in setting:
            configDB.setdefault('config', (setting.upper(), pinId, enable))
    # elif periphID == 'SPI_00753':
    # elif periphID == 'SPI_01329':
    # else:
    #     print("SHD >> getConfigDatabaseI2S {} - NOT FOUND!!!".format(periphID))

    return componentID, configDB

def __getConfigDatabaseSDADC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'SDADC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    
    if periphID == 'SDADC_U2260':
        configDB.setdefault('config', (setting.upper(), pinId, enable))
    # else:
    #     print("SHD dbg >> __getConfigDatabaseSDADC {} - NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseCBG(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'CBG_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    
    if periphID == 'CBG_03516':
        configDB.setdefault('config', (setting, enable))
    # else:
    #     print("SHD dbg >> __getConfigDatabaseCBG {} - NOT FOUND!!!".format(periphID))

    return configDB

def __getConfigDatabaseCMPDAC(periphID, settings):
    # fnValue format -> '{}_{}'.format(componentID, setting)
    signalId, pinId, fnValue, pinNameValue, enable = settings
    componentID = fnValue.split('_')[0].lower()
    setting = fnValue.split('_')[-1].split('/')[0].lower()

    configDB = dict()
    configDB.setdefault('msgID', 'CMPDAC_CONFIG_HW_IO')
    
    periphID = periphID.upper()
    
    if periphID == 'CMP_DAC_03496':
        configDB.setdefault('config', (setting, enable))
    # else:
    #     print("SHD dbg >> __getConfigDatabaseCMPDAC {} - NOT FOUND!!!".format(periphID))

    return configDB

def getDBMsgPLIBConfiguration(ATDF, settings, intMode):
    periphList = __getDevicePeripheralList(ATDF)
    msgID = None
    
    signalId, pinId, fnValue, pinNameValue, enable = settings

    if "/" in fnValue:
        fnValue = fnValue.split('/')[0]

    # fnValue format -> '{}_{}'.format(componentID, setting)
    splitedComp = fnValue.split('_')
    if len(splitedComp) > 2:
        componentID = "_".join(splitedComp[:2]).lower()
    else:
        componentID = splitedComp[0].lower()
    # Remove plib number except i2c, for example: flexcom0 -> flexcom
    plib = componentID
    if plib != 'i2s':
        plib = "".join(filter(lambda x: not x.isdigit(), componentID))

    # Adapt plib according to the peripheral PIO ID
    dependencyList = dict()
    dependencyList[plib] = componentID
    newDependencyList = adaptDevicePeripheralDependencies(ATDF, dependencyList)
    # print("SHD >> getDBMsgPLIBConfiguration newDependencyList: {}".format(newDependencyList))

    for depId, capId in newDependencyList.items():
        componentID = capId
        plib = depId

        periphID = ""
        configDB = dict()
        params = dict()
        
        for peripheral in periphList:
            splitedPeriph = peripheral.split('_')
            if len(splitedPeriph) > 2:
                pName = "_".join(splitedPeriph[:2]).lower()
            else:
                pName = splitedPeriph[0].lower()
            
            # print("SHD >> checking periph {}: {} = {}".format(peripheral, plib, pName))
            if plib == pName:
                periphID = peripheral
                params.setdefault('peripheral', peripheral)
                break

        if plib == 'gpio':
            pinNameLower = pinNameValue.lower()
            if "i2c_bb" in pinNameLower or "_scl" in pinNameLower or "_sda" in pinNameLower:
                componentID = "i2c_bb"
                configDB = __getConfigDatabaseI2CBB(periphID, settings);

        elif plib == 'adc' or plib == 'afec' or plib == 'adchs':
            configDB = __getConfigDatabaseADC(periphID, settings)
            
        elif plib == 'dac' or plib == 'dacc':
            configDB = __getConfigDatabaseDAC(periphID, settings)
            
        elif plib == 'ac':
            configDB = __getConfigDatabaseAC(periphID, settings)
            
        elif plib == 'acc':
            configDB = __getConfigDatabaseACC(periphID, settings) 
                
        elif plib == 'pwm' or plib == 'mcpwm':
            configDB = __getConfigDatabasePWM(periphID, settings)

        elif plib == 'flexcom':
            configDB = __getConfigDatabaseFLEXCOM(periphID, settings)

        elif plib == 'sercom':
            configDB = __getConfigDatabaseSERCOM(periphID, settings)

        elif plib == 'mcspi':
            configDB = __getConfigDatabaseMCSPI(periphID, settings)
            
        elif plib == 'eic':
            configDB = __getConfigDatabaseEIC(periphID, settings, intMode)

        elif plib == 'aic':
            componentID, configDB = __getConfigDatabaseAIC(periphID, settings)
            
        elif plib == 'supc':
            componentID, configDB = __getConfigDatabaseSUPC(periphID, settings)
            
        elif plib == 'ocmp':
            configDB = __getConfigDatabaseOCMP(periphID, settings)

        elif plib == 'ccp':
            configDB = __getConfigDatabaseCCP(periphID, settings)

        elif plib == 'int':
            componentID, configDB = __getConfigDatabaseINT(periphID, settings)

        elif plib == 'spi':
            configDB = __getConfigDatabaseSPI(periphID, settings)

        # elif plib == 'i2s':
        #     componentID, configDB = __getConfigDatabaseI2S(periphID, settings)

        elif plib == 'sdadc':
            configDB = __getConfigDatabaseSDADC(periphID, settings)
        
        elif plib == 'cbg':
            configDB = __getConfigDatabaseCBG(periphID, settings)
        
        elif plib == 'cmp_dac':
            configDB = __getConfigDatabaseCMPDAC(periphID, settings)

        # else:
        #     print("SHD >> getDevicePLIBConfigurationDBMessage {} NOT FOUND!!! - {}".format(plib, periphID))
            
        config = configDB.get('config')
        if config != None:
            msgID = configDB.get('msgID')
            params.setdefault('config', config)
            params.setdefault('enable', enable)

    return (componentID, msgID, params)

def __getConfigDatabaseDrvPlc(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    if (functionValue.lower() == "gpio") or (signalId in ["cs", "int", "irq"]):
        if "PL360" in nameValue.upper() or "PL460" in nameValue.upper():
            configDB.setdefault('msgID', 'DRVPLC_CONFIG_HW_IO')
            configDB.setdefault('config', (signalId, pinId, functionValue, nameValue, enable))
    
    return configDB

def __getConfigDatabaseDrvX2CScope(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    if "tx" in nameValue.lower():
        configDB.setdefault('msgID', 'X2CSCOPE_CONFIG_HW_IO')
        configDB.setdefault('config', ("TX", pinId, enable))
    elif "rx" in nameValue.lower():
        configDB.setdefault('msgID', 'X2CSCOPE_CONFIG_HW_IO')
        configDB.setdefault('config', ("RX", pinId, enable))
    
    return configDB

def __getConfigDatabaseDrvPMSMFOC(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    # if "tx" in nameValue.lower():
    #     configDB.setdefault('msgID', 'X2CSCOPE_CONFIG_HW_IO')
    #     configDB.setdefault('config', ("TX", pinId, enable))
    # elif "rx" in nameValue.lower():
    #     configDB.setdefault('msgID', 'X2CSCOPE_CONFIG_HW_IO')
    #     configDB.setdefault('config', ("RX", pinId, enable))
    
    return configDB

def __getConfigDatabaseDrvSST26(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    cs = ""
    fn = "".join(filter(lambda x: x.isalpha(), functionValue)).upper()
    # print("SHD dbg >> getConfigDatabaseDrvSST26 settings: {} ".format(settings))
    if 'SQI' in fn:
        if signalId.lower() == 'qcs':
            protocol = 'SQI'
            cs = "".join(filter(lambda x: x.isdigit(), functionValue.split("_")[-1]))
    elif ('SS' in fn) or ('CS' in fn) or (nameValue is not None and '_CS' in nameValue.upper()):
        protocol = 'SPI'
        cs = 0
    
    if cs != "":
        configDB.setdefault('msgID', 'SST26_CONFIG_HW_IO')
        configDB.setdefault('config', (pinId, protocol, int(cs), enable))

    return configDB

def __getConfigDatabaseDrvAT25(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    pinFn = nameValue.split("_")[-1].upper()
    # print("SHD >> getConfigDatabaseDrvAT25 pinFn: {} ".format(pinFn))
    if pinFn in ["WP", "CS", "HOLD"]:
        configDB.setdefault('msgID', 'AT25_CONFIG_HW_IO')
        configDB.setdefault('config', (pinFn, pinId, enable))
    
    return configDB

def __getConfigDatabaseDrvSDSPI(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    # print("SHD >> __getConfigDatabaseDrvSDMMC nameValue: {} ".format(nameValue))
    if functionValue == "GPIO" and signalId == "cs" and "_microSD_SS" in nameValue:
        configDB.setdefault('msgID', 'DRV_SDSPI_CONFIG_HW_IO')
        configDB.setdefault('config', (pinId, signalId, nameValue, enable))
    elif signalId == "sck":
        plib = functionValue.split("_")[0]
        configDB.setdefault('msgID', 'DRV_SDSPI_CONFIG_INSTANCE_HW_IO')
        configDB.setdefault('config', (plib, enable))
    
    return configDB

def __getConfigDatabaseDrvAT25DF(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()

    pinFn = nameValue.split("_")[-1].upper()
    # print("SHD >> getConfigDatabaseDrvAT25 pinFn: {} ".format(pinFn))
    if pinFn in ["CS"]:
        configDB.setdefault('msgID', 'AT25DF_CONFIG_HW_IO')
        configDB.setdefault('config', (pinFn, pinId, enable))
    
    return configDB

def __getConfigDatabaseDrvWINCS02(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()
    if (signalId == 'irq') or (signalId == 'int') or (signalId == 'hostwake'):
        plib = functionValue.split("_")[0]
        setting = functionValue.split('_')[-1]
        configDB.setdefault('msgID', 'WINCS02_CONFIG_HW_IO')
        configDB.setdefault('config', (signalId, pinId, plib, setting, enable))
    
    return configDB

def __getConfigDatabaseDrvWINC(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()
    if (signalId == 'irq') or (signalId == 'int') or (signalId == 'hostwake'):
        plib = functionValue.split("_")[0]
        setting = functionValue.split('_')[-1]
        configDB.setdefault('msgID', 'WINC_CONFIG_HW_IO')
        configDB.setdefault('config', (signalId, pinId, plib, setting, enable))
    
    return configDB

def __getConfigDatabaseWirelessRNWF(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()
    plib = functionValue.split("_")[0]
    addon = nameValue.split("_")[0]
    configDB.setdefault('msgID', 'WIRELESS_RNWF_CONFIG_HW_IO')
    configDB.setdefault('config', (addon, plib, enable))
    
    return configDB

def __getConfigDatabaseWirelessRNBD(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()
    plib = functionValue.split("_")[0]
    configDB.setdefault('msgID', 'WIRELESS_RNBD_CONFIG_HW_IO')
    configDB.setdefault('config', (pinId, nameValue, plib, enable))
    
    return configDB

def __getConfigDatabasePlcSrvPvddMon(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings

    configDB = dict()
    plib = functionValue.split("_")[0]
    setting = functionValue.split('_')[-1]
    channel = "".join(filter(lambda x: x.isdigit(), setting))
    configDB.setdefault('msgID', 'PLV_SRV_PVDDMON_CONFIG_HW_IO')
    configDB.setdefault('config', (plib, channel, enable))

    return configDB

def getDBMsgDriverConfiguration(settings):
    driver, signalId, pinId, functionValue, nameValue, enable = settings
    
    componentID = driver
    configDB = dict()
    params = dict()

    if driver == 'drvPlcPhy' or driver == 'drvG3MacRt':
        configDB = __getConfigDatabaseDrvPlc(settings)
    elif driver == 'X2CScope':
        configDB = __getConfigDatabaseDrvX2CScope(settings)
    elif driver == 'pmsm_foc':
        configDB = __getConfigDatabaseDrvPMSMFOC(settings)
    elif driver == 'drv_sst26':
        configDB = __getConfigDatabaseDrvSST26(settings)
    elif driver == 'drv_at25':
        configDB = __getConfigDatabaseDrvAT25(settings)
    elif driver == 'drv_sdspi':
        configDB = __getConfigDatabaseDrvSDSPI(settings)
    elif driver == 'drv_at25df':
        configDB = __getConfigDatabaseDrvAT25DF(settings)
    elif driver == 'drvWifiWincS02':
        configDB = __getConfigDatabaseDrvWINCS02(settings)
    elif driver == 'drvWifiWinc':
        configDB = __getConfigDatabaseDrvWINC(settings)
    elif driver == 'sysWifiRNWF':
        configDB = __getConfigDatabaseWirelessRNWF(settings)
    elif driver == 'RNBD_Dependency':
        configDB = __getConfigDatabaseWirelessRNBD(settings)
    elif driver == 'srv_pvddmon':
        configDB = __getConfigDatabasePlcSrvPvddMon(settings)
    # else:
    #     print("SHD >> getDeviceDriverConfigurationDBMessage {} NOT FOUND!!!".format(driver))
        
    config = configDB.get('config')
    if config != None:
        msgID = configDB.get('msgID')
        params.setdefault('config', config)
    else:
        # print("SHD >> getDeviceDriverConfigurationDBMessage error config {}".format(configDB))
        msgID = None

    return (componentID, msgID, params)

def getAutoconnectTable(atdf, idDependency, idCapability):
    connectionTable = []
    family = atdf.getNode("/avr-tools-device-file/devices/device").getAttribute("family")
    # print("SHD >> getAutoconnectTable family:{} dep:{} cap:{}".format(family, idDependency, idCapability)) 

    if idDependency != "":
        for depId, capId in __drvDependencies.items():
            exception = False
            periphGmac = None
            periphEth = None
            depToCheck = idDependency

            # Handle exceptions in drv instance numbers designators and RMII connections
            if idDependency.startswith("drvEmac") == True:
                if "drvExtPhy" in idCapability:
                    depToCheck = "drvEmac"
                else:
                    continue
            elif idDependency.startswith("drvGmac") == True:
                periphGmac = atdf.getNode("/avr-tools-device-file/devices/device/peripherals/module@[name=\"GMAC\"]")
                periphEth = atdf.getNode("/avr-tools-device-file/devices/device/peripherals/module@[name=\"ETH\"]")
                if "drvExtPhy" in idCapability:
                    depToCheck = "drvGmac"
                else:
                    continue
            else:
                # Remove instance number if needed from dep to check
                idDepSplit = idDependency.split("_")
                if idDepSplit[-1].isdigit():
                    depToCheck = "_".join(idDepSplit[:-1])

            # print("SHD >> getAutoconnectTable depId:{} depToCheck:{}".format(depId, depToCheck)) 
            if depId == depToCheck:
                connection = []
                # Add dependency
                connection.append(idDependency)
                # handle name exceptions
                if 'a_drv_i2s' == depId:
                    exception = True
                    depType = "drv_i2s_I2S_dependency"
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
                        # print("SHD >> getAutoconnectTable skip pmsm_foc: plib:{}".format(plib)) 
                        continue
                    # print("SHD >> getAutoconnectTable check pmsm_foc: plib:{}, depType{}".format(plib, depType)) 
                elif 'drvGmac' == depId:
                    exception = True
                    if periphGmac is not None:
                        instance = "".join(filter(lambda x: x.isdigit(), idDependency))
                        depType = "GMAC{}_PHY_Dependency".format(instance)
                    elif periphEth is not None:
                        depType = "ETH_PHY_Dependency"
                    else:
                        # print("SHD >> getAutoconnectTable drvGmac peripheral not found") 
                        continue
                elif 'drvEmac' == depId:
                    exception = True
                    instance = "".join(filter(lambda x: x.isdigit(), idDependency))
                    depType = "MAC_PHY_Dependency{}".format(instance)
                elif 'drvPic32mEthmac' == depId:
                    exception = True
                    depType = "ETHMAC_PHY_Dependency"
                elif 'le_gfx_lcdc' == depId:
                    exception = True
                    depType = "LCDC"
                elif 'le_gfx_slcdc' == depId or 'le_gfx_slcd' == depId:
                    exception = True
                    depType = "Segmented Display"
                elif 'ptc' == depId:
                    exception = True
                    depType = "lib_acquire"
                elif 'drvWifiWincS02' == depId:
                    exception = True
                    depType = "spi_dependency"
                elif 'drvWifiWinc' == depId:
                    exception = True
                    depType = "spi_dependency"
                elif 'drv_sst26' == depId:
                    depType = depId
                    if 'sqi' in idCapability:
                        capId = "SQI"
                    elif 'qspi' not in idCapability:
                        capId = "SPI"
                elif 'RNBD_Dependency' == depId:
                    exception = True
                    depType = "RNBD_USART_Dependency"
                elif 'ecc' in depId or 'sha' in depId or 'ta010' == depId:
                    exception = True
                    depType = "{}_DEP_PLIB_{}".format(depId.upper(), capId.upper())
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
                    exception = True
                    idCapability = "I2C"
                elif "gfx_disp_slcd1-" in idCapability:
                    exception = True
                    idCapability = "slcd_display"
                elif idCapability.startswith("a_i2sc"):
                    exception = True
                    instance = "".join(filter(lambda x: x.isdigit(), idCapability.replace("i2s", "is")))
                    idCapability = "I2SC{}_I2S".format(instance)
                elif idCapability.startswith("a_ssc"):
                    exception = True
                    instance = "".join(filter(lambda x: x.isdigit(), idCapability.replace("i2s", "is")))
                    idCapability = "SSC{}_I2S".format(instance)
                elif idCapability.startswith("a_i2s"):
                    spiPeripheral = atdf.getNode("/avr-tools-device-file/devices/device/peripherals/module@[name=\"SPI\"]")
                    spiVersion = None
                    if spiPeripheral is not None:
                        spiVersion = spiPeripheral.getAttribute("id")

                    if spiVersion == "01329":
                        exception = True
                        instance = "".join(filter(lambda x: x.isdigit(), idCapability.replace("i2s", "is")))
                        idCapability = "SPI{}_I2S".format(instance)
                    else:
                        exception = True
                        instance = "".join(filter(lambda x: x.isdigit(), idCapability.replace("i2s", "is")))
                        idCapability = "I2S{}_I2S".format(instance)
                elif capId == "SWI":
                    capId = "UART"
                elif 'drvExtPhy' in idCapability:
                    exception = True
                    idCapability = "lib{}".format(idCapability)

                if exception == True:
                    connection.append("{}".format(idCapability))
                else:
                    connection.append("{}_{}".format(idCapability.upper(), capId))
                
                connectionTable.append(connection)

    # print("SHD >> getAutoconnectTable connectionTable:{}".format(connectionTable)) 
    return connectionTable

def getDriverDependencyFromPin(pinName, pinFunction):
    dep = ""
    string = pinName.upper()
    if __checkSubstringList(['MCSPI'], string) == True:
        dep = ""
    elif __checkSubstringList(['I2C', 'TWI', 'SDA', 'SCL', 'TWD', 'TWCK'], string) == True:
        if __checkSubstringList(['SDADC'], string) == True:
            dep = ""
        else:
            dep = "drv_i2c"
    elif __checkSubstringList(['_SPI', '_MISO', '_MOSI', '_CS', '_SCK'], string) == True:
        if __checkSubstringList(['LIN' ,'GFX_DISP' ,'X32', 'I2S'], string) == True:
            dep = ""
        elif __checkSubstringList(['USART'], string) == True:
            dep = "drv_usart"
        else:
            dep = "drv_spi"
    elif __checkSubstringList(['UART', 'USART', 'VIRTUAL_COM', 'VCOM'], string) == True:
        dep = "drv_usart"
    else:
        string = pinFunction.upper()
        if __checkSubstringList(['SDMMC'], string) == True:
            dep = "drv_sdmmc"
        elif __checkSubstringList(['GMAC'], string) == True:
            # Add instance number if needed
            dep = "drvGmac" + "".join(filter(lambda x: x.isdigit(), string.split("_")[0]))
        elif __checkSubstringList(['ETHMAC'], string) == True:
            dep = "drvPic32mEthmac"
        elif __checkSubstringList(['CMP_DAC'], string) == True:
            dep = string[:8].lower()

    return dep

def checkPlibFromSignalConnector(plib, signal):
    plibLow = plib.lower()
    signalLow = signal.lower()

    if plibLow == signalLow:
        return True
    elif 'i2c' in signalLow:
        # Check if Plib supports these communication signals
        if __checkSubstringList(['i2c', 'twi', 'sercom', 'flexcom'], plibLow) == True:
            return True
    elif 'uart' in signalLow:
        # Check if Plib supports these communication signals
        if __checkSubstringList(['uart', 'usart', 'sercom', 'flexcom'], plibLow) == True:
            return True
    elif 'spi' in signalLow:
        # Check if Plib supports these communication signals
        if __checkSubstringList(['spi', 'sercom', 'flexcom'], plibLow) == True:
            return True

    return False
