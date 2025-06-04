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
import sys
from os import path
import glob

######################  Harmony System Hardware Definitions  ######################
def loadModule():
    print("Load Module: Harmony System Hardware Definitions (SHD)")

    processor = Variables.get("__PROCESSOR")
    shdPath = Variables.get("__MODULE_ROOT")
    libsPath = path.join(shdPath, 'libs')
    sys.path.insert(0, libsPath)
    boardPath = path.join(shdPath, 'boards')
    sys.path.insert(0, boardPath)
    clickBoardPath = path.join(shdPath, 'clickBoards')
    sys.path.insert(0, clickBoardPath)
    
    import yaml

    mainBoardCompatibleList = []
    mainBoardFileList = glob.glob(path.join(boardPath, '*.yml'))
    for mainBoardFile in mainBoardFileList:
        try:
            mainBoardYaml = yaml.safe_load(open(mainBoardFile, 'r'))
            if mainBoardYaml['processor']['name'] == processor:
                mainBoardCompatibleList.append((mainBoardYaml['name'], mainBoardYaml.get('config'))) 
        except Exception as error:
            print("SHD >> ERROR loading main board : {} error: {}".format(mainBoardFile, error))
            continue
    
    for mainBoard in mainBoardCompatibleList:
        boardName, config = mainBoard
        # boardName, config, connectorList = mainBoard
        if config != None:
            print("SHD loading main board " + boardName.upper())
            shdModule = Module.CreateComponent("mainBoard_" + config.split(".")[0].upper(),
                                            boardName.upper(),
                                            "/System Hardware Definitions (SHD)/Main Boards/",
                                            "/boards/"+ config)
            shdModule.setDisplayType("MAIN BOARD")
        