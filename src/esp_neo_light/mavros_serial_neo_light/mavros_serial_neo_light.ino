#include <Adafruit_NeoPixel.h>

// Set this to the digital pin connected to your NeoPixel DIN
#define PIN        6 
// Set this to the number of LEDs you are driving
#define NUMPIXELS  1 

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  // Must match the baud rate in the Jetson Python script
  Serial.begin(115200); 
  
  pixels.begin();
  pixels.setBrightness(50); // Set brightness (0-255)
  
}

void loop() 
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    switch(cmd) {
      case 'Y':
        pixels.fill(pixels.color(255, 255, 0),0); // Yellow
        break;
      case 'G':
        setLEDColor(0, 255, 0);   // Green
        break;
      case 'R':
        setLEDColor(255, 0, 0);   // Red
        break;
    }
  }
}

void setLEDColor(int r, int g, int b) {
  pixels.clear();
  for(int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
  pixels.show();
}