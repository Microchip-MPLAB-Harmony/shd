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

    # plugInMainBoardList = []
    
    mainBoardCompatibleList = []
    mainBoardFileList = glob.glob(path.join(boardPath, '*.yml'))
    for mainBoardFile in mainBoardFileList:
        mainBoardYaml = yaml.safe_load(open(mainBoardFile, 'r'))
        if mainBoardYaml['processor']['name'] == processor:
            mainBoardCompatibleList.append((mainBoardYaml['name'], mainBoardYaml.get('config'))) 
            # connectorList = []
            # connectors = mainBoardYaml.get('connectors')
            # if connectors != None:
            #     for connector in connectors:
            #         connectorList.append((connector.get('name'), connector.get('compatible')))
            # mainBoardCompatibleList.append((mainBoardYaml['name'], mainBoardYaml.get('config'), connectorList)) 
            # plugInMainBoardList.append(path.relpath(mainBoardFile, shdPath).replace("\\", "/"))
    
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
        
    # plugInFileName = path.join(shdPath, 'config', 'hw_description.yml')
    # plugInFile.setdefault('mainboards', plugInMainBoardList)
    # plugInFile.setdefault('clickboards', clickBoardPathList)
    # with open(plugInFileName, 'w') as file:
    #     print('CHRIS dbg -> creating {}'.format(plugInFileName))
    #     yaml.safe_dump(plugInFile, file, encoding='utf-8', allow_unicode=True)
