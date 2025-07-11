﻿![Microchip logo](https://raw.githubusercontent.com/wiki/Microchip-MPLAB-Harmony/Microchip-MPLAB-Harmony.github.io/images/microchip_logo.png)
![Harmony logo small](https://raw.githubusercontent.com/wiki/Microchip-MPLAB-Harmony/Microchip-MPLAB-Harmony.github.io/images/microchip_mplab_harmony_logo_small.png)

# Microchip MPLAB® Harmony 3 Release Notes

## SHD Release v1.2.0

This release adds support for the following development kits and extension boards:

- **Host boards support**
  - **PIC32CM JH/JH01**
    - PIC32CM JH-Value Line Curiosity Nano + Touch - Nano Base
    - PIC32CM JH-Value Line Curiosity Nano + Touch - Nano Explorer
    - PIC32CM JH01 Curiosity Nano+ Touch - Nano Base
    - PIC32CM JH01 Curiosity Nano+ Touch - Nano Explorer
  - **PIC32CM GV**
    - PIC32CM GV Curiosity Nano + Touch - Nano Base
    - PIC32CM GV Curiosity Nano + Touch - Nano Explorer
  - **PIC32CM LS00**
    - PIC32CM LS00 Curiosity Nano + Touch - Nano Base
    - PIC32CM LS00 Curiosity Nano + Touch - Nano Explorer
  - **PIC32CM MC00**
    - PIC32CM MC00 Curiosity Nano + Touch - Nano Base
    - PIC32CM MC00 Curiosity Nano + Touch - Nano Explorer
  - **WBZ451H**
    - WBZ451HPE EVB Board
  - **PIC32WM_BZ6204**
    - WBZ653 Curiosity Board
- **Click/Add-on boards support**
  - **Click boards**
    - Weather click
    - Heart Rate 9 click
    - USB I2C click
    - USB SPI click
    - USB UART click
    - GSM GPS click
    - IR Thermo 2 click
    - LED Driver 3 click
    - Thumbstick click
    - Fan click
    - PIR click
    - OLED C Click
    - WIFI 7 click
    - RFID click
    - BLE 2 click
    - GRID EYE click
    - LR click
    - Elink E-Paper display click
    - 13DOF click
    - microSD click
    - DRAM click
    - Flash 2 click
 
- **New Features and Enhancements**
  - Added multi-processor capability in board configuration files:
    - pic32-wfi32-20-curiosity: WFI32E03, PIC32MZ2051W104132
    - pic32-wfi32e-curiosity: WFI32E01, PIC32MZ1025W104132
    - wfi32e02-hpc-curiosity: WFI32E02, PIC32MZ1025W104132
    - wfi32e04-hpc-20-curiosity: WFI32E04, PIC32MZ2051W104132
    - wfi32e-iot-20-db: WFI32E03, PIC32MZ2051W104132
    - wfi32e-iot-db: WFI32E01, PIC32MZ1025W104132

  - Enhanced analysis of configured I2C/SPI signals to allow communication buses.
  
- **Bug Fixes**
  - Replaced Ethernet interface by Ethernet External conntector in the following boards:
    - pic32ck-gc01-curiosity-ultra
    - pic32ck-sg01-curiosity-ultra
    - pic32mz-ef-curiosity

**Known issues**
  - None.

**Development Tools**

- [MPLAB® X IDE v6.25](https://www.microchip.com/mplab/mplab-x-ide)
- MPLAB® X IDE plug-ins:
  - MPLAB® Code Configurator 5.5.1 or higher
- MPLAB® Harmony3 Library 1.5.5-b or higher

## SHD Release v1.1.0

This release adds support for the following development kits and extension boards:

- **Host boards support**
  - **PIC32CM GC/SG**
    - PIC32CM GC Curiosity Pro Development Board
    - PIC32CM SG Curiosity Pro Development Board
  - **PIC32MK MCJ**
    - PIC32MK MCJ Curiosity Pro Development Board
 
- **New Features and Enhancements**
  - Added support for NC (non-configurable) pins in the board description files.
  - Improved support for interrupt sense configuration.
  
- **Bug Fixes**
  - Fixed file generation for Trustzone devices
  - Fixed configuration values for Wincs02 add-on board.

**Known issues**
  - None.

**Development Tools**

- [MPLAB® X IDE v6.20](https://www.microchip.com/mplab/mplab-x-ide)
- MPLAB® X IDE plug-ins:
  - MPLAB® Code Configurator 5.5.1 or higher
- MPLAB® Harmony3 Library 1.5.5-b or higher

## SHD Release v1.0.0

This release adds support for the following development kits and extension boards:

- **Host boards support**
  - **MPU**
    - SAM9X60 Curiosity
    - SAM9X75 Curiosity
    - SAMA5D27-SOM1-EK1
    - ATSAMA5D27-WLSOM1 EVALUATION KIT
    - SAMA5D29 Curiosity
    - SAMA7D65 Curiosity Kit
    - SAMA7G54 Evaluation Kit
  - **PIC32AK**
    - PIC32AK DIM + Curiosity Platform Development Board
  - **dsPIC33AK**
    - dsPIC33AK DIM + Curiosity Platform Development Board
  - **Wireless solutions**
    - WFI32E02 High Pin Count (HPC) Curiosity Board
    - WFI32E04 High Pin Count (HPC) Curiosity Board
  - **PIC32MZ DA**
    - PIC32MZ DA Curiosity
    - PIC32MZ DA Starter Kit
  - **PIC32CZ CA**
    - PIC32CZ CA70 Curiosity Ultra
    - PIC32CZ CA80 Curiosity Ultra
    - PIC32CZ CA90 Curiosity Ultra
  - **PIC32CX_MT**
    - PIC32CXMTC Curiosity Board
- **Click/Add-on boards support**
  - **Wireless add-on boards**
    - WIxCS02 M.2 Wi-Fi Module Card (SPI)
  - **Ethernet PHY boards**
    - LAN8740 Phy Board
  - **Gigabit Ethernet connectivity boards**
    - LAN8840 EDS2 Daughter Card

**Known issues**
  - None.

**Development Tools**

- [MPLAB® X IDE v6.20](https://www.microchip.com/mplab/mplab-x-ide)
- MPLAB® X IDE plug-ins:
  - MPLAB® Code Configurator 5.5.1 or higher
- MPLAB® Harmony3 Library 1.5.4 or higher

## SHD Release v1.0.0-E1

This release introduces initial support for:

- **Host boards support**
  - **SAM D5x/E5x**
    - SAM E54 Curiosity Ultra
    - SAM E54 Xplained Pro
    - SAM E51 Curiosity Nano - Nano Base
  - **PIC32CX_MT**
    - PIC32CXMTG Evaluation Kit
    - PIC32CXMTSH Development Board
    - PIC32CXMTC Development Board
  - **PIC32MZ EF**
    - PIC32MZ EF Starter Kit
    - PIC32MZ EF Curiosity 2.0
  - **PIC32MM**
    - PIC32MM Curiosity Development Board
    - PIC32MM USB Curiosity
  - **PIC32CK GC/SG**
    - PIC32CK GC Curiosity Ultra Development Board
    - PIC32CK SG Curiosity Ultra Development Board
  - **SAM C2x**
    - SAM C21 Xplained Pro
    - SAM C21N Xplained Pro
  - **SAM D21/DA1**
    - SAM D21 Xplained Pro
    - SAM D21 Curiosity Nano - Nano Base
    - SAM D20 Xplained Pro
    - SAM DA1 Xplained Pro
  - **SAM D1x**
    - SAM D10 Xplained Mini
    - SAM D11 Xplained Pro
  - **SAM E/S/V7x**
    - SAM E70 Xplained Ultra
    - SAM V71 Xplained Ultra
  - **SAMG5x**
    - SAM G55 Xplained Pro
  - **SAMLx**
    - SAM L10 Xplained Pro
    - SAM L11 Xplained Pro
    - SAM L21 Xplained Pro
    - SAM L22 Xplained Pro
  - **Wireless solutions**
    - WBZ351 EVB Board
    - WBZ451 EVB Board
    - PIC32 WFI32E Curiosity Board
    - PIC32 WFI32E 2.0 Curiosity Board
    - WFI32E IOT DB
    - WFI32E IOT 2.0 DB
- **Click/Add-on boards support**
  - **Click boards**
    - EEPROM 3 click
    - EEPROM 4 click
    - EEPROM 10 click
    - I/O1 Xplained Pro
    - PL460 Evaluation Kit (G3 MAC RT)
    - PL460 Evaluation Kit (PLC PHY)
  - **Wireless add-on boards**
    - WINCS02 add-on board
    - RNWF11
    - RNWF02
    - RNBD350
    - RNBD451
  - **Ethernet PHY boards**
    - IP101GR ETH Phy Board
    - KSZ8041 ETH Phy Board
    - KSZ8061 ETH Phy Board
    - KSZ8091 ETH Phy Board
    - LAN8720A ETH Phy Board
    - LAN8770 ETH Phy Board
    - LAN9303 ETH Phy Board
    - LAN9354 ETH Phy Board

**Known issues**
  - EIC NMI is not automatically enabled for EIC_u2217, EIC_u2254 and EIC_u2804. Will be solved in next CSP release.
  - SEVERE error message is shown when Core repository is not present. WIll be solved in next SHD release.

**Development Tools**

- [MPLAB® X IDE v6.20](https://www.microchip.com/mplab/mplab-x-ide)
- [MPLAB® XC32 C/C++ Compiler v4.45](https://www.microchip.com/mplab/compilers)
- MPLAB® X IDE plug-ins:
  - MPLAB® Code Configurator 5.5.1 or higher
- MPLAB® Harmony3 Library 1.5.4 or higher
