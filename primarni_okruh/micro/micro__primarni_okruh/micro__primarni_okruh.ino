// Lucy primary v2
// Include the Wire library for I2C
#include <Wire.h>
/* 
E1 = R_PWM - purple
E2 = L_PWM - blue
IN1 = R_BACKWARD - gray
IN2 = R_FORWARD - white
IN3 = L_FORWARD - yellow
IN4 = L_BACKWARD - green
*/
// MOTOR DRIVER PINS
#define R_PWM 5
#define R_FORWARD 4
#define R_BACKWARD 7
#define L_PWM 6
#define L_FORWARD 8
#define L_BACKWARD 9

// DISTANCE SENSORS PINS
#define F_ULTRASONIC_TRIG_PIN 10
#define F_ULTRASONIC_ECHO_PIN 16
#define B_ULTRASONIC_TRIG_PIN 15
#define B_ULTRASONIC_ECHO_PIN 14
//#define ULTRASONICS_VCC_PIN 14


// COMMAND CODES
#define COMMAND_CONTINUE 0x00
#define COMMAND_STOP 0x01
#define COMMAND_RIDE_FORWARD 0x02
#define COMMAND_FORWARD_STEER_LEFT 0x03
#define COMMAND_FORWARD_STEER_RIGHT 0x04
#define COMMAND_RIDE_BACKWARD 0x05
#define COMMAND_BACKWARD_STEER_LEFT 0x06
#define COMMAND_BACKWARD_STEER_RIGHT 0x07
#define COMMAND_TURN_LEFT 0x08
#define COMMAND_TURN_RIGHT 0x09

#define COMMAND_SEND_STATE 0x11

#define COMMAND_SET_PWM_BYTE 0x21
#define COMMAND_SET_SPEED_LEVEL 0x22
#define COMMAND_SET_FREE_SPACE_MULTIPLIER 0x23

// STATE CODES
#define STOP 0x01
#define RIDE_FORWARD 0x02
#define FORWARD_STEER_LEFT 0x03
#define FORWARD_STEER_RIGHT 0x04
#define RIDE_BACKWARD 0x05
#define BACKWARD_STEER_LEFT 0x06
#define BACKWARD_STEER_RIGHT 0x07
#define TURN_LEFT 0x08
#define TURN_RIGHT 0x09
#define BARRIER_IN_FRONT_STOP 0x0A
#define BARRIER_IN_BACK_STOP 0x0B
#define NO_COMMUNICATION_STOP 0x0C

// STATUS CODES
#define OK 0x01
#define ERROR_BARRIER_IN_FRONT 0x02
#define ERROR_BARRIER_IN_BACK 0x03
#define ERROR_UKNOWN 0x11
#define ERROR_NO_VALUE 0x12

char last_command_status_code;
char last_command;
char doing_now;
int communication_timeout;

byte free_space_multiplier;
byte speed_level;
byte pwm_byte;


