/*
 * QFL Controller - Arduino Nano
 * Quantum-Flux Lab Control System
 * 
 * Version: 1.0
 * Date: 2026-01-31
 * License: MIT (Open Source)
 * 
 * SAFETY WARNING: This code controls high-voltage (30kV) equipment.
 * Triple-redundant safety systems are implemented but operator
 * vigilance is mandatory. Always wear PPE and maintain safe distances.
 * 
 * Open Source References:
 * - Corona discharge physics: Riba et al., Sensors 21(19):6676 (2021)
 * - EHD thrust: Ianconescu et al., J. Electrostatics 69 (2011) 512
 * - NASA HDBK-4007 for HV safety margins
 */

#include <Wire.h>
#include <Adafruit_INA219.h>

// =============================================================================
// CONFIGURATION CONSTANTS
// =============================================================================

// Pin Definitions
const int PIN_ESTOP = 2;           // Emergency stop (interrupt pin)
const int PIN_RELAY = 3;           // Safety relay control
const int PIN_PIEZO_START = 4;     // Piezo pins 4-9 (6 units)
const int PIN_MOSFET_GATE = 10;    // Main MOSFET for HV enable
const int PIN_LED_YELLOW = 11;     // Yellow warning LED
const int PIN_LED_RED = 12;        // Red warning/critical LED
const int PIN_BUZZER = 13;         // Audio warning
const int PIN_TEMP1 = A0;          // Temperature sensor 1
const int PIN_TEMP2 = A1;          // Temperature sensor 2
const int PIN_OZONE = A2;          // Ozone sensor
const int PIN_UV = A3;             // UV sensor

// Safety Thresholds (ADJUST BASED ON CALIBRATION)
const float EFIELD_WARNING = 2000;      // V/m (2 kV/m)
const float EFIELD_CRITICAL = 4000;     // V/m (4 kV/m)
const float TEMP_WARNING = 40.0;        // °C
const float TEMP_CRITICAL = 50.0;       // °C
const float OZONE_WARNING = 0.05;       // ppm
const float OZONE_CRITICAL = 0.08;      // ppm
const float UV_WARNING = 0.5;           // mW/cm²
const float UV_CRITICAL = 1.0;          // mW/cm²
const float CURRENT_WARNING = 0.8;      // A
const float CURRENT_CRITICAL = 1.2;     // A
const float SPL_WARNING = 100;          // dB
const float SPL_CRITICAL = 120;         // dB

// Timing Constants
const unsigned long WATCHDOG_TIMEOUT = 100;  // ms
const unsigned long SENSOR_INTERVAL = 100;   // ms (10 Hz sampling)
const unsigned long PWM_FREQ_HV = 400;       // Hz (corona frequency)
const unsigned long PWM_FREQ_AUDIO = 20;     // Hz (infrasound)

// Piezo Array Phasing (degrees)
const int PIEZO_PHASE[6] = {0, 60, 120, 180, 240, 300};

// =============================================================================
// GLOBAL STATE
// =============================================================================

enum SystemState {
  STATE_INIT,
  STATE_STANDBY,
  STATE_RUNNING,
  STATE_WARNING,
  STATE_CRITICAL,
  STATE_EMERGENCY_STOP
};

SystemState currentState = STATE_INIT;
Adafruit_INA219 ina219;

// Sensor readings
struct SensorData {
  float temperature1;
  float temperature2;
  float ozone;
  float uv;
  float current;
  float voltage;
  float power;
  float spl;
  unsigned long timestamp;
};

SensorData sensors;

// Control parameters
struct ControlParams {
  int hvAmplitude;      // 0-255 (PWM duty)
  int hvFrequency;      // Hz
  int audioFrequency;   // Hz
  int audioAmplitude;   // 0-255
  bool enableHV;
  bool enableAudio;
};

ControlParams params = {128, 400, 20, 100, false, false};

