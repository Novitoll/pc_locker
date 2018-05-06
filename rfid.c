#include <SPI.h>
#include <MFRC522.h>

#include <Keypad.h>
#include <SoftwareSerial.h>

#define RST_PIN         9
#define SS_PIN          10
#define BT_RX           2
#define BT_TX           3
#define BLUETOOTH_DELAY 1000

MFRC522 mfrc522(SS_PIN, RST_PIN);       // Create MFRC522 instance
SoftwareSerial BTserial(BT_RX, BT_TX);  // Create a serial for BT communication

// prepare a matrix keyboard settings
const byte ROWS = 4;
const byte COLS = 4;
char key;

char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

byte rowPins[ROWS] = {15, 16, 17, 18};  // analogue
byte colPins[COLS] = {7, 6, 5, 4};

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

void setup() {
  Serial.begin(9600);                   // Init serial for RFID & Keypad
  SPI.begin();                          // Init SPI bus
  mfrc522.PCD_Init();                   // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();    // Show details of PCD - MFRC522 Card Reader details

  BTserial.begin(38400);
  BTserial.print("AT");
  delay(BLUETOOTH_DELAY);

  BTserial.print("AT+NAMEgR00t");
  delay(BLUETOOTH_DELAY);

  BTserial.print("AT+PIN0007");
  delay(BLUETOOTH_DELAY);
}

void loop() {
  // rfid input
  if (mfrc522.PICC_IsNewCardPresent()) {
    mfrc522.PICC_ReadCardSerial();
    mfrc522.PICC_DumpToSerial(&(mfrc522.uid));
  }

  // keypad input
  key = keypad.getKey();
  if (key){
    Serial.println(key);
  }

  // bluetooth
  if (BTserial.available()) {
    String btInput = BTserial.readString();
    Serial.println(btInput);
  }
}