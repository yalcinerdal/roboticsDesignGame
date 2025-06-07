#include <Servo.h>

Servo servoMotor;
const int roundNumber = 600;
const int dirPin = 2;
const int stepPin = 3;
const int servoPin = 6;
const int enablePin = 12;
const int MS1 = 8;
const int MS2 = 9;
const int MS3 = 10;

int microstepFactor = 8;
float stepsPerDegree = (200.0 * microstepFactor) / 360.0;


void setup() {
  Serial.begin(9600);    
  Serial.println("READY");
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(MS3, OUTPUT);

  setMicrostepping("QUARTER");  // "FULL", "HALF", "QUARTER", "EIGHTH", "SIXTEENTH"

  servoMotor.attach(6);
  servoMotor.write(90);
  digitalWrite(enablePin, LOW);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');

    if (command == "handShowsPalm") {
      rotatesHandToPalm();
      //slowMoveServo(90, 180, 15);   
      delay(100);
    } else if (command == "handShowsBack") {
      rotatesHandToBack();
      //slowMoveServo(90, 0, 15);   
      delay(100);
    /*} else if (command == "handHomePositionFromPalm"){
      slowMoveServo(180, 90, 15);   
      delay(100);
    } else if (command == "handHomePositionFromBack"){
      slowMoveServo(0, 90, 15);   
      delay(100);}*/
    } else if (command == "handShowsSide"){
      rotatesHandToSide();
    } else if (command == "armRotatesBack"){
      //Serial.println("arm back.");
      rotatesArmToBack();
    } else if (command == "armRotatesForward"){
      //Serial.println("arm forward.");
      rotatesArmToForward();
    }
    else if (command == "startPosition"){
      rotatesArmToForward();
      delay(10);
      handShowsPalm();
    }
    else if (command == "sleepPosition"){
      handShowsSide();
      delay(100);
      rotatesArmToBack();
    }
    /*else if (command == "slowsleepPosition"){
      slowMoveServo(90, 0, 15);   
      delay(100);
      rotatesArmToBack();
    }*/
  }
}

void rotatesHandToPalm(){
  servoMotor.write(0);
  delay(100);
}

void rotatesHandToSide(){
  servoMotor.write(90);
  delay(100);
}

void rotatesHandToBack(){
  servoMotor.write(180);
  delay(100);
}

void rotatesArmToForward(){
  rotatesArm(40,true);
  delay(100);
}

void rotatesArmToBack(){
  rotatesArm(40,false);
  delay(100);
}

void setMicrostepping(String mode) {
  if (mode == "FULL") {
    digitalWrite(MS1, LOW);
    digitalWrite(MS2, LOW);
    digitalWrite(MS3, LOW);
    microstepFactor = 1;
  }
  else if (mode == "HALF") {
    digitalWrite(MS1, HIGH);
    digitalWrite(MS2, LOW);
    digitalWrite(MS3, LOW);
    microstepFactor = 2;
  }
  else if (mode == "QUARTER") {
    digitalWrite(MS1, LOW);
    digitalWrite(MS2, HIGH);
    digitalWrite(MS3, LOW);
    microstepFactor = 4;
  }
  else if (mode == "EIGHTH") {
    digitalWrite(MS1, HIGH);
    digitalWrite(MS2, HIGH);
    digitalWrite(MS3, LOW);
    microstepFactor = 8;
  }
  else if (mode == "SIXTEENTH") {
    digitalWrite(MS1, HIGH);
    digitalWrite(MS2, HIGH);
    digitalWrite(MS3, HIGH);
    microstepFactor = 16;
  }

  stepsPerDegree = (200.0 * microstepFactor) / 360.0;
}

void rotatesArm(float degree, bool forward) {
  digitalWrite(dirPin, forward ? HIGH : LOW); 

  int steps = degree * stepsPerDegree;

  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(75000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(75000);
  }
}

void slowMoveServo(int fromAngle, int toAngle, int delayTime) {
  if (fromAngle < toAngle) {
    for (int pos = fromAngle; pos <= toAngle; pos++) {
      servoMotor.write(pos);
      delay(delayTime);
    }
  } else {
    for (int pos = fromAngle; pos >= toAngle; pos--) {
      servoMotor.write(pos);
      delay(delayTime);
    }
  }
}