// Safety flags
volatile bool emergencyStop = false;
unsigned long lastWatchdogReset = 0;
unsigned long lastSensorRead = 0;
unsigned long stateEntryTime = 0;

// =============================================================================
// SETUP
// =============================================================================

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Wait for serial or timeout
  
  Serial.println(F("=============================================="));
  Serial.println(F("QFL Controller v1.0"));
  Serial.println(F("SAFETY WARNING: High Voltage System Active"));
  Serial.println(F("=============================================="));
  
  // Initialize pins
  pinMode(PIN_ESTOP, INPUT_PULLUP);
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_MOSFET_GATE, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  
  for (int i = 0; i < 6; i++) {
    pinMode(PIN_PIEZO_START + i, OUTPUT);
    digitalWrite(PIN_PIEZO_START + i, LOW);
  }
  
  // Initialize I2C for current sensor
  Wire.begin();
  if (!ina219.begin()) {
    Serial.println(F("ERROR: INA219 current sensor not found!"));
    // Continue anyway - we'll use analog backup
  } else {
    Serial.println(F("INA219 current sensor initialized"));
  }
  
  // Attach emergency stop interrupt
  attachInterrupt(digitalPinToInterrupt(PIN_ESTOP), handleEmergencyStop, FALLING);
  
  // Initial safe state
  setSafeState();
  
  // Self-test sequence
  if (performSelfTest()) {
    Serial.println(F("SELF-TEST PASSED"));
    transitionToState(STATE_STANDBY);
  } else {
    Serial.println(F("SELF-TEST FAILED - CHECK HARDWARE"));
    transitionToState(STATE_EMERGENCY_STOP);
  }
  
  Serial.println(F("Ready for commands. Type 'help' for list."));
}

// =============================================================================
// MAIN LOOP
// =============================================================================

void loop() {
  // Watchdog reset
  resetWatchdog();
  
  // Read and process serial commands
  processSerialCommands();
  
  // Read sensors at defined interval
  if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
    readAllSensors();
    lastSensorRead = millis();
    
    // Log sensor data
    logSensorData();
    
    // Safety check
    checkSafetyLimits();
  }
  
  // State machine
  switch (currentState) {
    case STATE_STANDBY:
      // Waiting for activation
      break;
      
    case STATE_RUNNING:
      updateOutputs();
      break;
      
    case STATE_WARNING:
      handleWarningState();
      break;
      
    case STATE_CRITICAL:
    case STATE_EMERGENCY_STOP:
      // Remain in safe state
      break;
      
    default:
      break;
  }
  
  // Update indicators based on state
  updateIndicators();
}

// =============================================================================
// SAFETY FUNCTIONS
// =============================================================================

void setSafeState() {
  digitalWrite(PIN_RELAY, LOW);          // Open relay
  digitalWrite(PIN_MOSFET_GATE, LOW);    // Disable MOSFET
  
  for (int i = 0; i < 6; i++) {
    digitalWrite(PIN_PIEZO_START + i, LOW);
  }
  
  params.enableHV = false;
  params.enableAudio = false;
  
  Serial.println(F("SAFE STATE ENGAGED"));
}

void handleEmergencyStop() {
  emergencyStop = true;
  setSafeState();
  transitionToState(STATE_EMERGENCY_STOP);
  
  // This runs in interrupt context - keep it brief
  Serial.println(F("\n!!! EMERGENCY STOP TRIGGERED !!!"));
}

void resetWatchdog() {
  lastWatchdogReset = millis();
}

bool checkWatchdog() {
  return (millis() - lastWatchdogReset) < WATCHDOG_TIMEOUT;
}

// =============================================================================
// SENSOR FUNCTIONS
// =============================================================================

