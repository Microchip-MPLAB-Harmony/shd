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
    context = dict()
    context["configuration"] = "wfi32e_iot_20_db.yml"
    context["database"] = Database
    context["atdf"] = ATDF
    context["log"] = Log
    mainBoard = MainBoard(context)
    boardName = mainBoard.getName()
    if boardName is not None:
        Log.writeInfoMessage("Loading SHD Main Board: " + boardName.upper())
    else:
        Log.writeInfoMessage("ERROR in Loading SHD Main Board: " + context["configuration"])
        return

    mainBoard.createConfigurationSymbols(boardComponent)

    ################################ Generation Code by Templates ################################

    configName = Variables.get("__CONFIGURATION_NAME")

    bspJinjaSourceFile = boardComponent.createFileSymbol("SHD_JINJA_C", None)
    bspJinjaSourceFile.setSourcePath("boards/templates/bsp.c.j2")
    bspJinjaSourceFile.setOutputName("bsp.c")
    bspJinjaSourceFile.setDestPath("bsp/")
    bspJinjaSourceFile.setProjectPath("config/" + configName + "/bsp/")
    bspJinjaSourceFile.setType("SOURCE")
    bspJinjaSourceFile.setOverwrite(False)

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

    bspSystemDefFile = boardComponent.createFileSymbol("SHD_DEF", None)
    bspSystemDefFile.setType("STRING")
    bspSystemDefFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES")
    bspSystemDefFile.setSourcePath("boards/templates/system_definitions.h")

def destroyComponent(boardComponent):
    global mainBoard

    mainBoard.resetSignalConfiguration()

