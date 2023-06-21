/*******************************************************************************
  MPLAB Harmony Application Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app.c

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

#include "app.h"
#include "string.h"

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
    This structure should be initialized by the APP_Initialize function.

    Application strings and buffers are be defined outside this structure.
*/

APP_DATA appData;

// *****************************************************************************
// *****************************************************************************
// Section: Application Callback Functions
// *****************************************************************************
// *****************************************************************************

/* TODO:  Add any necessary callback functions.
*/

// *****************************************************************************
// *****************************************************************************
// Section: Application Local Functions
// *****************************************************************************
// *****************************************************************************


typedef struct {
    size_t dataIndex;
    uint32_t dataBitMask[8];
    uint32_t dataAcc[8];
} DEITLV_DATA;

static DEITLV_DATA deitlvData;

static uint8_t itlvShiftRegs[] = {0b00000000, 0b01000000, 0b01100000, 0b01110000, 0b01111000, 0b01111100, 0b01111110, 0b01111111};
static uint32_t dataBitMaskInit[] = {0x0000000F, 0xF0000000, 0x0F000000, 0x00F00000, 0x000F0000, 0x0000F000, 0x00000F00, 0x000000F0};

/**
 * \brief Meters and More Interleaver.
 *
 * \param puc_in  Pointer to interleaver input.
 * \param puc_out  Pointer to interleaver output.
 * \param us_length  Data length in bytes.
 */
uint16_t itlv_mm(uint8_t *puc_in, uint8_t *puc_out, uint16_t us_length)
{
	uint8_t inputByte;
    uint8_t outputByte;
    size_t len = 0;
   
    for (uint8_t dataIndex = 0; dataIndex < us_length + 7; dataIndex++)
    {
        outputByte = 0;
        inputByte = (dataIndex <= us_length)? *puc_in++ : 0;
        for (uint16_t bitIndex = 0; bitIndex < 8; bitIndex++)
        {
            // Update value in itlvShiftRegs
            if ((inputByte & (1 << bitIndex)) != 0)
            {
                itlvShiftRegs[bitIndex] |= 0x80;
            }
            // Update output value
            if ((itlvShiftRegs[bitIndex] & (1 << (7 - bitIndex))) > 0)
            {
                outputByte |= (1 << bitIndex);
            }
            
            // Shift itlvShiftRegs for next iteration
            itlvShiftRegs[bitIndex] >>= 1;
        }
        *puc_out++ = outputByte;
        len++;
    }
    
    return len;
}

/**
 * \brief Meters and More Deinterleaver initialization.
 *
 */
void deitlv_mm_init(void)
{
    deitlvData.dataIndex = 0;
    memcpy(deitlvData.dataBitMask, dataBitMaskInit, sizeof(deitlvData.dataBitMask));
    memset(deitlvData.dataAcc, 0, sizeof(deitlvData.dataAcc));
}

/**
 * \brief Meters and More Deinterleaver. It can be performed in several steps.
 *
 * \param puc_in  Pointer to interleaver input.
 * \param us_length  Step size in bytes.
 */
uint16_t deitlv_mm(uint8_t *puc_in, uint8_t *puc_out, uint16_t us_step_size)
{
	size_t dataIndexInit = deitlvData.dataIndex;
    size_t len = 0;
    uint32_t input32b;
    uint8_t dataIndex;

    for (dataIndex = dataIndexInit; dataIndex < (dataIndexInit + us_step_size); dataIndex++)
    {
        uint32_t bitMask;
        uint8_t dataAccIndex;
        uint8_t dataACCIndexStart = dataIndex % 8;

        input32b = *puc_in++ << 24;
        input32b += *puc_in++ << 16;
        input32b += *puc_in++ << 8;
        input32b += *puc_in++;

        for (uint8_t bitIndex = 0; bitIndex < 8; bitIndex++)
        {
            dataAccIndex = dataACCIndexStart - bitIndex;
            if (dataAccIndex > 0xF0)
            {
                dataAccIndex += 8;
            }

            bitMask = deitlvData.dataBitMask[dataAccIndex];
			deitlvData.dataAcc[dataAccIndex] &= ~bitMask;
			deitlvData.dataAcc[dataAccIndex] |= (input32b & bitMask);

            // Update dataBitMask
            deitlvData.dataBitMask[dataAccIndex] = (bitMask == 0xF0000000)? 0x0000000F : (bitMask << 4);

        }

        if (dataIndex >= 7)
        {
            uint32_t value32 = deitlvData.dataAcc[dataAccIndex];

            for (uint8_t groupIndex = 7; groupIndex < 128; groupIndex--)
            {
                // Catch 4-bit group
                uint8_t data = (value32 >> (groupIndex << 2)) & 0x0F;
                // Extend sign bit
                if (data & 0x08)
                {
                    data |= 0xF0;
                }
                // Convert to 8-bit group: val8b = val4b*2 + 1
                data = (data << 1) + 1;
                // Write output
                *puc_out++ = data;
                len++;
            }
        }
    }

    deitlvData.dataIndex = dataIndex;

    return len;
}

