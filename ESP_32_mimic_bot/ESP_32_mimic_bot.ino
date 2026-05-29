#include <ESP32Servo.h>

Servo thumbServo;
Servo indexServo;
Servo middleServo;
Servo ringServo;
Servo littleServo;
Servo wristServo;

String data = "";

void setup() {
  Serial.begin(115200);

  thumbServo.attach(12);
  indexServo.attach(14);
  middleServo.attach(25);
  ringServo.attach(26);
  littleServo.attach(27);
  wristServo.attach(33);

  Serial.println("ESP32 Ready");
}

void loop() {

  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      processData(data);
      data = "";
    } else {
      data += c;
    }
  }
}

// -------- FUNCTION TO PROCESS DATA --------
void processData(String cmd) {

  int T = 0, I = 0, M = 0, R = 0, L = 0, W = 90;

  int parsed = sscanf(cmd.c_str(), "T:%d,I:%d,M:%d,R:%d,L:%d,W:%d",
         &T, &I, &M, &R, &L, &W);

  if (parsed == 6) {
    thumbServo.write(T);
    indexServo.write(I);
    middleServo.write(M);
    ringServo.write(R);
    littleServo.write(L);
    wristServo.write(W);
  }

  Serial.println(cmd);  // Debug
}