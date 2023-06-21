/*******************************************************************************
  MPLAB Harmony Application Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app_console.c

  Summary:
    This file contains the source code for the MPLAB Harmony application.

  Description:
    This file contains the source code for the MPLAB Harmony application.  It
    implements the logic of the application's state machine and it may call
    API routines of other MPLAB Harmony modules in the system, such as drivers,
    system services, and middleware.  However, it does not call any of the
    system interfaces (such as the "Initialize" and "Tasks" functions) of any of
    the modules in the system or make any assumptions about when those functions
    are called.  That is the responsibility of the configuration-specific system
    files.
 *******************************************************************************/

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

#include "definitions.h"
#include "app_console.h"
#include "app_sdcard.h"

// *****************************************************************************
// *****************************************************************************
// Section: Global Data Definitions
// *****************************************************************************
// *****************************************************************************

// *****************************************************************************
/* Application Data

  Summary:
    Holds application data

  Description:
    This structure holds the application's data.

  Remarks:
    This structure should be initialized by the APP_CONSOLE_Initialize function.

    Application strings and buffers are be defined outside this structure.
*/

APP_CONSOLE_DATA app_consoleData;
static uint8_t CACHE_ALIGN app_cmdBuffer[256];

// *****************************************************************************
// *****************************************************************************
// Section: Application Callback Functions
// *****************************************************************************
// *****************************************************************************

void APP_CONSOLE_TimerCallback ( uintptr_t context )
{
    app_consoleData.timerExpired = true;
}

// *****************************************************************************
// *****************************************************************************
// Section: Application Local Functions
// *****************************************************************************
// *****************************************************************************

static void _commandSST26RDJID (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv);
static void _commandSST26RD (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv);
static void _commandSST26WR (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv);
static void _commandSSDWR (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv);
static void _commandSSDRD (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv);

static const SYS_CMD_DESCRIPTOR appCmdTbl[] =
{
    {"SST26JID", _commandSST26RDJID, ": Read SST26 Jedec Id"},
    {"SST26RD", _commandSST26RD, ": Read data from SST26 memory. Params: address[hex] length[dec]. Address must be aligned to 256"},
    {"SST26WR", _commandSST26WR, ": Write in SST26 memory. Params: address[hex] data. Address must be aligned to 256"},
    {"SSDWR", _commandSSDWR, ": Read data from SSD memory. Params: address[hex] length[dec]"},
    {"SSDRD", _commandSSDRD, ": Write in SSD memory. Params: address[hex] data"},
};

static void _commandSST26RDJID (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv)
{
    if (argc != 1) {
        SYS_CMD_MESSAGE("Unsupported Command !\r\n");
        return;
    }

    app_consoleData.state = APP_CONSOLE_SST26_JDEC;
}

static void _commandSST26WR (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv)
{
    if (argc != 3) {
        SYS_CMD_MESSAGE("Unsupported Command !\r\n");
        return;
    }

    // Extract address from parameters
    app_consoleData.sst26Address = (uint32_t)strtoul(argv[1], NULL, 16);

    // Extract message from parameters
    app_consoleData.sst26Length = (size_t)strlen(argv[2]);
    memcpy(app_consoleData.pData, argv[2], app_consoleData.sst26Length);

    app_consoleData.state = APP_CONSOLE_SST26_WRITE;
}

static void _commandSST26RD (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv)
{
    if (argc != 3) {
        SYS_CMD_MESSAGE("Unsupported Command !\r\n");
        return;
    }

    // Extract address from parameters
    app_consoleData.sst26Address = (uint32_t)strtoul(argv[1], NULL, 16);

    // Extract address from parameters
    app_consoleData.sst26Length = (uint32_t)strtoul(argv[2], NULL, 10);

    app_consoleData.state = APP_CONSOLE_SST26_READ;
}

static void _commandSSDWR (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv)
{
    if (argc != 3) {
        SYS_CMD_MESSAGE("Unsupported Command !\r\n");
        return;
    }

    // Extract address from parameters
    app_consoleData.ssdAddress = (uint32_t)strtoul(argv[1], NULL, 16);

    // Extract message from parameters
    app_consoleData.ssdLength = strlen(argv[2]);
    memcpy(app_consoleData.pData, argv[2], app_consoleData.ssdLength);

    app_consoleData.state = APP_CONSOLE_SSD_WRITE;
}

