// Simple servo jaw control via serial
// Upload this to your Arduino
// Servo connected to pin 9
// 20 degrees = closed, 70 degrees = open

#include <Servo.h>

Servo jawServo;
const int SERVO_PIN = 9;  // Change to your servo pin

void setup() {
  Serial.begin(9600);
  jawServo.attach(SERVO_PIN);
  jawServo.write(20);  // Start closed (20 = closed, 70 = open)
}

void loop() {
  if (Serial.available() > 0) {
    int angle = Serial.parseInt();

    // Safety bounds
    if (angle >= 0 && angle <= 180) {
      jawServo.write(angle);
    }

    // Clear buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}
