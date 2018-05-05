#include <SoftwareSerial.h>

#define BT_RX         2
#define BT_TX         3
#define SERIAL_HOST   9600
#define SERIAL_SOFT   38400
#define DELAY_TIMEOUT 1000

SoftwareSerial BTserial(BT_RX, BT_TX);

char incomingByte = 0;

void setup() {
  Serial.begin(9600);
  Serial.println("Arduino with HC-06 is ready");

  BTserial.begin(38400);
  Serial.println("BTserial started at 38400");

  Serial.print("AT");
  Serial.print("\r\n");
  delay(DELAY_TIMEOUT);

  Serial.print("AT+NAME");
  Serial.print("gr00t");
  Serial.print("\r\n");
  delay(DELAY_TIMEOUT);

  Serial.print("AT+BAUD");
  Serial.print("9600");
  Serial.print("\r\n");
  delay(DELAY_TIMEOUT);

  Serial.print("AT+PIN");
  Serial.print("0007");
  Serial.print("\r\n");
  delay(DELAY_TIMEOUT);
}

void loop() {
  if(Serial.available() > 0) {
    incomingByte = Serial.read();

    if(incomingByte == '0') {
       BTserial.println("l");
    } else if(incomingByte == '1') {
       BTserial.println("u");
    }

  }
}

