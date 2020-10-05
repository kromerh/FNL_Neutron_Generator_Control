// ***********************************
// *** Reading of the mass flow
// ***********************************
int inputPinAnalog1 = A0; // Mass flow reading PIN

const int numReadings1 = 30;

int readings1[numReadings1];      // the readings from the analog input

int readIndex = 0;              // the index of the current reading
int total1 = 0;                  // the running total
float average1 = 0;                // the average
float V1 = 0.0;  // mass flow

// ***********************************
// *** Setpoint of the mass flow
// ***********************************
int outputPinAnalog1 = 9; // Setpoint of the mass flow PIN
float V_out = 0;  // Setpoint of the mass flow as INTEGER from twofast-rpi3-4
float V_out_raw = 0;  // Setpoint of the mass flow as INTEGER from twofast-rpi3-4

// ***********************************
// *** Time
// ***********************************
unsigned long previousMillis = 0; // previous time
const long interval = 1000;           // interval at which to execute

// ***********************************
// ***********************************

void setup() {
  // initialize serial communication 
  Serial.begin(9600);
  pinMode(outputPinAnalog1, OUTPUT);  // sets the pin as output

  // initialize all the readings to 0:
  for (int thisReading = 0; thisReading < numReadings1; thisReading++) {
    readings1[thisReading] = 0;
  }
}

// ***********************************
// ***********************************

// reads the analog inputs numReadings1 times and returns the average
void readAnalog(){
  // subtract the last reading:
  total1 = total1 - readings1[readIndex];

  // read from the sensor:
  readings1[readIndex] = analogRead(inputPinAnalog1);

  // add the reading to the total:
  total1 = total1 + readings1[readIndex];

  // advance to the next position in the array:
  readIndex = readIndex + 1;

  // if we're at the end of the array...
  if (readIndex >= numReadings1) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  // calculate the average:
  average1 = total1 / numReadings1;

  // send it to the computer as ASCII digits
  V1 = average1 * (5.0 / 1023.0); // uncalibrated

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
  // ***********************************
  // *** Setpoint of the mass flow
  // ***********************************
  if (Serial.available() > 0){  // Looking for incoming data
    V_out_raw = Serial.parseFloat();
    V_out = (V_out_raw + 0.0) * 256/5;  // 256/5 = 51
    analogWrite(outputPinAnalog1, V_out);  // Setpoing mass flow meter
  }  
  // ***********************************
  // *** Reading of the mass flow
  // ***********************************
  if (currentMillis - previousMillis >= interval) {
    // save the last time executed
    //Serial.println(currentMillis - previousMillis);
    Serial.print("V_1 ");  // mass flow reading
    Serial.print(V1);
    Serial.print(", ");
    Serial.print(V_out_raw);
    Serial.print(", ");
    Serial.print("V_out ");  // mass flow setpoint x 256/5
    Serial.println(V_out);
    previousMillis = currentMillis;
    // print: V1 V_out
    delay(50);
  }
  //Serial.print("I do stuff");
  
}
