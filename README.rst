pc_locker
====

Arduino Uno R3 project with RFID, HC-06 bluetooth, matrix 4x4 keyboard auth to lock/unlock Linux PC

Pre-requisistes
------------

* Linux
* Arduino 1.8.5
* Python 2.7 - pyserial
* RFID input (unlock / lock)
* Keypad (unlock)
* Bluetooth HC-06 (unlock / lock)
* Device with HC-06 compatibility

Instructions
------------

1) include your ``$(whoami)`` user to ``dialout`` group in order to access to ``/dev/ttyAC*`` where Arduino is connected
2) execute Python script ``python lock_pc_gnome.py --dp=/dev/ttyACM1``

* RFID input
* MIFARE UID
* Keypad

# = cancel, \* = trigger, 1234567890abcd, 3 fail attempts -> block N-seconds

* Bluetooth HC-06
u = unlock, l  = lock, AT+NAME, AT+PIN

.. image:: device.jpg
