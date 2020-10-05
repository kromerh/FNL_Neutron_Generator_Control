// ***********************************
// *** Dose reading, HV reading
// ***********************************
int inputPinAnalog1 = A0; // Dose 1
int inputPinAnalog2 = A1; // Dose 2
int inputPinAnalog3 = A2; // HV I
int inputPinAnalog4 = A3; // HV V

const int numReadings1 = 30;
const int numReadings2 = 30;
const int numReadings3 = 30;
const int numReadings4 = 30;

int readings1[numReadings1];      // the readings from the analog input
int readings2[numReadings2];      // the readings from the analog input
int readings3[numReadings3];      // the readings from the analog input
int readings4[numReadings4];      // the readings from the analog input
int readIndex = 0;              // the index of the current reading
int total1 = 0;                  // the running total
int total2 = 0;                  // the running total
int total3 = 0;                  // the running total
int total4 = 0;                  // the running total
float average1 = 0;                // the average
float average2 = 0;                // the average
float average3 = 0;                // the average
float average4 = 0;                // the average
float V1 = 0.0;  // dose
float V2 = 0.0;  // dose
float V3 = 0.0;  // HV I
float V4 = 0.0;  // HV V


// ***********************************
// *** Time
// ***********************************
unsigned long previousMillis = 0; // previous time readBS_WS_DF was executed
const long interval = 1000;           // interval at which to execute readBS_WS_DF (milliseconds)

// ***********************************
// ***********************************

void setup() {
  // initialize serial communication 
  Serial.begin(9600);
 

  // *** Dose reading A8 & A9
  // initialize all the readings to 0:
  for (int thisReading = 0; thisReading < numReadings1; thisReading++) {
    readings1[thisReading] = 0;
    readings2[thisReading] = 0;
    readings3[thisReading] = 0;
    readings4[thisReading] = 0;
  }
}

// ***********************************
// ***********************************

// reads the analog inputs 100 times and returns the average
void readAnalog(){
  // subtract the last reading:
  total1 = total1 - readings1[readIndex];
  total2 = total2 - readings2[readIndex];
  total3 = total3 - readings3[readIndex]; // HV Current 0 - 10 V || 0 - 150 -kV
  total4 = total4 - readings4[readIndex]; // HV Voltage 0 - 10 V || 0 - 2 mA
  // read from the sensor:
  readings1[readIndex] = analogRead(inputPinAnalog1);
  readings2[readIndex] = analogRead(inputPinAnalog2);
  readings3[readIndex] = analogRead(inputPinAnalog3); // HV Current 0 - 10 V || 0 - 150 -kV
  readings4[readIndex] = analogRead(inputPinAnalog4); // HV Voltage 0 - 10 V || 0 - 2 mA
  // add the reading to the total:
  total1 = total1 + readings1[readIndex];
  total2 = total2 + readings2[readIndex];
  total3 = total3 + readings3[readIndex]; // HV Current 0 - 10 V || 0 - 150 -kV
  total4 = total4 + readings4[readIndex]; // HV Voltage 0 - 10 V || 0 - 2 mA
  // advance to the next position in the array:
  readIndex = readIndex + 1;

  // if we're at the end of the array...
  if (readIndex >= numReadings1) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  // calculate the average:
  average1 = total1 / numReadings1;
  average2 = total2 / numReadings2;
  average3 = total3 / numReadings3;
  average4 = total4 / numReadings4;
  // send it to the computer as ASCII digits
  V1 = average1 * (5.0 / 1023.0) * 4.017065;
  V2 = average2 * (5.0 / 1023.0) * 4.061856;
  V3 = average3 * (5.0 / 1023.0) ;//* 0.443037975; // HV Current 0 - 10 V || 0 - 150 -kV
  V4 = average4 * (5.0 / 1023.0) ;//* 50.81218274; // HV Voltage 0 - 10 V || 0 - 2 mA
  //Serial.print(V1);
  //Serial.print(" ");
  //Serial.print(V2);  
  //Serial.print(" ");
  //Serial.println(abs(V2 - V1));  
  delay(5);        // delay in between reads for stability  
}

void loop() {
  readAnalog();
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    // save the last time executed
    //Serial.println(currentMillis - previousMillis);
    Serial.print(V1);  // Voltage A8
    Serial.print(" ");
    Serial.print(V2);   // Voltage A9
    Serial.print(" ");
    Serial.print(abs(V2 - V1));  // Voltage difference A8-A9
    Serial.print(" ");
    Serial.print(V3);  // HV Current 0-10V --> 0-2 mA
    Serial.print(" ");
    Serial.println(V4);  // HV Voltage 0-10V --> -(0-150) kV
    previousMillis = currentMillis;
    // print: V1  V2  V2-V1  v3 v4
    delay(50);
    Serial.flush();
  }
  //Serial.print("I do stuff");
  
}




