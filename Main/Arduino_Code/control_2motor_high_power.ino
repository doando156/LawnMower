#include <SoftwareSerial.h>


const int btRx = 2;  
const int btTx = 3;  
SoftwareSerial bluetooth(btRx, btTx);

// Motor 1 control pins
const int M1_RPWM = 5;
const int M1_LPWM = 6;
const int M1_REN  = 7;
const int M1_LEN  = 8;

// Motor 2 control pins
const int M2_RPWM = 10;
const int M2_LPWM = 11;
const int M2_REN  = 12;
const int M2_LEN  = 13;

// Logic power supply pins
const int logicPower1 = A0;
const int logicPower2 = A1;

void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600);

  // Set motor control pins as output
  pinMode(M1_RPWM, OUTPUT);
  pinMode(M1_LPWM, OUTPUT);
  pinMode(M1_REN, OUTPUT);
  pinMode(M1_LEN, OUTPUT);

  pinMode(M2_RPWM, OUTPUT);
  pinMode(M2_LPWM, OUTPUT);
  pinMode(M2_REN, OUTPUT);
  pinMode(M2_LEN, OUTPUT);

  // Enable motor drivers
  digitalWrite(M1_REN, HIGH);
  digitalWrite(M1_LEN, HIGH);
  digitalWrite(M2_REN, HIGH);
  digitalWrite(M2_LEN, HIGH);

  // Enable logic supply from A0 and A1
  pinMode(logicPower1, OUTPUT);
  digitalWrite(logicPower1, HIGH);  // Provide 5V logic from A0

  pinMode(logicPower2, OUTPUT);
  digitalWrite(logicPower2, HIGH);  // Provide 5V logic from A1

}

void loop() {
  if (bluetooth.available()) {
    String input = bluetooth.readStringUntil('\n'); // read until newline
    input.trim();  // remove any whitespace

    Serial.print("Received: ");
    Serial.println(input);

    if (input.length() == 0) return;

    char command = input.charAt(0);      // First char is direction command
    int speed = input.substring(1).toInt(); // Rest is speed value

    // Clamp speed between 0 and 255
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;

    // Define slower speed for smoother turning
    int turnSpeed = speed / 2;

    switch (command) {
      case 'F': // Forward
        moveMotor1(speed, true);
        moveMotor2(speed, true);
        break;

      case 'B': // Backward
        moveMotor1(speed, false);
        moveMotor2(speed, false);
        break;

      case 'L': // Turn Left (left motor slower backward, right motor faster forward)
        moveMotor1(turnSpeed, false);  // slower
        moveMotor2(speed, true);       // faster
        break;

      case 'R': // Turn Right (left motor faster forward, right motor slower backward)
        moveMotor1(speed, true);       // faster
        moveMotor2(turnSpeed, false);  // slower
        break;

      case 'T': // Rotate in place (both motors forward at same speed)
        moveMotor1(speed, true);
        moveMotor2(speed, false);
        break;

      case 'S': // Stop
        stopMotors();
        break;

      default:
        Serial.println("Unknown command");
        break;
    }
  }
}

void moveMotor1(int speed, bool forward) {
  if (forward) {
    analogWrite(M1_RPWM, speed);
    analogWrite(M1_LPWM, 0);
  } else {
    analogWrite(M1_RPWM, 0);
    analogWrite(M1_LPWM, speed);
  }
}

void moveMotor2(int speed, bool forward) {
  if (forward) {
    analogWrite(M2_RPWM, speed);
    analogWrite(M2_LPWM, 0);
  } else {
    analogWrite(M2_RPWM, 0);
    analogWrite(M2_LPWM, speed);
  }
}

void stopMotors() {
  analogWrite(M1_RPWM, 0);
  analogWrite(M1_LPWM, 0);
  analogWrite(M2_RPWM, 0);
  analogWrite(M2_LPWM, 0);
}
