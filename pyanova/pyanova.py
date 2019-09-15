#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2017, c3V6a2Vy <c3V6a2Vy@protonmail.com>
# This software is under the terms of Apache License v2 or later.

"""pyanova module

This module provides constants and a thread-safe class to interact with
Anova(TM) bluetooth only devices. Anova(TM) device can be acquired from
https://anovaculinary.com/anova-precision-cooker/

Example:
    $> pip install pyanova

    import pyanova
    pa = pyanova.PyAnova()
    pa.set_unit('c')
    pa.set_temperature('42')
    pa.start_anova()
    pa.get_current_temperature()
    pa.stop_anova()

Todos:
    * add docs
    * add samples
    * add unit tests

"""


#Constants for commands and devices
DEVICE_PRIMARY_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
DEVICE_NOTIFICATION_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
DEVICE_NOTIFICATION_CHAR_HANDLE = 0X25

# Readers
READ_DEVICE_STATUS = "status" # stopped|running
READ_CALIBRATION_FACTOR = "read cal"
READ_TEMP_HISTORY = "read data"
READ_TARGET_TEMP = "read set temp"
READ_CURRENT_TEMP = "read temp"
READ_TIMER = "read timer"
READ_UNIT = "read unit"

# Setters
SET_CALIBRATION_FACTOR = "cal %.1f" # def 0.0, [-9.9, 9.9]
SET_TARGET_TEMP = "set temp %.1f" # [5.0C, 99,9C] | [41.0F, 211.8F]
SET_TIMER = "set timer %d" # in minutes, [0, 6000]
SET_TEMP_UNIT = "set unit %s" # 'c'|'f'

# Controllers
CTL_START = "start"
CTL_STOP = "stop"
CTL_TIMER_START = "start time"
CTL_TIMER_STOP = "stop time"

# The following commands are not available for the Bluetooth only version Anova
READ_DATE = "read date"
CLEAR_ALARM = "clear alarm"
GET_ID_CARD = "get id card"
SERVER_PARA = "server para %s %d"
SET_DEV_NAME = "set name %s"
SET_SECRET_KEY = "set number %s"
SET_SPEAKER_OFF = "set speaker off"

# ANOVA device BLE mac pattern
import re
DEFAULT_DEV_MAC_PATTERN = re.compile('^01:02:03:04')

# RESPONSES
RESP_INVALID_CMD = "Invalid Command"

# Connection settings
DEFAULT_TIMEOUT_SEC = 10
DEFAULT_CMD_TIMEOUT_SEC = 5
DEFAULT_SCAN_RETRIES = 2

# Logging format
import logging
DEFAULT_LOGGING_FORMATER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
DEFAULT_HANDLER = logging.StreamHandler()
DEFAULT_HANDLER.setFormatter(DEFAULT_LOGGING_FORMATER)
DEFAULT_LOGGER = logging.getLogger('pyanova_default_logger')
DEFAULT_LOGGER.addHandler(DEFAULT_HANDLER)
DEFAULT_LOGGER.setLevel(logging.INFO)