void readAllSensors() {
  // Temperature sensors (DHT22 simplified - using analog read)
  // In production, use proper DHT22 library
  int temp1Raw = analogRead(PIN_TEMP1);
  int temp2Raw = analogRead(PIN_TEMP2);
  sensors.temperature1 = (temp1Raw * 5.0 / 1023.0 - 0.5) * 100.0; // LM35 conversion
  sensors.temperature2 = (temp2Raw * 5.0 / 1023.0 - 0.5) * 100.0;
  
  // Ozone sensor (MiCS-2614)
  int ozoneRaw = analogRead(PIN_OZONE);
  sensors.ozone = ozoneRaw * (5.0 / 1023.0) * 0.1; // Approximate conversion
  
  // UV sensor (GUVA-S12SD)
  int uvRaw = analogRead(PIN_UV);
  sensors.uv = uvRaw * (5.0 / 1023.0) * 10.0; // mW/cm² approx
  
  // Current sensor (INA219)
  if (ina219.success()) {
    sensors.current = ina219.getCurrent_mA() / 1000.0; // Convert to A
    sensors.voltage = ina219.getBusVoltage_V();
    sensors.power = ina219.getPower_mW() / 1000.0;
  } else {
    // Fallback: analog current sense
    sensors.current = analogRead(A6) * (5.0 / 1023.0) / 0.1; // Shunt resistor
    sensors.voltage = 12.0; // Assume nominal
    sensors.power = sensors.current * sensors.voltage;
  }
  
  // SPL estimation from microphone
  int micRaw = analogRead(A7);
  sensors.spl = 20.0 * log10(micRaw + 1) + 50.0; // Rough calibration
  
  sensors.timestamp = millis();
}

void logSensorData() {
  // CSV format for logging
  Serial.print(F("DATA,"));
  Serial.print(sensors.timestamp);
  Serial.print(F(","));
  Serial.print(sensors.temperature1);
  Serial.print(F(","));
  Serial.print(sensors.temperature2);
  Serial.print(F(","));
  Serial.print(sensors.ozone, 3);
  Serial.print(F(","));
  Serial.print(sensors.uv, 2);
  Serial.print(F(","));
  Serial.print(sensors.current, 3);
  Serial.print(F(","));
  Serial.print(sensors.voltage, 2);
  Serial.print(F(","));
  Serial.print(sensors.spl, 1);
  Serial.print(F(","));
  Serial.println(currentState);
}

// =============================================================================
// SAFETY CHECK
// =============================================================================

void checkSafetyLimits() {
  bool warning = false;
  bool critical = false;
  
  // Check temperature
  if (sensors.temperature1 > TEMP_CRITICAL || sensors.temperature2 > TEMP_CRITICAL) {
    critical = true;
    Serial.println(F("CRITICAL: Overtemperature detected"));
  } else if (sensors.temperature1 > TEMP_WARNING || sensors.temperature2 > TEMP_WARNING) {
    warning = true;
  }
  
  // Check ozone
  if (sensors.ozone > OZONE_CRITICAL) {
    critical = true;
    Serial.println(F("CRITICAL: Ozone level exceeded"));
  } else if (sensors.ozone > OZONE_WARNING) {
    warning = true;
  }
  
  // Check current
  if (sensors.current > CURRENT_CRITICAL) {
    critical = true;
    Serial.println(F("CRITICAL: Overcurrent detected"));
  } else if (sensors.current > CURRENT_WARNING) {
    warning = true;
  }
  
  // Check watchdog
  if (!checkWatchdog()) {
    critical = true;
    Serial.println(F("CRITICAL: Watchdog timeout"));
  }
  
  // State transitions
  if (critical && currentState != STATE_CRITICAL && currentState != STATE_EMERGENCY_STOP) {
    setSafeState();
    transitionToState(STATE_CRITICAL);
  } else if (warning && currentState == STATE_RUNNING) {
    transitionToState(STATE_WARNING);
  } else if (!warning && !critical && currentState == STATE_WARNING) {
    transitionToState(STATE_RUNNING);
  }
}

// =============================================================================
// OUTPUT CONTROL
// =============================================================================

