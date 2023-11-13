# Mbed CE CI Shield v2
![CI Shield Board Photo](https://app.box.com/shared/static/sus1jw2syzq1cniygclq2agn0icui5ii.jpg)
This repository contains version 2 of Mbed OS Community Edition's CI Test Shield board.  This PCB is designed to help test the low-level I/O functionality of many different MCUs supported by Mbed OS.

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
- 1x Power USB Port (designed to be connected to a power source like a travel charger, data lines not hooked up)
- 1x Data USB Port (designed to be connected to a test runner machine, potentially a single board computer without too much power)

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

## Board Design Files

The top level schematic of the board looks like this:
![Schematic First Page](https://app.box.com/shared/static/wtlwuf5gnrsw1ivigsv61j54yn62e4ua.png)

The complete schematic PDF can be seen here: https://github.com/mbed-ce/mbed-ce-ci-shield-v2/blob/master/Design%20Files/Rev1/docs/mbed-ce-ci-shield-v2-schematic.pdf

## The Logic Analyzer

### Input Mapping

Logic analyzer inputs are muxed by the FUNC_SEL[0..2] pins.

| Analyzer Input | FUNC_SEL = 000 | FUNC_SEL = 001 | FUNC_SEL = 010 | FUNC_SEL = 1xx |
|---|---|---|---|---|
| D0 | UART.MCU_RX | I2C.SCL | SPI.SCLK | NC |
| D1 | UART.MCU_TX | I2C.SDA | SPI.MOSI | NC |
| D2 | UART.RTS | NC | SPI.MISO | NC |
| D3 | UART.CTS | NC | SPI.HW_CS | NC |
| D4 | SPI.SD_CS | SPI.SD_CS | SPI.SD_CS | SPI.SD_CS |
| D5 | GPOUT0 | GPOUT0 | GPOUT0 | GPOUT0 |
| D6 | GPOUT1/PWM | GPOUT1/PWM | GPOUT1/PWM | GPOUT1/PWM |
| D7 | GPOUT2 | GPOUT2 | GPOUT2 | GPOUT2 | 


## Board Bringup and Testing
### Flashing Firmware on New Boards

To flash the logic analyzer firmware, use [the mbed-ce fork of fxload](https://github.com/mbed-ce/fxload).  After installing it (and setting up udev rules, if on Linux), run the following command from the repo root:

```
$ fxload load_eeprom --ihex-path Firmware/fx2lafw-sigrok-fx2-8ch.ihx -t FX2LP --control-byte 0xC2
```

## Using the Logic Analyzer
The logic analyzer integrated into this board runs firmware from the Sigrok project, and is designed to be used with the sigrok CLI and the PulseView GUI.  This provides a complete set of open-source tools for capturing and decoding traffic moving across the board.

### Side Note: Sigrok Windows Issues
Unfortunately, the Sigrok project currently has extremely shoddy support for using USB-based logic analyzers when running on Windows, and I was not ultimately able to get it working.  I did a bit of a deep dive into what's going on here, including looking through the source code, and came up with the following information.

Internally, sigrok uses the epoll mechanism to handle asynchronous events.  Libusb, which it uses to communicate with USB devices, has never supported epoll on Windows in official releases.  However, back in like 2015, someone made a [fork](https://github.com/libusb/libusb/issues/252) called "event abstraction" of libusb-1.0 which added this support.  Ever since then, even though it was never merged or updated, sigrok [has used](https://sigrok.org/bugzilla/show_bug.cgi?id=1593) this fork to provide USB support on Windows.  

Unfortunately, in my testing, this old libusb version no longer seems to function reliably on Windows 10 and 11 machines.   It seems like factors such as the direction of the wind, blue whale migration patterns, and the mood of the river spirits determine whether it will actually be able to connect to a given USB device.  Even unplugging other USB devices or moving the board to a different machine sometimes made a difference.  With the same exact machines and hardware, fxload (built against the latest libusb) works perfectly reliably.  So I can only assume that this behavior is due to a bug or compatibility issue between Windows 10/11 and that old version of libusb.

More recently, in the nightlies after the sigrok-cli 0.7.2 and pulseview 0.4.2 releases, sigrok switched to building with the mainline version of libusb.  However, this version does not contain epoll emulation support, so any attempt by a sigrok driver to connect to a USB device on Windows will fail with an internal error.  It simply does not work and cannot be made to work -- I can only assume that the sigrok devs did not realize that it would completely break things when they made the change.  

As far as I can tell, the only way to fix this situation would be to refactor libsigrok's internals to use the libusb-1.0 threaded API (which is fully supported on windows) instead of the epoll-based API.  I raised this concern to the sigrok developers on IRC, and they did not seem interested in doing this refactor anytime soon.

So, TL;DR: sigrok-cli <=0.7.2 has buggy USB device support on Windows and sigrok-cli >0.7.2 has no USB device support at all, and no fix is currently planned.  Infinite sadness.  I can only hope that someone at sigrok HQ changes their mind about this someday -- perhaps the next major release breaking all USB devices on windows will raise a little more awareness.

Note that I would have reported this information on sigrok's bugzilla, but the developers refused to create an account for me.  So putting it here instead.

### Using the Logic Analyzer via WSL2 on Windows
If you have Windows 11 and WSL2, you can proxy USB devices to WSL using `usbipd`.  I found that this worked perfectly fine for the FX2 logic analyzer on the board.  First install usbipd using [these instructions](https://github.com/dorssel/usbipd-win/wiki/WSL-support).  Then, follow the linux instructions which follow.

### Using the Logic Analyzer on Linux
First, you need to install the udev rules. Copy the 60-libsigrok.rukes and 61-libsigrok-plugdev.rules files from [here](https://github.com/sigrokproject/libsigrok/blob/master/contrib/) into /etc/udev/rules.d.  Then, make sure your user account is in the `plugdev` group.  Finally, run:
```
$ sudo udevadm control --reload-rules
$ sudo udevadm trigger
```

If on WSL2 and the first command gives an error, run
```
$ sudo service udev restart
```
first.

You should now be able to run sigrok without root.  Now, you can run:
```
$ sigrok-cli -d fx2lafw --scan
```
and you should see something like
```
The following devices were found:
fx2lafw:conn=1.4 - sigrok FX2 LA (8ch) with 8 channels: D0 D1 D2 D3 D4 D5 D6 D7
```
This means your logic analyzer is working!


## Building the Design with KiBot