import pygatt
import threading
class PyAnova(object):
    """PyAnova class that represents an Anova device and provides methods for interactions

    operations of this class is thread-safe guarded by a `threading.Lock`_

    Attributes:
        cmd_lock (threading.Lock): lock object per command operation
        cb_cond (threading.Condition): condition object per callback operation 
        cb_resp (dict): variable for holding callback value

    """
    cmd_lock = threading.Lock()
    cb_cond = threading.Condition(threading.Lock())
    cb_resp = None

    @staticmethod
    def indication_callback(handle, value):
        """This is a callback function for `pygatt`_ BLE notification
        
        the callback function is made thread-safe by using `threading.condition`_ that's based on a `threading.lock`_ 

        .. _pygatt:
            https://github.com/peplin/pygatt/blob/91db29e7a82b36998eae56ef31a273ba4dad0851/pygatt/device.py#L131

        """
        PyAnova.cb_cond.acquire()
        PyAnova.cb_resp = {'handle': handle, 'value': value}
        PyAnova.cb_cond.notify()
        PyAnova.cb_cond.release()

    def __init__(self, auto_connect=True, logger=DEFAULT_LOGGER, debug=False):
        """This is the constructor for a pyanova.PyAnova object
        
        there are two ways of constructing a PyAnova object: 'auto mode' and 'manual mode'
        
        * 'auto mode': see `PyAnova.auto_connect()`_
        * 'manual mode': would not discover or connect to any device

        Args:
            auto_connect (bool): to use auto mode or not
            logger (logging.Logger): logger, defualt to `DEFAULT_LOGGER`_
            debug (bool): if set to Ture logger would set to `logging.DEBUG`_ level
        
        """
        self._dev = None
        self._adapter = pygatt.GATTToolBackend()
        self._logger = DEFAULT_LOGGER
        if debug: self._logger.setLevel(logging.DEBUG)
        if auto_connect: self.auto_connect()

    def __del__(self):
        """This is the destructor for a pyanova.PyAnova object

        it calls `PyAnova.disconnect()`_ for desctruction
        
        """
        self._logger.debug('destructing PyAnova object: %s'%str(self))
        self.disconnect()


    def auto_connect(self, timeout=DEFAULT_TIMEOUT_SEC):
        """This function automatically discovers and connects to the first available Anova device

        see `PyAnova.discover()`_ and `PyAnova.connect_device()`_

        Args:
            timeout (float): discover timeout setting, defualt to `DEFAULT_TIMEOUT_SEC`_

        Raises:
            RuntimeError: Already connected to a device or Anova device not found
        
        """
        if self.is_connected():
            errmsg = 'Already connected to a device: %s'%str(self._dev)
            self._logger.error(errmsg)
            raise RuntimeError(errmsg)
        self._logger.info('Auto connecting, timeout set to: %.2f'%timeout)
        anova_dev_props = self.discover(timeout=timeout)
        self._logger.debug('Found these Anova devices: %s'%str(anova_dev_props))
        if len(anova_dev_props) < 1:
            errmsg = 'Did not find Anova device in auto discover mode.'
            self._logger.error(errmsg)
            raise RuntimeError(errmsg)
        # it can control 1 device only, taking the first found Anova device
        self.connect_device(anova_dev_props[0])

    def discover(self, list_all = False, dev_mac_pattern=DEFAULT_DEV_MAC_PATTERN, timeout=DEFAULT_TIMEOUT_SEC, retries=DEFAULT_SCAN_RETRIES):
        """This function discovers nearby Bluetooh Low Energy (BLE) devices
        
        Args:
            list_all (bool): whetehr to list all discovered BLE devices or devices that matched the `dev_mac_pattern`_, default to `False`
            dev_mac_pattern (re.Pattern): compiled pattern for targeted mac addressed, default to `DEFAULT_DEV_MAC_PATTERN`_
            timeout (float): time to spent for discovering devices, default to `DEFAULT_TIMEOUT_SEC`_
            retries (int): number of retries before failing with a BLEError, defaults to `DEFAULT_SCAN_RETRIES`

        Raises:
            BLEError: Bluetooth Adapter error if a scan cannot be completed.

        Returns:
            array: array of device properties that is a dict with 'name' and 'address' as keys 
                   e.g: [{'name': 'ffs', 'address': '01:02:03:04:05:10'}, {'name': 'rlx', 'address': '01:02:03:04:05:21'}]
        
        """
        retry_count = 0
        complete = False
        while not complete:
            try:
                devices = self._adapter.scan(run_as_root=True, timeout=timeout)
                complete = True
            except pygatt.exceptions.BLEError as e:
                retry_count += 1
                if retry_count >= retries:
                    self._logger.error('BLE Scan failed due to adapter not able to reset')
                    raise e
                self._logger.info('Resetting BLE Adapter, retrying scan. {0} retries left'.format(
                    retries - retry_count))
                self._adapter.reset()
        if list_all:
            return devices
        return list(filter(lambda dev: dev_mac_pattern.match(dev['address']), devices))

    def connect_device(self, dev_prop, notification_uuid=DEVICE_NOTIFICATION_CHAR_UUID):
        """This function connects to an Anova device and register for notification

        Args:
            dev_prop: device property that is a dict with 'name' and 'address' as keys .
                      e.g: {'name': 'ffs', 'address': '01:02:03:04:05:10'}
            notification_uuid: the notification uuid to subscribe to, default to `DEVICE_NOTIFICATION_CHAR_UUID`_
                               this value should be constant for all Anova Bluetooth-only devices and can be discover
                               with gatt tool.
        
        """
        self._logger.info('Starting PyAnova BLE adapter')
        self._adapter.start()
        self._logger.info('Connecting to Anova device: %s'%str(dev_prop))
        self._dev = self._adapter.connect(dev_prop['address'])
        self._logger.info('Connected to: %s'%str(dev_prop))
        self._dev.subscribe(notification_uuid, callback=PyAnova.indication_callback, indication=True)
        self._logger.info('Subscribed to notification handle: %s'%notification_uuid)

    def disconnect(self):
        """This function disconnects from an existing Anova device and stops the BLE adapter
        
        """
        self._logger.info('Stopping PyAnova BLE adapter...')
        if self._adapter: self._adapter.stop()
        if self._dev:
            #self._dev.disconnect()
            self._dev = None
        self._logger.info('Stopped')

    def is_connected(self):
        """This function checks if an Anova device is already connected

        Returns: 
            bool: True if the device is already set
        """
        return self._dev is not None

    def _write_strcmd(self, strcmd, handle, cmd_timeout):
        """Thread-safe caller method that sends data to BLE device and wait for the response returns via notification

        There will be two level of locks: command lock and callback condition. The command lock would lock down so that no
        other thread can invoke another command. Then the function would acquire a callback condition, write to the handle 
        and wait for response to be set. The callback function is expected to produce the response and notify the thread 
        waiting for the response and then release the callback condition. Once the wait finishes, this function would be 
        holding the lock again so that we can process the response safely. Once processed, the callback lock and the command 
        lock would be released.

        Args:
            strcmd (str): command in string
            handle (int): handle of the receiver to send to
            cmd_timeout (float): timeout for waiting for response

        Returns:
            str: the response

        Raises:
            RuntimeError: times out for waiting for response

        """
        self._logger.debug('Command to be sent [%s]'%strcmd)
        bytedata = bytearray("%s\r"%(strcmd.strip()), 'utf8')
        self._logger.debug('Acquiring blocking command lock for [%s]'%strcmd)
        PyAnova.cmd_lock.acquire(True)
        PyAnova.cb_resp = None
        self._logger.debug('Acquiring callback condition lock for [%s]'%strcmd)
        PyAnova.cb_cond.acquire(True)
        self._logger.debug('Writing %s to handle: 0x%x'%(strcmd, handle))
        self._dev.char_write_handle(handle, bytedata)
        while not PyAnova.cb_resp:
            self._logger.debug('Waiting for response from callback, timeout: %.2f'%cmd_timeout)
            PyAnova.cb_cond.wait(cmd_timeout)
        self._logger.debug('Processing response from callback')
        if not PyAnova.cb_resp:
            errmsg = 'Timed out waiting for callback for command [%s]'%strcmd
            self._logger.error(errmsg)
            raise RuntimeError(errmsg)
        self._logger.debug('Received response from callback: %s'%str(PyAnova.cb_resp))
        resp = PyAnova.cb_resp['value'].decode('utf8').strip()
        PyAnova.cb_resp = None
        PyAnova.cb_cond.release()
        self._logger.debug('Released callback condition lock for [%s]'%strcmd)
        PyAnova.cmd_lock.release()
        self._logger.debug('Released command lock for [%s]'%strcmd)
        return resp

    # Read only functions (status getter and control setter)
    def get_status(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_DEVICE_STATUS, handle, timeout)

    def get_calibration_factor(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_CALIBRATION_FACTOR, handle, timeout)

    def get_temperature_history(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_TEMP_HISTORY, handle, timeout).split()

    def get_target_temperature(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_TARGET_TEMP, handle, timeout)

    def get_current_temperature(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_CURRENT_TEMP, handle, timeout)

    def get_timer(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_TIMER, handle, timeout)

    def get_unit(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(READ_UNIT, handle, timeout)

    def stop_anova(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(CTL_STOP, handle, timeout)

    def start_anova(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(CTL_START, handle, timeout)

    def stop_timer(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(CTL_TIMER_STOP, handle, timeout)

    def start_timer(self, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(CTL_TIMER_START, handle, timeout)

    # setter functions (that takes in parameters)
    def set_calibration_factor(self, cal_factor, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(SET_CALIBRATION_FACTOR%cal_factor, handle, timeout)

    def set_temperature(self, target_temp, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(SET_TARGET_TEMP%target_temp, handle, timeout)

    def set_timer(self, timer_minute, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        return self._write_strcmd(SET_TIMER%timer_minute, handle, timeout)

    def set_unit(self, unit, handle=DEVICE_NOTIFICATION_CHAR_HANDLE, timeout=DEFAULT_CMD_TIMEOUT_SEC):
        unit = unit.strip().lower()
        if unit != 'c' and unit != 'f': 
            errmsg = 'Expected unit to be either \'c\' or \'f\', found: %s'%unit
            self._logger.error(errmsg)
            raise ValueError(errmsg)
        return self._write_strcmd(SET_TEMP_UNIT%unit, handle, timeout)