static void _commandSSDRD (SYS_CMD_DEVICE_NODE* pCmdIO, int argc, char** argv)
{
    if (argc != 3) {
        SYS_CMD_MESSAGE("Unsupported Command !\r\n");
        return;
    }

    // Extract address from parameters
    app_consoleData.ssdAddress = (uint32_t)strtoul(argv[1], NULL, 16);

    // Extract address from parameters
    app_consoleData.ssdLength = (uint32_t)strtoul(argv[2], NULL, 10);

    app_consoleData.state = APP_CONSOLE_SSD_READ;
}


// *****************************************************************************
// *****************************************************************************
// Section: Application Initialization and State Machine Functions
// *****************************************************************************
// *****************************************************************************

/*******************************************************************************
  Function:
    void APP_CONSOLE_Initialize ( void )

  Remarks:
    See prototype in app_console.h.
 */

void APP_CONSOLE_Initialize ( void )
{
    int nCmds;

    BSP_LED_USER_On();

    app_consoleData.state = APP_CONSOLE_INIT;
    app_consoleData.error = ERR_CODE_SST26_NO_ERROR;
    nCmds = sizeof(appCmdTbl)/sizeof(SYS_CMD_DESCRIPTOR);

    app_consoleData.pData = app_cmdBuffer;

    if (!SYS_CMD_ADDGRP(appCmdTbl, nCmds, "App Commands", ": Demo console commands"))
    {
        SYS_CONSOLE_Message(SYS_CONSOLE_INDEX_0, "Failed to create APP Console Commands\r\n");
    }
}


/******************************************************************************
  Function:
    void APP_CONSOLE_Tasks ( void )

  Remarks:
    See prototype in app_console.h.
 */

