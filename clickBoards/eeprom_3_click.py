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
from clickBoard.clickBoard import ClickBoard

global clickBoard

def sendGetConnListMsg(symbol, event):
    remoteID = "mainBoard_SAMD21_CURIOSITY_CNANO"
    response = Database.sendMessage(remoteID, "GET_CONNECTOR_LIST", {})
    if response == None:
        print("GET_CONNECTOR_LIST Failure")
    else:
        print("GET_CONNECTOR_LIST response : {}".format(response))

def sendGetConnectorConfigMsg(symbol, event):
    remoteID = "mainBoard_SAMD21_CURIOSITY_CNANO"
    connectorName = "Curiosity Nano Base MikroBUS 1"
    response = Database.sendMessage(remoteID, "GET_CONNECTOR_CONFIGURATION", {'connector' : connectorName})
    if response == None:
        print("GET_CONNECTOR_CONFIGURATION Failure")
    else:
        print("GET_CONNECTOR_CONFIGURATION response : {}".format(response))

def instantiateComponent(boardComponent):
    global clickBoard

    # Disable xplainpro dependency
    boardComponent.setDependencyEnabled("xplainpro", False)
    
    # Create new instance of the click board
    clickBoard = ClickBoard("eeprom_3_click.yml")
    boardName = clickBoard.getName()
    if clickBoard != None:
        Log.writeInfoMessage("Loading SHD Click Board: " + boardName.upper())
    else:
        Log.writeInfoMessage("ERROR in Loading SHD Click Board: " + boardName.upper())
        return

    clickBoard.createConfigurationSymbols(boardComponent)

    symbol = boardComponent.createBooleanSymbol("CLICKBOARD_GET_CONNECTOR_LIST", None)
    symbol.setLabel("Send GET_CONNECTOR_LIST msg")
    symbol.setDependencies(sendGetConnListMsg, ["CLICKBOARD_GET_CONNECTOR_LIST"])

    symbol = boardComponent.createBooleanSymbol("CLICKBOARD_GET_CONNECTOR_CONFIG", None)
    symbol.setLabel("Send GET_CONNECTOR_CONFIG msg")
    symbol.setDependencies(sendGetConnectorConfigMsg, ["CLICKBOARD_GET_CONNECTOR_CONFIG"])

def onAttachmentConnected(source, target):
    global clickBoard

    remoteID = target["component"].getID()
    targetID = target["id"]

    if (Database.sendMessage(remoteID, "CONNECTOR_SET_CONFIGURATION", {targetID : clickBoard.getConnections()}) == None):
        print("CONNECTOR_SET_CONFIGURATION Failure")
    else:
        clickBoard.connect()

def onAttachmentDisconnected(source, target):
    global clickBoard
    
    remoteID = target["component"].getID()
    targetID = target["id"]

    if (Database.sendMessage(remoteID, "CONNECTOR_CLEAR_CONFIGURATION", {targetID : clickBoard.getConnections()}) == None):
        print("CONNECTOR_CLEAR_CONFIGURATION Failure")
    else:
        clickBoard.disconnect()
