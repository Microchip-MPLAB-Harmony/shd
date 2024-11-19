import sys
from os import path
import glob

######################  Harmony System Hardware Definitions  ######################
def loadModule():
    print("Load Module: Harmony System Hardware Description (SHD)")

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
        mainBoardYaml = yaml.safe_load(open(mainBoardFile, 'r'))
        if mainBoardYaml['processor']['name'] == processor:
            mainBoardCompatibleList.append((mainBoardYaml['name'], mainBoardYaml.get('config'))) 
    
    for mainBoard in mainBoardCompatibleList:
        boardName, config = mainBoard
        # boardName, config, connectorList = mainBoard
        if config != None:
            print("SHD loading main board " + boardName.upper())
            shdModule = Module.CreateComponent("mainBoard_" + config.split(".")[0].upper(),
                                            boardName.upper(),
                                            "/System Hardware Description (SHD)/Main Boards/",
                                            "/boards/"+ config)
            shdModule.setDisplayType("MAIN BOARD")
        