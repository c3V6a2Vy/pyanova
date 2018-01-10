#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

import sys
from gattlib import GATTRequester, GATTResponse


class NotifyingGATTRequester(GATTRequester):
    def __init__(self, *args):
        GATTRequester.__init__(self, *args)
        self._data_buff = ''

    def on_notification(self, handle, data):
        print [ord(c) for c in data]
        self._data_buff += data[3:]
        if data.endswith('\r'):
            print "Notification from handle [{}]: {}\n".format(handle, self._data_buff)
            self._data_buff = ''

class Writer(object):
    def __init__(self, address):
        self.requester = NotifyingGATTRequester(address, False)
        self.connect()
        self.gattresp = GATTResponse()

    def connect(self):
        print "Connecting...\n"
        sys.stdout.flush()

        self.requester.connect(True)
        print "OK!\n"

    def send_data(self, handle, strdata):
        self.requester.write_by_handle(handle, "%s\r"%(strdata.strip()))

    def disconnect(self):
        self.requester.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <addr>\n".format(sys.argv[0]))
        sys.exit(1)
    dev_addr = sys.argv[1]
    writer = Writer(dev_addr)
    handle=0x25
    while (True):
        ri = raw_input("[%s] > " % (dev_addr))
        if ri.startswith('sethandle:'):
            handle = int(ri.split(':')[1].strip(), 16)
            print "[%s] < Handle set to %s | %d \n" % (dev_addr, handle, str(handle))
        elif ri.startswith('bye'):
            writer.disconnect()
            print "Done."
            break
        else:
            if handle is None:
                print "Handle is not set, use sethandle:0x?? command to set handle\n"
            else:
                print "[%s] < Sending data to handle %s: %s \n" % (dev_addr, handle, ri)
                writer.send_data(handle, ri)
