from __future__ import print_function
import serial
import os
import argparse
import logging
from time import sleep

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger('tcpserver')

LOCK = "l"
UNLOCK = "d"

VALID_RFID_UID = "09 D4 20 A3"
VALID_PIN_CODE = "19"
INVALID_PIN_CODE_ATTEMPTS = 3
BLOCK_TIME = 5


class SerialReader(object):
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port=port, baudrate=baudrate)

    def read_line(self):
        return self.serial.readline().strip()

    def write_line(self, data):
        return self.serial.write(data.encode('ascii'))

    def pc_action(self, command=LOCK):
        os.system('gnome-screensaver-command -%s' % command)


class RFIDReader(SerialReader):
    KEY_CARD_UID = "Card UID"

    def __init__(self, *args, **kwargs):
        super(RFIDReader, self).__init__(*args, **kwargs)
        self.attempt = 0

    def pin_code_validate(self):
        pin_code = []

        while len(pin_code) != len(VALID_PIN_CODE):
            line = super(RFIDReader, self).read_line()
            if line == "#":  # cancel
                break
            elif len(line) != 1:
                continue
            pin_code.append(line)
            print("Word RFID:%s" % "".join(pin_code))

        if VALID_PIN_CODE == "".join(pin_code):
            print("Valid")
            return True
        else:
            self.attempt += 1
            if self.attempt == INVALID_PIN_CODE_ATTEMPTS:
                self.attempt = 0
                LOGGER.warning("Reached the maximum attempts - %d. Blocked for %d sec" % (INVALID_PIN_CODE_ATTEMPTS, BLOCK_TIME))
                sleep(BLOCK_TIME)
                return False
            else:
                LOGGER.warning("Failed attempt %d. Invalid attempt of pin code. Please try again" % self.attempt)
                self.pin_code_validate()

    def uid_validate(self, line):
        valid = False
        if self.KEY_CARD_UID in line:
            print(line)
            uid = line.split("%s:" % self.KEY_CARD_UID)[1].strip()
            valid = uid == VALID_RFID_UID
        return valid


def main(args):
    rfid = RFIDReader(port=args.dp, baudrate=args.srfid)

    while True:
        line = rfid.read_line()
        if line:
            rfid_uid_valid = rfid.uid_validate(line)

            if rfid_uid_valid:
                print("Please enter pin code")
                pin_code_valid = rfid.pin_code_validate()

                if pin_code_valid:
                    rfid.pc_action(command=UNLOCK)
            else:
                rfid.pc_action(command=LOCK)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dp", default="/dev/ttyACM0", help="Device that Arduino is connected with this PC")
    parser.add_argument("--srfid", default=9600, help="Serial number that Arduino listens to RFID")
    args = parser.parse_args()
    main(args)
