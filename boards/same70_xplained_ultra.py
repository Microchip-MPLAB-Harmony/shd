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
from mainBoard.mainBoard import MainBoard

global mainBoard

def handleMessage(messageID, args):
    return mainBoard.handleMessage(messageID, args)

def instantiateComponent(boardComponent):
    global mainBoard

    # Create new instance of the SHD mainBoard
    mainBoard = MainBoard("same70_xplained_ultra.yml", Database, ATDF)
    boardName = mainBoard.getName()
    if mainBoard != None:
        Log.writeInfoMessage("Loading SHD Main Board: " + boardName.upper())
    else:
        Log.writeInfoMessage("ERROR in Loading SHD Main Board: " + boardName.upper())
        return

    mainBoard.createConfigurationSymbols(boardComponent)

    ################################ Generation Code by Templates ################################

    configName = Variables.get("__CONFIGURATION_NAME")
    
    # bspSourceFile = boardComponent.createFileSymbol("SHD_C", None)
    # bspSourceFile.setSourcePath("boards/templates/bsp.c.ftl")
    # bspSourceFile.setOutputName("bsp.c")
    # bspSourceFile.setMarkup(True)
    # bspSourceFile.setOverwrite(True)
    # bspSourceFile.setDestPath("bsp/")
    # bspSourceFile.setProjectPath("config/" + configName + "/bsp/")
    # bspSourceFile.setType("SOURCE")

    bspJinjaSourceFile = boardComponent.createFileSymbol("SHD_JINJA_C", None)
    bspJinjaSourceFile.setSourcePath("boards/templates/bsp.c.j2")
    bspJinjaSourceFile.setOutputName("bsp.c")
    bspJinjaSourceFile.setDestPath("bsp/")
    bspJinjaSourceFile.setProjectPath("config/" + configName + "/bsp/")
    bspJinjaSourceFile.setType("SOURCE")
    bspJinjaSourceFile.setOverwrite(False)

    # bspHeaderFile = boardComponent.createFileSymbol("SHD_H", None)
    # bspHeaderFile.setSourcePath("boards/templates/bsp.h.ftl")
    # bspHeaderFile.setOutputName("bsp.h")
    # bspHeaderFile.setMarkup(True)
    # bspHeaderFile.setOverwrite(True)
    # bspHeaderFile.setDestPath("bsp/")
    # bspHeaderFile.setProjectPath("config/" + configName + "/bsp/")
    # bspHeaderFile.setType("HEADER")

    bspJinjaHeaderFile = boardComponent.createFileSymbol("SHD_JINJA_H", None)
    bspJinjaHeaderFile.setSourcePath("boards/templates/bsp.h.j2")
    bspJinjaHeaderFile.setOutputName("bsp.h")
    bspJinjaHeaderFile.setDestPath("bsp/")
    bspJinjaHeaderFile.setProjectPath("config/" + configName + "/bsp/")
    bspJinjaHeaderFile.setType("HEADER")
    bspJinjaHeaderFile.setOverwrite(False)

    bspSystemInitFile = boardComponent.createFileSymbol("SHD_INIT", None)
    bspSystemInitFile.setType("STRING")
    bspSystemInitFile.setOutputName("core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_PERIPHERALS")
    bspSystemInitFile.setSourcePath("boards/templates/system_initialize.c")
    # bspSystemInitFile.setMarkup(True)

    bspSystemDefFile = boardComponent.createFileSymbol("SHD_DEF", None)
    bspSystemDefFile.setType("STRING")
    bspSystemDefFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES")
    bspSystemDefFile.setSourcePath("boards/templates/system_definitions.h")
    # bspSystemDefFile.setMarkup(True)

    # bspSourceGPIOFile = boardComponent.createFileSymbol("SHD_GPIO_C", None)
    # bspSourceGPIOFile.setType("STRING")
    # bspSourceGPIOFile.setOutputName("core.LIST_BSP_INITIALIZATION")
    # bspSourceGPIOFile.setSourcePath("boards/templates/bsp_pio_11264.c.ftl")
    # bspSourceGPIOFile.setMarkup(True)

    # bspHeaderGPIOFile = boardComponent.createFileSymbol("SHD_GPIO_H", None)
    # bspHeaderGPIOFile.setType("STRING")
    # bspHeaderGPIOFile.setOutputName("core.LIST_BSP_MACRO_INCLUDES")
    # bspHeaderGPIOFile.setSourcePath("boards/templates/bsp_pio_11264.h.ftl")
    # bspHeaderGPIOFile.setMarkup(True)

def destroyComponent(boardComponent):
    global mainBoard

    mainBoard.resetSignalConfiguration()

