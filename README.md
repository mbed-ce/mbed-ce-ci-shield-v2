# Mbed CE CI Shield v2
![CI Shield Board Photo](https://app.box.com/shared/static/sus1jw2syzq1cniygclq2agn0icui5ii.jpg)
This repository contains version 2 of Mbed OS Community Edition's CI Test Shield board.  This PCB is designed to help test the low-level I/O functionality of many different MCUs supported by Mbed OS.

## High Level Functionality
This board contains the following hardware:
- 1x Infineon (Cypress) CY7C65632 4-Port USB 2.0 Hub
  - 2 ports are available externally, 2 ports are connected internally
- 1x Infineon (Cypress) CY7C65211 USB to SPI/I2C/UART adapter
  - This is connected to a number of different data lines via 4-to-1 multiplexer ICs.
- 1x Infineon (Cypress) FX2LP USB Microcontroller
  - This is programmed with Sigrok FX2LAFW firmware to turn it into an inexpensive plug-and-play logic analyzer
- 1x MicroSD card slot
- 1x 24FC64-I/SN 8KiB EEPROM
- 1x PWM to ADC loopback
- 1x Power USB Port (designed to be connected to a power source like a travel charger, data lines not hooked up)
- 1x Data USB Port (designed to be connected to a test runner machine, potentially a single board computer without too much power)

*Note: I swear I'm not sponsored by Infineon or anything, it just so happened that their chips were the best fit for everything I needed on the board.  I even tried to use an FT232H in the first rev of the hardware, but I could not for the life of me get it to work.*

It can test up to 10 different types of IO:
| IO Type | Test Method |
|---|---|
| **USB Device** | The Mbed target's USB Device port can be connected to one of the shield's downstream USB ports |
| **SPI Master** | The Mbed target can interact with the MicroSD card.  The logic analyzer can observe this interaction. |
| **SPI Slave** | The CY7C65211 can initiate SPI transactions which are handled by the MCU.  The logic analyzer can observe this interaction. |
| **I2C Master** | The Mbed target can talk to the EEPROM over I2C.  The logic analyzer can observe this interaction. |
| **I2C Slave** | The CY7C65211 can initiate I2C transactions which are handled by the MCU.  The logic analyzer can observe this interaction. |
| **UART** | The MCU can communicate with the CY7C65211 bidirectionally over UART.  The logic analyzer can observe this interaction. |
| **GPIO** (incl. interrupts) | The shield has 3 sets of "looped back" GPIOs, through which the MCU can send signals to itself.  The logic analyzer can observe this interaction. |
| **PWM** | The MCU outputs a PWM signal via GPIN1.  The logic analyzer measures the frequency and duty cycle. |
| **ADC** (AnalogIn) | The MCU outputs a PWM signal, which is averaged via an RC filter into a voltage.  This voltage is fed into the ADC and the test verifies whether it's read correctly. |
| **DAC** (AnalogOut) | The DAC outputs an analog signal which is fed into an ADC pin.  The test verifies whether the output matches the input. |

## Board Design Files

The complete schematic PDF can be seen here: https://github.com/mbed-ce/mbed-ce-ci-shield-v2/blob/master/Design%20Files/Rev2/docs/mbed-ce-ci-shield-v2-schematic.pdf

## The Logic Analyzer

### Input Mapping

Logic analyzer inputs are muxed by the FUNC_SEL[0..2] pins.

| Analyzer Input | FUNC_SEL = 000 | FUNC_SEL = 001 | FUNC_SEL = 010 | FUNC_SEL = 1xx |
|---|---|---|---|---|
| D0 | UART.MCU_TX | NC | SPI.HW_CS | NC |
| D1 | UART.RTS | I2C.SCL | SPI.MISO | NC |
| D2 | UART.CTS | I2C.SDA | SPI.MOSI | NC |
| D3 | UART.MCU_RX | NC | SPI.SCLK | NC |
| D4 | SPI.SD_CS | SPI.SD_CS | SPI.SD_CS | SPI.SD_CS |
| D5 | GPOUT0 | GPOUT0 | GPOUT0 | GPOUT0 |
| D6 | GPOUT1/PWM | GPOUT1/PWM | GPOUT1/PWM | GPOUT1/PWM |
| D7 | GPOUT2 | GPOUT2 | GPOUT2 | GPOUT2 | 


## Board Bringup and Testing
### Initial Testing
Before powering on a board, check that the resistance across the 5V rail is at least 10kOhms and the resistance across the 3V3 rail is at least 600 ohms.  These rails can be found on the LD1117S33 voltage regulator pins.  If these resistance checks fail, you almost certainly have a short somewhere.

When you first plug in a board, you should see three USB devices enumerate:
- One "Cypress Semiconductor Corp. Unprogrammed CY7C65632/34 hub HX2VL"
- One "Cypress Semiconductor Corp. USB-Serial (Single Channel)"
- One FX2LP in no-EEPROM mode (TODO what is this named in lsusb?)

If these USB devices do not enumerate, double-check the circuitry for the chips that don't enumerate.

Additionally, the current draw of the board should be between ~14mA and ~100mA when no Mbed board is connected.  A USB-C power meter (e.g. [this one](https://www.amazon.com/YOJOCK-Multimeter-Capacity-Voltmeter-Detector/dp/B0B99Z2GJK/ref=sr_1_9?dib=eyJ2IjoiMSJ9.iX__gGmXBPxxHfNBzHxyfFgmTumfZEwPzNiqHgM-xjpKqZPnhOuJR1RiFy9FZd9ywnokZULX3uNuLn3wjPfRzMTa6wi9CuISauNXOu6fG7H42mFD_JcXo6YkIb4BTH0TeAXOhVcqFAUZVJzWdGv3LkE6tN-ZSztvhJ_B8Q743Y4SdjQ1yXoat4ZTFl21J7AWT0NIZBzon9ufCeXE1DIOapZ1UtwN8YUdWXMnL6Na9XfRSr-9XrJQDiP0O8BlMa1EuW7bwhreSt4rebeifAKf5IgKVMM9mwSHv_Q01_jeqCs.-UOXTx2C3OK_0aZgVHIznGnAXKxyaKn3s9FG-mkci_g&dib_tag=se&keywords=usb+c+power+meter&qid=1714315489&sr=8-9)) is highly recommended when testing new boards.

### Flashing Logic Analyzer Firmware

To build and flash the logic analyzer firmware, you will need [Small Device C Compiler](https://sdcc.sourceforge.net/).  On Ubuntu, this can be installed with `sudo apt install sdcc sdcc-libraries`.  You will also need [the mbed-ce fork of fxload](https://github.com/mbed-ce/fxload).  Lastly, you will need access to a Linux command line environment -- WSL or MSYS2 should work if on Windows.

After installing these (and setting up udev rules for fxload, if on Linux), run the following commands from the repo root:

```
$ cd Firmware
$ python3 fx2lafw_update_serial_number.py 001 <replace 001 with the serial number you want to give this board>
$ cd sigrok-firmware-fx2lafw
$ ./autogen.sh
$ mkdir build
$ cd build
$ ../configure
$ make
$ fxload load_eeprom --ihex-path hw/sigrok-fx2-8ch/fx2lafw-sigrok-fx2-8ch.ihx -t FX2LP --control-byte 0xC2
```

Finally, unplug and replug the board from power and data.

Note: The python script run in step 2 works by modifying one of the fx2lafw source files to inject a unique serial number into the firmware, as I wasn't able to find any other way to do this.

### Flashing USB-Serial Adapter Configuration

To configure the USB-serial adapter (the CY7C65211), you will need to use Mbed CE's [cy_serial_bridge](https://github.com/mbed-ce/cy_serial_bridge) library.  This can be installed using `python3 -m pip install cy_serial_bridge`.  Then, we can use the following commands to load a configuration and program the serial number.

```
$ cy_serial_cli --pid 0x00fb load Firmware\CY7C65211-Configs\mbed_ce_cy7c65211a_cdc_base_config.bin
$ cy_serial_cli reconfigure --set-serno ShieldSN001 <replace 001 with the serial number you want to give this board>
$ cy_serial_cli change-type I2C # Change to I2C initially so it will not drive any lines on the board
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