void APP_CONSOLE_Tasks ( void )
{

    /* Check the application's current state. */
    switch ( app_consoleData.state )
    {
        case APP_CONSOLE_INIT:
        {
            SYS_TIME_HANDLE timer = SYS_TIME_HANDLE_INVALID;
            uint8_t counter;

            for (counter = 0; counter < 10; counter++)
            {
                BSP_LED_BLUE_Toggle();
                BSP_LED_GREEN_Toggle();

                if (SYS_TIME_DelayMS(100, &timer) != SYS_TIME_SUCCESS)
                {

                }
                else if(SYS_TIME_DelayIsComplete(timer) != true)
                {
                   while (SYS_TIME_DelayIsComplete(timer) == false);
                }
            }

            app_consoleData.timer = SYS_TIME_CallbackRegisterMS(APP_CONSOLE_TimerCallback, 0, 250, SYS_TIME_PERIODIC);
            if (app_consoleData.timer != SYS_TIME_HANDLE_INVALID)
            {
                app_consoleData.state = APP_CONSOLE_SST26_OPEN;
            }

            break;
        }

        case APP_CONSOLE_SST26_OPEN:
        {
            app_consoleData.sst26Handler = DRV_SST26_Open((SYS_MODULE_INDEX)DRV_SST26_INDEX, DRV_IO_INTENT_READWRITE);
            if (app_consoleData.sst26Handler != DRV_HANDLE_INVALID)
            {
                if (DRV_SST26_GeometryGet(app_consoleData.sst26Handler, &app_consoleData.sst26Geometry))
                {
                    DRV_SST26_UnlockFlash(app_consoleData.sst26Handler);
                    app_consoleData.state = APP_CONSOLE_RUNNING;
                }
                else
                {
                    app_consoleData.error = ERR_CODE_SST26_GEOMETRY;
                    app_consoleData.state = APP_CONSOLE_ERROR;
                }
            }
            else
            {
                app_consoleData.error = ERR_CODE_SST26;
                app_consoleData.state = APP_CONSOLE_ERROR;
            }
            break;
        }

        case APP_CONSOLE_RUNNING:
        {
            if (app_consoleData.timerExpired)
            {
                uint32_t stateSW;

                app_consoleData.timerExpired = false;

                BSP_LED_BLUE_Toggle();

                stateSW = BSP_SWITCH_USER_Get();
                if (stateSW == BSP_SWITCH_USER_STATE_PRESSED)
                {
                    SYS_CONSOLE_Message(SYS_CONSOLE_INDEX_0, "BSP_SWITCH_USER_STATE_PRESSED\r\n");
                    BSP_LED_GREEN_On();
                }
                else
                {
                    BSP_LED_GREEN_Off();
                }
            }
            break;
        }

        case APP_CONSOLE_SST26_JDEC:
        {
            uint8_t jedecId[3];

            if (DRV_SST26_ReadJedecId(app_consoleData.sst26Handler, jedecId))
            {
                app_consoleData.state = APP_CONSOLE_RUNNING;
                SYS_CONSOLE_Print(SYS_CONSOLE_INDEX_0, "Jedec ID: 0x%02X 0x%02X 0x%02X\r\n",
                                  jedecId[0], jedecId[1], jedecId[2]);
            }
            else
            {
                app_consoleData.error = ERR_CODE_SST26_JEDECID;
                app_consoleData.state = APP_CONSOLE_ERROR;
            }
            break;
        }

        case APP_CONSOLE_SST26_WRITE:
        {
            uint32_t address = app_consoleData.sst26Address;
            size_t dataLen = app_consoleData.sst26Length;

            if (false == DRV_SST26_SectorErase(app_consoleData.sst26Handler, address))
            {
                app_consoleData.error = ERR_CODE_SST26_ERASE;
                app_consoleData.state = APP_CONSOLE_ERROR;
                break;
            }

            while (DRV_SST26_TransferStatusGet(app_consoleData.sst26Handler) == DRV_SST26_TRANSFER_BUSY);

            if (DRV_SST26_PageWrite(app_consoleData.sst26Handler, (void *)app_consoleData.pData, dataLen) == false)
            {
                app_consoleData.error = ERR_CODE_SST26_WRITE;
                app_consoleData.state = APP_CONSOLE_ERROR;
                break;
            }

            while (DRV_SST26_TransferStatusGet(app_consoleData.sst26Handler) == DRV_SST26_TRANSFER_BUSY);

            SYS_CONSOLE_Print(SYS_CONSOLE_INDEX_0, "Write %u bytes in SST26 memory successfully\r\n", dataLen);

            app_consoleData.state = APP_CONSOLE_RUNNING;
            break;
        }

        case APP_CONSOLE_SST26_READ:
        {
            uint32_t address = app_consoleData.sst26Address;
            size_t dataLen = app_consoleData.sst26Length;

            if (DRV_SST26_Read(app_consoleData.sst26Handler, (void *)app_consoleData.pData, dataLen, address) == false)
            {
                app_consoleData.error = ERR_CODE_SST26_READ;
                app_consoleData.state = APP_CONSOLE_ERROR;
                break;
            }

            while (DRV_SST26_TransferStatusGet(app_consoleData.sst26Handler) == DRV_SST26_TRANSFER_BUSY);

            SYS_CONSOLE_Print(SYS_CONSOLE_INDEX_0, "Read SST26 memory: %s\r\n", app_consoleData.pData);

            app_consoleData.state = APP_CONSOLE_RUNNING;
            break;
        }

        case APP_CONSOLE_SSD_WRITE:
        {
            uint32_t address = app_consoleData.ssdAddress;
            size_t dataLen = app_consoleData.ssdLength;

            if (APP_SDCARD_Write(address, app_consoleData.pData, dataLen) == false)
            {
                app_consoleData.error = ERR_CODE_SSD_WRITE;
                app_consoleData.state = APP_CONSOLE_ERROR;
                break;
            }

            SYS_CONSOLE_Print(SYS_CONSOLE_INDEX_0, "Write %u bytes in SSD memory successfully\r\n", dataLen);

            app_consoleData.state = APP_CONSOLE_RUNNING;
            break;
        }

        case APP_CONSOLE_SSD_READ:
        {
            uint32_t address = app_consoleData.ssdAddress;
            size_t dataLen = app_consoleData.ssdLength;

            if (APP_SDCARD_Read(address, app_consoleData.pData, dataLen) == false)
            {
                app_consoleData.error = ERR_CODE_SSD_WRITE;
                app_consoleData.state = APP_CONSOLE_ERROR;
                break;
            }

            SYS_CONSOLE_Print(SYS_CONSOLE_INDEX_0, "Read %u bytes from SSD memory: %s\r\n", dataLen, app_consoleData.pData);

            app_consoleData.state = APP_CONSOLE_RUNNING;
            break;
        }

        /* The default state should never be executed. */
        default:
        {
            /* TODO: Handle error in application's state machine. */
            break;
        }
    }
}


/*******************************************************************************
 End of File
 */
