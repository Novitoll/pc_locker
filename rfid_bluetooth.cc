#include <SPI.h>
#include <MFRC522.h>
#include <SoftwareSerial.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above
#define BT_RX           2
#define BT_TX           3

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
SoftwareSerial BTserial(BT_RX, BT_TX);

void setup() {
  Serial.begin(9600);   // Initialize serial communications with the PC
  SPI.begin();      // Init SPI bus
  mfrc522.PCD_Init();   // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));

  BTserial.begin(38400);
}

void loop() {
  char inByte;

  // Look for new cards &&
  // Select one of the cards
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    // Dump debug info about the card; PICC_HaltA() is automatically called
    mfrc522.PICC_DumpToSerial(&(mfrc522.uid));
  }

  if (BTserial.available()) {       // only send data back if data has been sent
//    char inByte = BTserial.read();  // read the incoming data
//    Serial.println(inByte);         // send the data back in a new line so that it is not all one long line
    Serial.println("w00t");
    Serial.println("l");
  }
}