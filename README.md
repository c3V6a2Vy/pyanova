# pyanova
An Anova Precision Cooker (Sous Vide) Bluetooth API Python Wrapper

[![pypi-pyanova](https://img.shields.io/pypi/v/pyanova.svg?style=flat-square)](https://pypi.org/project/pyanova/)

## Descirption

This is a Python wrapper of the [Anova Precision Cooker](https://anovaculinary.com/anova-precision-cooker/) (Sous Vide) API via the Bluetooth LE connection. Under the hood, it utilizes [peplin/pygatt](https://github.com/peplin/pygatt) for the Bluetooth LE communications.

The library is tested on [C.H.I.P](https://docs.getchip.com/chip.html) with Debian + Python 2.7 and Python 3.4

## Acknowledgements

* This work relies heavily on the researches from [dfrankland/sous-vide](https://github.com/dfrankland/sous-vide/), a very nice API for Node JS. Commands used in _pyanova_ are based on its [research on the Android APP APK](https://github.com/dfrankland/sous-vide/blob/master/docs/ble.md).
* Bluetooh LE communication is made easy with [pygatt](https://github.com/peplin/pygatt)

## Installation

### Prerequisites

* [pygatt](https://github.com/peplin/pygatt) - specifically, it uses the [gatttool backend](https://github.com/peplin/pygatt/tree/master/pygatt/backends/gatttool)
* [bluez](https://git.kernel.org/pub/scm/bluetooth/bluez.git) - specifically, the gatttool backend requires [hcitool](https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c), make sure you can find `hcitool` in your system.

### Install using Python pip
Once the prerequisite are satisfied, you can install _pyanova_ with pip: `pip install pyanova`

## Usage

> The GATTTool backend normally requires __root__ permission. Hence you might need to run your program with __root__ permission or [setup passwordless sudo for 'hcitool'](https://www.sudo.ws/man/sudoers.man.html).

### Automode
You can initialize PyAnova easily with automode which will automatically discover and connect to the first available Anova device

```python
from pyanova import pyanova

pa = pyanova.PyAnova()
pa.get_status()
```

### Manual mode
Alternatively, you can fully control the discover and connect phrases of an PyAnova object

```python
from pyanova import pyanova

pa = pyanova.PyAnova(auto_connect=False)
devices = pa.discover(list_all=False, timeout=3)
pa.connect_device(devices[0])
pa.get_status()
```

### TODO
* Unit tests
* Autogen docs
* Probably swtich to [pygattlib](https://bitbucket.org/OscarAcena/pygattlib)?

### Demo
see: samples/pyanova_terminal.py

## Disclaimer
This software may harm your device. Use it at your own risk.

>THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM “AS IS” WITHOUT
WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
CORRECTION.
