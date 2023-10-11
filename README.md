# Mbed CE CI Shield v2
![CI Shield Board Photo](https://app.box.com/shared/static/sus1jw2syzq1cniygclq2agn0icui5ii.jpg)
This repository contains version 2 of Mbed OS Community Edition's CI Test Shield board.  This PCB is designed to help test the low-level I/O functionality of the many different MCUs supported by Mbed OS.

## High Level Functionality
This board contains the following hardware:
- 1x Infineon (Cypress) CY7C65632 4-Port USB 2.0 Hub
  - 2 ports are available externally, 2 ports are connected internally
- 1x FT232H Multi-Protocol USB Serial Adapter
  - It's connected to a number of different data lines via 4-to-1 multiplexer ICs.
- 1x Infineon (Cypress) FX2LP USB Microcontroller
  - This is programmed with Sigrok FX2LAFW firmware to turn it into an inexpensive plug-and-play logic analyzer
- 1x MicroSD card slot
- 1x 24FC64-I/SN 8KiB EEPROM
- 1x PWM to ADC loopback

It can test up to 10 different types of IO:
| IO Type | Test Method |
|---|---|
| **USB Device** | The Mbed target's USB Device port can be connected to one of the shield's downstream USB ports |
| **SPI Master** | The Mbed target can interact with the MicroSD card.  The logic analyzer can observe this interaction. |
| **SPI Slave** | The FT232H can initiate SPI transactions which are handled by the MCU.  The logic analyzer can observe this interaction. |
| **I2C Master** | The Mbed target can talk to the EEPROM over I2C.  The logic analyzer can observe this interaction. |
| **I2C Slave** | The FT232H can initiate I2C transactions which are handled by the MCU.  The logic analyzer can observe this interaction. |
| **UART** | The MCU can communicate with the FT232H bidirectionally over UART.  The logic analyzer can observe this interaction. |
| **GPIO** (incl. interrupts) | The shield has 3 sets of "looped back" GPIOs, through which the MCU can send signals to itself.  The logic analyzer can observe this interaction. |
| **PWM** | The MCU outputs a PWM signal via GPIN1.  The logic analyzer measures the frequency and duty cycle. |
| **ADC** (AnalogIn) | The MCU outputs a PWM signal, which is averaged via an RC filter into a voltage.  This voltage is fed into the ADC and the test verifies whether it's read correctly. |
| **DAC** (AnalogOut) | The DAC outputs an analog signal which is fed into an ADC pin.  The test verifies whether the output matches the input. |

## The Logic Analyzer

### Input Mapping

### Flashing Firmware on New Boards