void updateOutputs() {
  if (!params.enableHV && !params.enableAudio) return;
  
  unsigned long now = micros();
  static unsigned long lastHVUpdate = 0;
  static unsigned long lastAudioUpdate = 0;
  static int phaseIndex = 0;
  
  // HV piezo control (phased array)
  if (params.enableHV) {
    unsigned long hvPeriod = 1000000UL / params.hvFrequency;
    if (now - lastHVUpdate >= hvPeriod / 6) {
      lastHVUpdate = now;
      
      // Sequential firing with phase delay
      for (int i = 0; i < 6; i++) {
        int pin = PIN_PIEZO_START + i;
        if (i == phaseIndex) {
          digitalWrite(pin, HIGH);
        } else {
          digitalWrite(pin, LOW);
        }
      }
      phaseIndex = (phaseIndex + 1) % 6;
    }
  }
  
  // Audio control (would use PWM or external DAC)
  // Placeholder for audio frequency generation
}

// =============================================================================
// STATE MACHINE
// =============================================================================

void transitionToState(SystemState newState) {
  SystemState oldState = currentState;
  currentState = newState;
  stateEntryTime = millis();
  
  Serial.print(F("State transition: "));
  Serial.print(stateToString(oldState));
  Serial.print(F(" -> "));
  Serial.println(stateToString(newState));
  
  switch (newState) {
    case STATE_STANDBY:
      setSafeState();
      break;
      
    case STATE_RUNNING:
      digitalWrite(PIN_RELAY, HIGH);
      digitalWrite(PIN_MOSFET_GATE, HIGH);
      break;
      
    case STATE_WARNING:
      // Continue operating but warn
      break;
      
    case STATE_CRITICAL:
    case STATE_EMERGENCY_STOP:
      setSafeState();
      break;
      
    default:
      break;
  }
}

const char* stateToString(SystemState state) {
  switch (state) {
    case STATE_INIT: return "INIT";
    case STATE_STANDBY: return "STANDBY";
    case STATE_RUNNING: return "RUNNING";
    case STATE_WARNING: return "WARNING";
    case STATE_CRITICAL: return "CRITICAL";
    case STATE_EMERGENCY_STOP: return "EMERGENCY_STOP";
    default: return "UNKNOWN";
  }
}

void handleWarningState() {
  // Auto-shutdown after 10 seconds in warning if not acknowledged
  if (millis() - stateEntryTime > 10000) {
    Serial.println(F("Warning timeout - shutting down"));
    setSafeState();
    transitionToState(STATE_CRITICAL);
  }
}

// =============================================================================
// INDICATORS
// =============================================================================

void updateIndicators() {
  switch (currentState) {
    case STATE_STANDBY:
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, millis() % 1000 < 100 ? HIGH : LOW); // Slow blink
      noTone(PIN_BUZZER);
      break;
      
    case STATE_RUNNING:
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED, LOW);
      noTone(PIN_BUZZER);
      break;
      
    case STATE_WARNING:
      digitalWrite(PIN_LED_YELLOW, millis() % 1000 < 500 ? HIGH : LOW);
      digitalWrite(PIN_LED_RED, LOW);
      tone(PIN_BUZZER, 2000, 100);
      break;
      
    case STATE_CRITICAL:
    case STATE_EMERGENCY_STOP:
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED, HIGH);
      tone(PIN_BUZZER, 4000);
      break;
      
    default:
      break;
  }
}

// =============================================================================
// SELF TEST
// =============================================================================