static size_t prepareDataToDEITLV(uint8_t *srcData, uint8_t *dstData, size_t length)
{
    uint32_t outputValue32;
    size_t len = 0;
    
    while(length < 0xF000)
    {
        uint8_t inputValue = *srcData;
        outputValue32 = 0;
        for (uint8_t idx = 0; idx < 8; idx++)
        {
            if (inputValue & (1 << idx))
            {
                outputValue32 |= (0x0F << (idx << 2));
            }
        }
        
        *dstData++ = (outputValue32 >> 24) & 0xFF;
        *dstData++ = (outputValue32 >> 16) & 0xFF;
        *dstData++ = (outputValue32 >> 8) & 0xFF;
        *dstData++ = outputValue32 & 0xFF;
        len += 4;
        
        srcData++;
        length--;
    }
}

static void extractDataFromDEITLV(uint8_t *srcData, uint8_t *dstData, size_t length)
{
    uint32_t srcValue;
    uint32_t mask;
    uint8_t dstValue;
    
    for (uint8_t index = 0; index < length; index += 4)
    {
        dstValue = 0;
        srcValue = (uint32_t)(*srcData++) << 24;
        srcValue += (uint32_t)(*srcData++) << 16;
        srcValue += (uint32_t)(*srcData++) << 8;
        srcValue += (uint32_t)(*srcData++);
        
        for (uint8_t idx = 0; idx < 8; idx++)
        {
            mask = 0x0F << (idx << 2);
            if (srcValue & mask)
            {
                dstValue |= (1 << idx);
            }
        }
        
        *dstData++ = dstValue;
    }
}

/*******************************************************************************
  Function:
    void APP_Initialize ( void )

  Remarks:
    See prototype in app.h.
 */
//static uint8_t inputDataITLV[] = {221,170,80,26,144,171,160,210,79,154};
static uint8_t inputDataITLV[] = {0xdf, 0xf3, 0xc7, 0x98, 0xcf, 0x29, 0xa5, 0xc0, 
0x39, 0x72, 0xb6, 0xf2, 0xf7, 0xc6, 0x2d, 0xef};


static uint8_t outputDataITLV[30] = {0};
static uint8_t outputDataDEITLV[30] = {0};
static uint8_t outputData2DEITLV[30] = {0};


static uint8_t deitlvInputData[40] = {0};
static uint8_t deitlvOutputData[80] = {0};
static uint8_t extractedData[20] = {0};

void APP_Initialize ( void )
{
    size_t outputLenITLV;
    size_t outputLenDEITLV;
//    size_t outputLen2DEITLV;
//    size_t outputLen3DEITLV;
//    
//    uint8_t *pDataIn;
//    uint8_t *pDataout;
//    size_t inputLen;
//    size_t outputLen;


    /* Place the App state machine in its initial state. */
    appData.state = APP_STATE_INIT;
    
    deitlv_mm_init();
    
    outputLenITLV = itlv_mm(inputDataITLV, outputDataITLV, sizeof(inputDataITLV));
    
    prepareDataToDEITLV(outputDataITLV, deitlvInputData, outputLenITLV);
    
    outputLenDEITLV = deitlv_mm(deitlvInputData, outputDataDEITLV, outputLenITLV);
    
    extractDataFromDEITLV(outputDataDEITLV, extractedData, outputLenDEITLV);
    
    
    
    
//    deitlv_mm_init();
//    // Paso 1: Sacar 1 byte. Se necesitan los 8 primeros bytes para sacar 1.
//    pDataIn = &outputDataITLV[0];
//    pDataout = &outputData2DEITLV[0];
//    inputLen = 8;
//    outputLen = deitlv_mm(pDataIn, pDataout, inputLen);
//    // PAso 2: Sacar 3 bytes mas. Llevamos 4. En total son 10.
//    pDataIn += inputLen;
//    pDataout += outputLen;
//    inputLen = 3;
//    outputLen = deitlv_mm(pDataIn, pDataout, inputLen);
//    // PAso 3: Sacar 4 bytes mas. Llevamos 8. En total son 10.
//    pDataIn += inputLen;
//    pDataout += outputLen;
//    inputLen = 4;
//    outputLen = deitlv_mm(pDataIn, pDataout, inputLen);
//    // PAso 4: Sacar 2 bytes mas. Llevamos 10. En total son 10.
//    pDataIn += inputLen;
//    pDataout += outputLen;
//    inputLen = 2;
//    outputLen = deitlv_mm(pDataIn, pDataout, inputLen);

    

    /* TODO: Initialize your application's state machine and other
     * parameters.
     */
}


/******************************************************************************
  Function:
    void APP_Tasks ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Tasks ( void )
{

    /* Check the application's current state. */
    switch ( appData.state )
    {
        /* Application's initial state. */
        case APP_STATE_INIT:
        {
            bool appInitialized = true;


            if (appInitialized)
            {

                appData.state = APP_STATE_SERVICE_TASKS;
            }
            break;
        }

        case APP_STATE_SERVICE_TASKS:
        {

            break;
        }

        /* TODO: implement your application state machine.*/


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
