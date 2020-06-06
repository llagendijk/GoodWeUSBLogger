# GoodWeUSBLogger
Python based logger for GoodWe inverters using USB.

based on: https://github.com/sircuri/GoodWeUSBLogger which in its turn was based 
on https://github.com/jantenhove/GoodWeLogger 

## Required Python version

This software is developed for **python3** (tested on python 3.5.3) but also works under python 2.7.

```bash
sudo apt-get update
sudo apt-get install -y python-pip
```

## Required python modules

* configparser
* paho-mqtt
* pyudev
* ioctl_opt
* enum

these imodules should however be installed when you install the tool as described below.
cd into the directory where the sources are located.

```bash
python3 setup.py install
```

## Config

Create file _/etc/udev/rules.d/98-my-usb-device.rules_ with:

```bash
SUBSYSTEM=="input", GROUP="input", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0084", ATTRS{idProduct}=="0041", MODE="0660", GROUP="plugdev", SYMLINK+="goodwe"
```

Create file _/etc/goodwe.conf_:

```
[inverter]
loglevel = DEBUG
pollinterval = 5000
#vendorId = 0084
#modelId = 0041
#logfile = /var/log/goodwe.log

[mqtt]
# server = localhost
# port = 1883
# topic = goodwe
#clientid = goodwe-usb
# username = goodwe
# password = xxxxxx
# domoticz-topic = domoticz/in

[domoticz]
online = 96
power_daytotal = 104
power_grand_total = 105
errorMessage = 97
mains_frequency = 102
total_hours = 103
mains_current = 95
input1_current = 93
input2_current = 94
current_power = 99
temperature = 100
mains_voltage = 92
input1_voltage = 90
input2_voltage = 91

```
Almost all configuration parameters have sensible defaults and are commented out. The values shown are the defaults. If you need to change a 
setting remove the # in front of the parameter name.
Only when username and the optional password are set, they will be used. Setting the username will trigger authentication for the MQTT server. 
Password can optionally be set. The domoticz-topic (when defined) triggers the update to domoticz. 
The domoticz section is only read/used when domoticz-topic is set. This section contains the idx values as defined in Domoticz for the known 
data items. 

## Usage

The program will lookup the device on its own by enumerating all USB devices and look for the **_vendorId_** and **_modelId_** as listed above.
My tested GoodWe solar inverters all have these vendor and model id. You can lookup your own by connecting the USB device to the raspberry and 
look for these values in the system logs. These _should_ be the correct IDs for all GoodWe solar inverters.

The application needs to be run as **root** in the current setup. The high level logs for the daemon are written to stdout/stderr or the 
defined logfile (not normally needed).

To start the daemon application for testing:

```bash
$ sudo  goodweusb2mqtt
```

The systemd service unit goodweusb2mqtt.service in installed when the setup s run as described above.
It may be necessary to correct the path to the executable when pthon installs it in a different place.

'''bash
systemctl enable goodweusb2mqtt.service
systemctl start goodweusb2mqtt.service

## Inverter information

You can lookup the serial number of your inverter in the _/var/log/goodwe.log_ file after a succesfull start.

```
2019-06-14 17:44:42,135 run(48) - INFO: Connected to MQTT 192.168.2.240
2019-06-14 17:45:22,863 handleRegistration(415) - INFO: New inverter found with serial id: 15000DTU166W0157. Register address.
2019-06-14 17:45:23,078 handleRegistrationConfirmation(443) - INFO: Inverter now online.
```

The application will start to deliver information packets on the configured MQTT channel.
The channels are composed as:
* '**goodwe** / **_SERIALID_** / **data**' for the data packets
* '**goodwe** / **_SERIALID_** / **online**' for a simple 1 or 0 as the online status.
