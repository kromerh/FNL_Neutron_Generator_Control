// ***********************************
// *** Extraction Voltage
// ***********************************
int pwmPin = 9; // output pin supporting PWM
int LEDpin = 2;  // Pin where the red LED is connected that indicates if extraction USoll signal is on
int switchPin = 7; // Pin where the switch is connected to
int switchSignal = 0; //Signal of the switch (5V or off)

float volt = 1.9; // variable to hold the voltage read
float val = 0; 

// ***********************************
// *** Time
// ***********************************
unsigned long previousMillis = 0; // previous time readBS_WS_DF was executed
const long interval = 1000;           // interval at which to execute readBS_WS_DF (milliseconds)

// ***********************************
// *** HV reading from RPi
// ***********************************
int incomingByte = 0;   // for incoming serial data


const int numReadings = 30;

int readings1[numReadings];      // the readings from the analog input
int readings2[numReadings];      // the readings from the analog input
int readIndex = 0;              // the index of the current reading
int total1 = 0;                  // the running total
int total2 = 0;                  // the running total
int average1 = 0;                // the average
int average2 = 0;                // the average
float V1 = 0;                // the average
float V2 = 0;                // the average

int inputPin1 = A0;
int inputPin2 = A1;

void setup() {
	pinMode(LEDpin, OUTPUT);
	pinMode(switchPin, INPUT);
  // initialize serial communication with computer:
  Serial.begin(9600);
  // initialize all the readings to 0:
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readings1[thisReading] = 0;
    readings2[thisReading] = 0;
  }
}

void readPressure() {
  // subtract the last reading:
  total1 = total1 - readings1[readIndex];
  total2 = total2 - readings2[readIndex];
  // read from the sensor:
  readings1[readIndex] = analogRead(inputPin1);
  readings2[readIndex] = analogRead(inputPin2);
  // add the reading to the total:
  total1 = total1 + readings1[readIndex];
  total2 = total2 + readings2[readIndex];
  // advance to the next position in the array:
  readIndex = readIndex + 1;

  // if we're at the end of the array...
  if (readIndex >= numReadings) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  // calculate the average:
  average1 = total1 / numReadings;
  average2 = total2 / numReadings;
  delay(5);        // delay in between reads for stability
}

void loop() {
  // *** Extraction Voltage
  switchSignal = digitalRead(switchPin);
  digitalWrite(LEDpin, switchSignal);
  if (switchSignal == 1) {
     val = 255 * (volt / 5);
     analogWrite(pwmPin, val);
  }
  else
  {
    analogWrite(pwmPin, 0);
  }
  // ***
  readPressure();
  unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
      // save the last time executed
      V1 = average1 * 5.0 / 1023.0 * 2.0 * 1.020408163265306;
      V2 = average2 * 5.0 / 1023.0 * 2.0 * 1.020408163265306;
      //Serial.println(currentMillis - previousMillis);
      Serial.print(V1);  // Voltage A0 -- pressure
      Serial.print(" ");
      Serial.print(V2);   // Voltage A1 -- pressure
      Serial.print(" ");
      Serial.println(switchSignal); 
      previousMillis = currentMillis;
      
      // receive data:
        if (Serial.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial.read();
                switch ((char)incomingByte) {
                 case '0':
                  	Serial.print("0");
                  break;
                  
                 case '1':
                  	Serial.print("1");
                  break;

                 default:
                  break;
                }                
        }
    }  
}
