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
def getDeviceFunctionListByPinId(Database, ATDF, pinId):
    functionList = []
    family = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("family")
    architecture = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("architecture")
    if architecture == "MIPS" or architecture == "33Axxx" or "WBZ" in family or family == "PIC32WM_BZ":
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
    series = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("series")
    pinMap = dict()
    # Send message to core to get available pins
    availablePinDictionary = {}
    availablePinDictionary = Database.sendMessage("core", "PIN_LIST", availablePinDictionary)
    for pinNumber, pinId in availablePinDictionary.items():
        # Handle exception for PIC32CZCA70 series (ATDF and pin Dictionary are different)
        if series == "PIC32CZCA70":
            pinId = str(pinId[:2]) + "{}".format(pinId[2:]).zfill(2)

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
    if architecture == "MIPS" or architecture == "33Axxx":
        family = ATDF.getNode("/avr-tools-device-file/devices/device").getAttribute("family")
        if family == "PIC32MZW":
            newDependencyList = {}
            for depId, capId in dependencyList.items():
                if depId == 'ethmac':
                    depId = 'drvPic32mEthmac'

                newDependencyList.setdefault(depId, capId)

            return newDependencyList 
        else:
            return dependencyList
    else:
        newDependencyList = {}
        pioPeriphID = getDeviceGPIOPeripheral(ATDF)
        flexcomID = __getDeviceFLEXCOMPeripheral(ATDF)
        # print("SHD dbg >> adaptDevicePeripheralDependencies {} - {}".format(pioPeriphID, flexcomID))
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