void setup() {
  pinMode(R_PWM, OUTPUT);
  pinMode(R_FORWARD, OUTPUT);
  pinMode(R_BACKWARD, OUTPUT);
  pinMode(L_PWM, OUTPUT);
  pinMode(L_FORWARD, OUTPUT);
  pinMode(L_BACKWARD, OUTPUT);
  reset_ride();

  pinMode(F_ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(F_ULTRASONIC_ECHO_PIN, INPUT);
  pinMode(B_ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(B_ULTRASONIC_ECHO_PIN, INPUT);
  //pinMode(ULTRASONICS_VCC_PIN, OUTPUT);
  //digitalWrite(ULTRASONICS_VCC_PIN, HIGH);

  // Join I2C bus as slave with address 8
  Wire.begin(0x8);
  
  // Call receiveEvent when data received                
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  
  Serial.begin(9600);

  doing_now = STOP;
  communication_timeout = 40;
  free_space_multiplier = 1;
  speed_level = 2;
  pwm_byte = 75;

  delay(100);
}

void loop() {
  if (communication_timeout <= 0) {
    reset_ride();
    doing_now = NO_COMMUNICATION_STOP;
    communication_timeout = 0;
    Serial.println("ERROR: No commands");
    Serial.println("SET doing_now: NO_COMMUNICATION_STOP");
  }
  else if (doing_now == RIDE_FORWARD || doing_now == FORWARD_STEER_LEFT || doing_now == FORWARD_STEER_RIGHT) {
    if (is_space_free('f', free_space_multiplier)) {
    }
    else {
      safe_stop_ride();
      doing_now = BARRIER_IN_FRONT_STOP;
      Serial.println("SET doing_now: BARRIER_IN_FRONT_STOP");
    }
  }
  else if (doing_now == RIDE_BACKWARD || doing_now == BACKWARD_STEER_LEFT || doing_now == BACKWARD_STEER_RIGHT) {
    if (is_space_free('b', free_space_multiplier)) {
    }
    else {
      safe_stop_ride();
      doing_now = BARRIER_IN_BACK_STOP;
      Serial.println("SET doing_now: BARRIER_IN_BACK_STOP");
    }
  }
  delay(50);
  communication_timeout-=1;
}


void ride_forward(byte pwm_byte) {
  reset_ride();
  digitalWrite(R_FORWARD, HIGH);
  digitalWrite(L_FORWARD, HIGH);
  analogWrite(R_PWM, pwm_byte);
  analogWrite(L_PWM, pwm_byte);
}

void ride_backward(byte pwm_byte) {
  reset_ride();
  digitalWrite(R_BACKWARD, HIGH);
  digitalWrite(L_BACKWARD, HIGH);
  analogWrite(R_PWM, pwm_byte);
  analogWrite(L_PWM, pwm_byte);
}

void steer_left(byte pwm_byte) {
  reset_ride();
  digitalWrite(R_FORWARD, HIGH);
  analogWrite(R_PWM, pwm_byte * 2); 
}

void steer_right(byte pwm_byte) {
  reset_ride();
  digitalWrite(L_FORWARD, HIGH);
  analogWrite(L_PWM, pwm_byte * 2);
}

void backward_steer_left(byte pwm_byte) {
  reset_ride();
  digitalWrite(R_BACKWARD, HIGH);
  analogWrite(R_PWM, pwm_byte *2); 
}

void backward_steer_right(byte pwm_byte) {
  reset_ride();
  digitalWrite(L_BACKWARD, HIGH);
  analogWrite(L_PWM, pwm_byte * 2);
}

void turn_left() {
  reset_ride();
  digitalWrite(L_BACKWARD, HIGH);
  digitalWrite(R_FORWARD, HIGH);
  analogWrite(L_PWM, 150);
  analogWrite(R_PWM, 150);
}

void turn_right() {
  reset_ride();
  digitalWrite(R_BACKWARD, HIGH);
  digitalWrite(L_FORWARD, HIGH);
  analogWrite(R_PWM, 150);
  analogWrite(L_PWM, 150);
}

void reset_ride() {
  digitalWrite(R_PWM, LOW);
  digitalWrite(R_FORWARD, LOW);
  digitalWrite(R_BACKWARD, LOW);
  digitalWrite(L_PWM, LOW);
  digitalWrite(L_FORWARD, LOW);
  digitalWrite(L_BACKWARD, LOW);
}

void safe_stop_ride() {
  reset_ride();
}


bool is_space_free(char sensor, int multiplier) {
  int distance;
  if (sensor == 'b') {
    distance = get_back_distance();
    Serial.print("Back distance: ");
  }
  else {
    distance = get_front_distance();
    Serial.print("Front distance: ");
  }
  Serial.println(distance);
  if (distance > 5 * multiplier || distance == 0)
    return true;
  else
    return false;
}

int get_front_distance() {
  long duration;
  digitalWrite(F_ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);
  // Sets the F_ULTRASONIC_TRIG_PIN on HIGH state for 10 micro seconds
  digitalWrite(F_ULTRASONIC_TRIG_PIN, HIGH);
  
  delayMicroseconds(10);
  digitalWrite(F_ULTRASONIC_TRIG_PIN, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(F_ULTRASONIC_ECHO_PIN, HIGH, 50000);
  // Calculating the distance
  return duration*0.034/2;
}

int get_back_distance() {
 long duration;
 digitalWrite(B_ULTRASONIC_TRIG_PIN, LOW);
 delayMicroseconds(2);
 // Sets the F_ULTRASONIC_TRIG_PIN on HIGH state for 10 micro seconds
 digitalWrite(B_ULTRASONIC_TRIG_PIN, HIGH);
 
 delayMicroseconds(10);
 digitalWrite(B_ULTRASONIC_TRIG_PIN, LOW);
 // Reads the echoPin, returns the sound wave travel time in microseconds
 duration = pulseIn(B_ULTRASONIC_ECHO_PIN, HIGH, 50000);
 // Calculating the distance
 return duration*0.034/2;
}


// Function that executes whenever data is received from master
void receiveEvent(int howMany) {
  char arr[howMany] ;
  int i = 0;
  char val;
  while (Wire.available()) { // loop through all but the last
    arr[i] = Wire.read(); // receive byte as a character
    i += 1;
  }
  char c =  arr[0]; 
  if (sizeof(arr) > 1) {
  val = arr[2];
  }
  
    last_command = c;
    if (!c) {
      last_command_status_code = OK;
    }
    else if (c < 16) {
      do_command(c);
    }
    else if (c > 16 & c < 32) {
    }
    else if (c > 32 & c < 48) {
       if (val) { 
        do_set_variable_command(c, val);
       }
       else {
        last_command_status_code = ERROR_NO_VALUE;
        Serial.println("ERROR: no byte");
       }
    }
    else {
      last_command_status_code = ERROR_UKNOWN;
    }
    communication_timeout = 40;
}

void requestEvent() {
  if (last_command == COMMAND_SEND_STATE) {
      Wire.write(doing_now);
   }
  else {
    Wire.write(last_command_status_code);
  }
 Serial.print("Last command status code: ");
 Serial.println(last_command_status_code, HEX);
}

void do_command(char c) {
   if (c == COMMAND_STOP) {
      reset_ride();
      last_command_status_code = OK;
      doing_now = STOP;
      Serial.println("SET doing_now: STOP");
   }
   else if (c == COMMAND_RIDE_FORWARD || c == COMMAND_FORWARD_STEER_LEFT || c == COMMAND_FORWARD_STEER_RIGHT) {
    if (is_space_free('f', free_space_multiplier)) {

      if (c == COMMAND_RIDE_FORWARD) {
        Serial.println("SET doing_now: RIDE_FORWARD");
        ride_forward(pwm_byte);
        doing_now = RIDE_FORWARD;
      }
      else if (c == COMMAND_FORWARD_STEER_LEFT) {
        Serial.println("SET doing_now: FORWARD_STEER_LEFT");
        steer_left(pwm_byte);
        doing_now = FORWARD_STEER_LEFT;
      }
      else if (c == COMMAND_FORWARD_STEER_RIGHT) {
        Serial.println("SET doing_now: FORWARD_STEER_RIGHT");
        steer_right(pwm_byte);
        doing_now = FORWARD_STEER_RIGHT;
      }
      last_command_status_code = OK;
    }
    else {
      last_command_status_code = ERROR_BARRIER_IN_FRONT;
      delay(100);
    }
  }
  else if (c == RIDE_BACKWARD || c == BACKWARD_STEER_LEFT || c == BACKWARD_STEER_RIGHT) {
    if (is_space_free('b', free_space_multiplier)) {

      if (c == COMMAND_RIDE_BACKWARD) {
        Serial.println("SET doing_now: RIDE_BACKWARD");
        ride_backward(pwm_byte);
        doing_now = RIDE_BACKWARD;
      }
      else if (c == COMMAND_BACKWARD_STEER_LEFT) {
        Serial.println("SET doing_now: BACKWARD_STEER_LEFT");
        backward_steer_left(pwm_byte);
        doing_now = BACKWARD_STEER_LEFT;
      }
      else if (c == COMMAND_BACKWARD_STEER_RIGHT) {
        Serial.println("SET doing_now: BACKWARD_STEER_RIGHT");
        backward_steer_right(pwm_byte);
        doing_now = BACKWARD_STEER_RIGHT;
      }
      last_command_status_code = OK;
    }
    else {
      last_command_status_code = ERROR_BARRIER_IN_BACK;
    }
  }
  else if (c == COMMAND_TURN_LEFT) {
    turn_left();
      last_command_status_code = OK;
      doing_now = TURN_LEFT;
      Serial.println("SET doing_now: TURN_LEFT");
  }
  else if (c == COMMAND_TURN_RIGHT) {
      turn_right();
      last_command_status_code = OK;
      doing_now = TURN_RIGHT;
      Serial.println("SET doing_now: TURN_RIGHT");
  }

  else {
      last_command_status_code = ERROR_UKNOWN;
  }
  delay(100);
}

void do_set_variable_command(char c, char val) {
  Serial.println(val, DEC);
  
  if (c == COMMAND_SET_PWM_BYTE) {
    pwm_byte = val - 0;
    last_command_status_code = OK;
    Serial.print("SET pwm_byte: ");
    Serial.println(pwm_byte, DEC);
  }

  else if (c == COMMAND_SET_SPEED_LEVEL) {
    speed_level = val - 0;
    last_command_status_code = OK;
    Serial.print("SET speed_level: ");
    Serial.println(pwm_byte, DEC);
  }

  else if (c == COMMAND_SET_FREE_SPACE_MULTIPLIER) {
    free_space_multiplier = val - 0;
    last_command_status_code = OK;
    Serial.print("SET free_space_multiplier: ");
    Serial.println(pwm_byte, DEC);
  }
  
  else {
    last_command_status_code = ERROR_UKNOWN;
    Serial.println("ERROR: UKNOWN command");
  }

}
