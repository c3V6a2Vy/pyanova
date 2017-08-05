#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

"""
Constants for commands and devices
"""

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
SET_CALIBRATION_FACTOR = "cal %.f" # def 0.0, [-9.9, 9.9]
SET_TARGET_TEMP = "set temp %f" # [5.0C, 99,9C] | [41.0F, 211.8F]
SET_TIMER = "set timer %d" # in minutes, [0, 6000]
SET_TEMP_UNIT = "set unit %s" # 'c'|'f'

# Controllers
CTL_START = "start"
CTL_STOP = "stop"
CTL_TIMER_START = "start time"
CTL_TIMER_sTOP = "stop time"

# The following commands are not available for the Bluetooth only version Anova
READ_DATE = "read date"
CLEAR_ALARM = "clear alarm"
GET_ID_CARD = "get id card"
SERVER_PARA = "server para %s %d"
SET_DEV_NAME = "set name %s"
SET_SECRET_KEY = "set number %s"
SET_SPEAKER_OFF = "set speaker off"

# RESPONSES
RESP_INVALID_CMD = "Invalid Command"