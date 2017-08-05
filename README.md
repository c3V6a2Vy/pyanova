# pyanova
An Anova Precision Cooker (Sous Vide) Bluetooth API Python Wrapper

## Descirption

This is a Python wrapper of the [Anova Precision Cooker](https://anovaculinary.com/anova-precision-cooker/) (Sous Vide) API via the Bluetooth LE connection. Under the hood, it utilizes [pygattlib](https://bitbucket.org/OscarAcena/pygattlib) for the Bluetooth LE communications.

## Acknowledgements

* This work relies heavily on the researches from [dfrankland/sous-vide](https://github.com/dfrankland/sous-vide/), a very nice API for Node JS. Commands used in _pyanova_ are based on its [research on the Android APP APK](https://github.com/dfrankland/sous-vide/blob/master/docs/ble.md).
* Bluetooh LE communication is made easy with [pygattlib](https://bitbucket.org/OscarAcena/pygattlib)

## Installation

### Prerequisites

* [BlueZ](http://www.bluez.org/) - required by _pygattlib_
* [Boost](http://www.boost.org/) - required by _pygattlib_
* Have `root` permissions for interacting with your Bluetooth devices

### Install using Python pip
Once the prerequisite are satisfied, you can install _pyanova_ with pip: `pip install pyanova`

## Usage

### Determine your device's BLE MAC address

If _BlueZ_ is installed correctly, `hcitool` should be avaialble in the system. 

* List available Bluetooth devices: `hcitool dev`

	```shell
	Devices:                                                   
        hci0    38:A2:8C:66:0D:83 
	```

* Scan BLE devices: `hscitool lescan`
 
	```shell
	LE Scan ...                                                
	19:24:E1:9F:7B:6B (unknown)                                
	01:02:03:04:31:00 (unknown)                                
	24:4B:03:9B:F7:44 (unknown)                                
	28:56:5A:03:CA:AC (unknown)                                
	08:66:98:A7:31:F0 (unknown)                                
	3C:3F:E6:4E:9D:00 (unknown)                                
	88:C6:26:53:C9:94                                          
	04:52:C7:3F:93:78 (unknown)  
	```

* A valid Anova Precision Cooker MAC address is likely to start with `01:02:03:04:`

### Using the library

You can use the library's syncrhonized APIs

```python
cooker = pyanova('01:02:03:04:31:00')
# status
print "Current status: " + cooker.read_status()
print "Current temperature unit is set to: " + cooker.read_temperature_unit()

# config
cooker.set_unit_farenheit()
cooker.set_unit_celsius()

# getting ready
cooker.read_temp()
cooker.set_temp(42.5)
cooker.read_timer()
cooker.set_timer(60)

# start cooking
## Start the heating circulation
cooker.start()
## wait for the temprature to increase to targeted temprature
cooker.start_timer()
cooker.stop_timer()
## finish cooking
cooker.stop()

# exiting
cooker.disconnect()
```

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
