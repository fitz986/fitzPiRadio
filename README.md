# fitzPiRadio
Raspberry Pi stuffed in vintage General Electric Radio

# Background
I stumbled upon a 1940s General Electric Model 321 at the Alameda Antqiues Faire for $10. It wasn't a functioning radio, 
so I decided to make an internet radio it. 

# Project Goals
Minimal external modifications to the radio. That meant preserving original look, utilizing all existing buttons, volume
controls, stational dials, etc.  In addition the station dial would automagically move to preset position after station button
was pressed. 

# Hardware
* General Electric Model 321 Radio
* Raspberry Pi Model 3
* Servo motor for station dial control
* 2 Dayton Audio Speaker Drivers (original mono speaker sounded pretty terrible)
* HIfiBerry AMP+ Sound Card for Raspberry Pi
* MCP3008 10 bit ADC for volume pot readings

# Pinout

| Pin              | Function  |
|:----------------:| :-----:|
| BCM11            | Button 1 |
| BCM13            | Button 2 |
| BCM15            | Button 3 |
| BCM16            | Button 4 |
| BCM18            | Button 5 |
| BCM22            | ServoPin |
| BCM7             | LED      |
| BCM23            | SPICLK   |
| BCM21            | SPIMISO  |
| BCM19            | SPIMOSI  |
| BCM24            | SPICS    |