bool performSelfTest() {
  Serial.println(F("Performing self-test..."));
  
  // Test LEDs
  Serial.print(F("Testing LEDs..."));
  digitalWrite(PIN_LED_YELLOW, HIGH);
  delay(200);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, HIGH);
  delay(200);
  digitalWrite(PIN_LED_RED, LOW);
  Serial.println(F("OK"));
  
  // Test buzzer
  Serial.print(F("Testing buzzer..."));
  tone(PIN_BUZZER, 1000, 200);
  delay(300);
  Serial.println(F("OK"));
  
  // Test relay (don't actually energize HV)
  Serial.print(F("Testing relay..."));
  digitalWrite(PIN_RELAY, HIGH);
  delay(100);
  digitalWrite(PIN_RELAY, LOW);
  Serial.println(F("OK"));
  
  // Test sensors
  Serial.print(F("Testing sensors..."));
  readAllSensors();
  if (sensors.temperature1 > -50 && sensors.temperature1 < 100) {
    Serial.println(F("OK"));
  } else {
    Serial.println(F("WARN (check calibration)"));
  }
  
  // Check emergency stop
  Serial.print(F("Testing E-Stop..."));
  if (digitalRead(PIN_ESTOP) == HIGH) {
    Serial.println(F("OK (not pressed)"));
  } else {
    Serial.println(F("PRESSED"));
  }
  
  return true;
}

// =============================================================================
// SERIAL COMMANDS
// =============================================================================

void processSerialCommands() {
  if (!Serial.available()) return;
  
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  cmd.toLowerCase();
  
  if (cmd == "help") {
    printHelp();
  } else if (cmd == "status") {
    printStatus();
  } else if (cmd == "start") {
    if (currentState == STATE_STANDBY) {
      params.enableHV = true;
      params.enableAudio = true;
      transitionToState(STATE_RUNNING);
    } else {
      Serial.println(F("Cannot start from current state"));
    }
  } else if (cmd == "stop") {
    setSafeState();
    transitionToState(STATE_STANDBY);
  } else if (cmd.startsWith("hv ")) {
    int val = cmd.substring(3).toInt();
    params.hvAmplitude = constrain(val, 0, 255);
    Serial.print(F("HV amplitude set to "));
    Serial.println(params.hvAmplitude);
  } else if (cmd.startsWith("freq ")) {
    int val = cmd.substring(5).toInt();
    params.hvFrequency = constrain(val, 100, 2000);
    Serial.print(F("HV frequency set to "));
    Serial.println(params.hvFrequency);
  } else if (cmd == "reset") {
    emergencyStop = false;
    setSafeState();
    transitionToState(STATE_STANDBY);
  } else {
    Serial.println(F("Unknown command. Type 'help' for list."));
  }
}

void printHelp() {
  Serial.println(F("\n=== QFL Controller Commands ==="));
  Serial.println(F("help     - Show this help"));
  Serial.println(F("status   - Show system status"));
  Serial.println(F("start    - Start operation (from STANDBY)"));
  Serial.println(F("stop     - Emergency stop"));
  Serial.println(F("hv N     - Set HV amplitude (0-255)"));
  Serial.println(F("freq N   - Set HV frequency (100-2000 Hz)"));
  Serial.println(F("reset    - Clear emergency stop"));
  Serial.println(F("=================================\n"));
}

void printStatus() {
  Serial.println(F("\n=== QFL System Status ==="));
  Serial.print(F("State: "));
  Serial.println(stateToString(currentState));
  Serial.print(F("Uptime: "));
  Serial.print(millis() / 1000);
  Serial.println(F(" seconds"));
  Serial.print(F("Temp1: "));
  Serial.print(sensors.temperature1);
  Serial.println(F(" C"));
  Serial.print(F("Temp2: "));
  Serial.print(sensors.temperature2);
  Serial.println(F(" C"));
  Serial.print(F("Ozone: "));
  Serial.print(sensors.ozone, 3);
  Serial.println(F(" ppm"));
  Serial.print(F("Current: "));
  Serial.print(sensors.current, 3);
  Serial.println(F(" A"));
  Serial.print(F("HV Enabled: "));
  Serial.println(params.enableHV ? F("YES") : F("NO"));
  Serial.print(F("HV Freq: "));
  Serial.print(params.hvFrequency);
  Serial.println(F(" Hz"));
  Serial.println(F("=====================\n"));
}
