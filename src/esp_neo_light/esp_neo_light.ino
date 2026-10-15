#include <Adafruit_NeoPixel.h>

#define pwm_input 14
#define neo_out 13
#define green_pwm 1200
#define red_pwm 1500
#define yellow_pwm 1800
#define red_blink_pwm 2100

#define PIXEL_COUNT 14

Adafruit_NeoPixel strip(PIXEL_COUNT, neo_out, NEO_RGB + NEO_KHZ800);

uint32_t green = strip.Color(255, 0, 0);
uint32_t yellow = strip.Color(255, 255, 0);
uint32_t red = strip.Color(0, 255, 0);
uint32_t blue = strip.Color(0, 0, 255);


void setup() {
  #if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  Serial.begin(9600);
  pinMode(pwm_input, INPUT);
  strip.begin(); 
  strip.fill(red);
  strip.show();
  delay(1000);
  strip.clear();
  strip.show();
}

void input(){
  unsigned long highTime = pulseIn(pwm_input, HIGH, 50000); 
  Serial.println(highTime);
  if (highTime > 0) {
    Serial.print("Pulse Width: ");
    Serial.print(highTime);
    Serial.println(" us");
    set_color(highTime);
}
}

void set_color(int pulseWidth){
  if (pulseWidth > 1100 && pulseWidth < 1300) {         // Targets ~1200
    strip.fill(green, 0);
  } 
  else if (pulseWidth > 1400 && pulseWidth < 1600) {    // Targets ~1500
    strip.fill(red, 0);
  } 
  else if (pulseWidth > 1700 && pulseWidth < 1900) {    // Targets ~1800
    strip.fill(yellow, 0);
  } 
  else if (pulseWidth > 2000 && pulseWidth < 2200){
    strip.clear();
  }
  else{
    strip.fill(blue, 0);
  }
  strip.show();
}

void loop() {
  input();
}
