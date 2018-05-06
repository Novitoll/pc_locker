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


class MainReader(SerialReader):
    KEY_CARD_UID = "Card UID"

    def __init__(self, *args, **kwargs):
        super(MainReader, self).__init__(*args, **kwargs)
        self.attempt = 0

    def pin_code_validate(self):
        pin_code = []

        while len(pin_code) != len(VALID_PIN_CODE):
            line = super(MainReader, self).read_line()
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
        uid = line.split("%s:" % self.KEY_CARD_UID)[1].strip()
        return uid == VALID_RFID_UID


def main(args):
    rfid = MainReader(port=args.dp, baudrate=args.sbaud)

    while True:
        try:
            line = rfid.read_line()
            if line:
                print("LINE:%s" % line)

                # rfid
                if rfid.KEY_CARD_UID in line:
                    rfid_uid_valid = rfid.uid_validate(line)
                    if rfid_uid_valid:
                        rfid.pc_action(command=UNLOCK)
                    else:
                        rfid.pc_action(command=LOCK)
                        sleep(10)

                # keypad
                if line == "*":
                    print("Please enter pin code:")
                    pin_code_valid = rfid.pin_code_validate()
                    if pin_code_valid:
                        rfid.pc_action(command=UNLOCK)
                        continue

                # bluetooth
                if line == "u":
                    rfid.pc_action(command=UNLOCK)
                elif line == "l":
                    rfid.pc_action(command=LOCK)
        except Exception as exc:
            print("Exception occurred {}".format(exc))
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dp", default="/dev/ttyACM2", help="Device that Arduino is connected with this PC")
    parser.add_argument("--sbaud", default=9600, help="Serial number that Arduino listens to RFID")
    args = parser.parse_args()
    main(args)
