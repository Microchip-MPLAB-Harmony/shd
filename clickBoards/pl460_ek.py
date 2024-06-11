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

def instantiateComponent(boardComponent):
    global clickBoard
    
    # Create new instance of the click board
    clickBoard = ClickBoard("pl460_ek.yml")
    boardName = clickBoard.getName()
    if clickBoard != None:
        Log.writeInfoMessage("Loading SHD Click Board: " + boardName.upper())
    else:
        Log.writeInfoMessage("ERROR in Loading SHD Click Board: " + boardName.upper())
        return

    clickBoard.createConfigurationSymbols(boardComponent)
        
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
