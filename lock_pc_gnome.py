from __future__ import print_function
import serial
import os
import argparse
import logging
import requests

from time import gmtime, strftime, sleep

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger('tcpserver')

LOCK = "l"
UNLOCK = "d"

VALID_RFID_UID = "80 73 C8 2B"
VALID_PIN_CODE = "1909abcd"
INVALID_PIN_CODE_ATTEMPTS = 3
BLOCK_TIME = 5

with open("token", "r") as f:
    bot_token = f.readline().strip()
    f.close()


class SerialReader(object):
    def __init__(self, port, baudrate, args=None):
        self.serial = serial.Serial(port=port, baudrate=baudrate)

    def read_line(self):
        return self.serial.readline().strip()

    def write_line(self, data):
        return self.serial.write(data.encode('ascii'))


class MainReader(SerialReader):
    KEY_CARD_UID = "Card UID"

    def __init__(self, *args, **kwargs):
        super(MainReader, self).__init__(*args, **kwargs)
        self.attempt = 0
        self.args = kwargs.get('args', None)

    def pc_action(self, command=LOCK):
        if self.args and args.notify:
            command_txt = "LOCK" if command == LOCK else "UNLOCK"
            self.send_msg("%s action performed" % command_txt)
        os.system('gnome-screensaver-command -%s' % command)

    def send_msg(self, text):
        URL = "https://api.telegram.org/bot%s/sendMessage" % bot_token
        t0 = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        req_body = {
            "chat_id": self.args.chat_id,  # ws-events chat
            "text": "%s: %s" % (t0, text)
        }
        response = requests.post(URL, json=req_body)
        print(response.json())

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
    rfid = MainReader(port=args.dp, baudrate=args.sbaud, args=args)
    inputs = [s.strip() for s in args.i.split(',')]

    while True:
        try:
            line = rfid.read_line()
            if line:
                print("LINE:%s" % line)

                # rfid
                if 'r' in inputs and rfid.KEY_CARD_UID in line:
                    rfid_uid_valid = rfid.uid_validate(line)
                    if rfid_uid_valid:
                        rfid.pc_action(command=UNLOCK)
                    else:
                        rfid.pc_action(command=LOCK)
                        sleep(10)

                # keypad
                if 'k' in inputs and line == "*":
                    print("Please enter pin code:")
                    pin_code_valid = rfid.pin_code_validate()
                    if pin_code_valid:
                        rfid.pc_action(command=UNLOCK)
                        continue

                if 'b' not in inputs: continue
                # bluetooth
                if line == "u":
                    rfid.pc_action(command=UNLOCK)
                elif line == "l":
                    rfid.pc_action(command=LOCK)
        except Exception as exc:
            msg = "Exception occurred: {}".format(exc)
            print(msg)
            if args.notify:
                rfid.send_msg(msg)
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", help="String of inputs: [r - rfid, k - keypad, b - bluetooth]", default="r,k,b")
    parser.add_argument("--dp", default="/dev/ttyACM0", help="Device that Arduino is connected with this PC")
    parser.add_argument("--sbaud", default=9600, help="Serial number that Arduino listens to RFID")
    parser.add_argument("--chat_id", help="Telegram chat id", default=None, type=str)
    parser.add_argument("--notify", default=True, help="Boolean if to send Telegram notification on events", choices=[True, False])
    args = parser.parse_args()
    main(args)
