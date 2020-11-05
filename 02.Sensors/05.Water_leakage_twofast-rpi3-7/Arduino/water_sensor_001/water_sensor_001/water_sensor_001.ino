#define WATER_SENSOR1 2// sensor S1
#define WATER_SENSOR2 4// sensor S2
#define WATER_SENSOR3 7// sensor S3

void setup() {
  init_sensors();
}
void loop() {
  Serial.print(digitalRead(WATER_SENSOR1));
  Serial.print(", ");
  Serial.print(digitalRead(WATER_SENSOR2));
  Serial.print(", ");
  Serial.println(digitalRead(WATER_SENSOR3));
  delay(1000);
}

void init_sensors() {
    Serial.begin (9600);
    pinMode(WATER_SENSOR1, INPUT);
    pinMode(WATER_SENSOR2, INPUT);
    pinMode(WATER_SENSOR3, INPUT);
}
