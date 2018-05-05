from __future__ import print_function
import serial
import os
import argparse
from time import sleep

LOCK = "l"
UNLOCK = "d"

VALID_RFID_UID = "09 D4 20 A3"


class SerialReader(object):
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port=port, baudrate=baudrate)

    def read_line(self):
        return self.serial.readline()

    def write_line(self, data):
        return self.serial.write(data.encode('ascii'))

    def pc_action(self, command=LOCK):
        os.system('gnome-screensaver-command -%s' % command)


class RFIDReader(SerialReader):
    KEY_CARD_UID = "Card UID"

    def read_line(self):
        line = super(RFIDReader, self).read_line()
        if line:
            print("Word RFID:%s" % line)
            if self.KEY_CARD_UID in line:
                uid = line.split("%s:" % self.KEY_CARD_UID)[1].strip()

                if uid == VALID_RFID_UID:
                    self.pc_action(command=LOCK)
                else:
                    self.pc_action(command=UNLOCK)

        return line


def main(args):
    rfid = RFIDReader(port=args.dp, baudrate=args.srfid)

    while True:
        rfid.read_line()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dp", default="/dev/ttyACM0", help="Device that Arduino is connected with this PC")
    parser.add_argument("--srfid", default=9600, help="Serial number that Arduino listens to RFID")
    args = parser.parse_args()
    main(args)
