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

    plugInFile = dict()
    plugInMainBoardList = []
    clickBoardPathList = []
    clickBoardConfigList = []
    
    mainBoardCompatibleList = []
    mainBoardFileList = glob.glob(path.join(boardPath, '*.yml'))
    for mainBoardFile in mainBoardFileList:
        mainBoardYaml = yaml.safe_load(open(mainBoardFile, 'r'))
        if mainBoardYaml['processor']['name'] == processor:
            connectorList = []
            connectors = mainBoardYaml.get('connectors')
            for connector in connectors:
                connectorList.append((connector.get('name'), connector.get('compatible')))
            mainBoardCompatibleList.append((mainBoardYaml['name'], mainBoardYaml.get('config'), connectorList)) 
            plugInMainBoardList.append(path.relpath(mainBoardFile, shdPath).replace("\\", "/"))
    
    for mainBoard in mainBoardCompatibleList:
        boardName, config, connectorList = mainBoard
        if config != None:
            print("SHD loading main board " + boardName.upper())
            shdModule = Module.CreateComponent("mainBoard_" + config.split(".")[0].upper(),
                                            boardName.upper(),
                                            "/System Hardware Definitions (SHD)/Main Boards/",
                                            "/boards/"+ config)
            shdModule.setDisplayType("MAIN BOARD")
        
            # for connector in connectorList:
            #     connectorName, compatible = connector
            #     shdModule.addCapability(connectorName, compatible)

    clickBoardList = []
    clickBoardFileList = glob.glob(path.join(clickBoardPath, '*.yml'))
    for clickBoardFile in clickBoardFileList:
        if 'clickBoards.yml' not in clickBoardFile:
            clickBoardYaml = yaml.safe_load(open(clickBoardFile, 'r'))
            clickBoardList.append((clickBoardYaml.get('name'), clickBoardYaml.get('config'), clickBoardYaml.get('compatible'))) 
            clickBoardPathList.append(path.relpath(clickBoardFile, shdPath).replace("\\", "/"))
            clickBoardConfigList.append(clickBoardFile.split("\\")[-1])
    
    for clickBoard in clickBoardList:
        boardName, config, connector = clickBoard
        if config != None:
            clickModule = Module.CreateComponent(config.split(".")[0].upper(),
                                                boardName.upper(),
                                                "/System Hardware Definitions (SHD)/Click Boards/",
                                                "/clickBoards/" + config)
            clickModule.addDependency(connector, connector, None, False, True)
            clickModule.setDisplayType("CLICK BOARD")
            # mikroBUS click boards must include a xplainpro dependency 
            # to be able to use mikroBus-XplainPro adaptation board
            if connector == 'mikrobus':
                clickModule.addDependency('xplainpro', 'xplainpro', None, False, True)


    plugInFileName = path.join(shdPath, 'config', 'hw_description.yml')
    plugInFile.setdefault('mainboards', plugInMainBoardList)
    plugInFile.setdefault('clickboards', clickBoardPathList)
    with open(plugInFileName, 'w') as file:
        print('CHRIS dbg -> creating {}'.format(plugInFileName))
        yaml.safe_dump(plugInFile, file, encoding='utf-8', allow_unicode=True)

    fileName = path.join(clickBoardPath, 'clickBoards.yml')
    with open(fileName, 'w') as file:
        print('CHRIS dbg -> creating {}'.format(fileName))
        yaml.safe_dump(clickBoardConfigList, file, encoding='utf-8', allow_unicode=True)
    