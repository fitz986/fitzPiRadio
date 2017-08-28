# Servo Control
import time
import RPi.GPIO as GPIO
from datetime import date as dt
import datetime
import requests
import subprocess


######## initialize GPIO pins############
b1Pin = 11
b2Pin = 13
b3Pin = 15
b4Pin = 16
b5Pin = 18
servoPin = 22
ledPin = 7
SPICLK = 23
SPIMISO = 21
SPIMOSI = 19
SPICS = 24

GPIO.setmode(GPIO.BOARD)

#sets up servo, pushbuttons, LED, & SPI pins
GPIO.setup(servoPin, GPIO.OUT)
GPIO.setup(b1Pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(b2Pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(b3Pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(b4Pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(b5Pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def check_volume(trim_pot_changed, last_read):
	DEBUG = 0
	tolerance =50
	# read the analog pin
	trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
	pot_adjust = abs(trim_pot - last_read)
	if DEBUG:
		print "trim_pot:", trim_pot
		print "pot_adjust:", pot_adjust
		print "last_read", last_read
	if pot_adjust > tolerance:
		trim_pot_changed = True
	else:
		trim_pot_changed = False
		
	if DEBUG:
		print "trim_pot_changed", trim_pot_changed
	if ( trim_pot_changed ):
		set_volume = trim_pot / 10.24           # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
		set_volume = round(set_volume)          # round out decimal valu
		set_volume = int(set_volume)            # cast volume as integer
		volume = 100-set_volume
		print 'Volume = ', volume
		vol_cmd = 'mpc volume ' +str(volume)
		subprocess.call(vol_cmd, shell=True)
		#set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' .format(volume = set_volume)
		#os.system(set_vol_cmd)  # set volume

		if DEBUG:
			print "set_volume", set_volume
			print "tri_pot_changed", set_volume

	# save the potentiometer reading for the next loop
	last_read = trim_pot
	return trim_pot_changed, last_read


def get_duty_cyle(degrees):
	dc = (1./18.)*degrees + 2
	return dc

def move(desired_position, wait_period=.05):
	global current_position
	pwm = GPIO.PWM(servoPin, 50)
	pwm.start(get_duty_cyle(current_position))
	if desired_position>current_position:
		for i in range(current_position, desired_position):
	   		dc = get_duty_cyle(i) 
	   		pwm.ChangeDutyCycle(dc)
	   		time.sleep(wait_period)
	else:
		for i in range(current_position, desired_position, -1):
	   		dc = get_duty_cyle(i) 
	   		pwm.ChangeDutyCycle(dc)
	   		time.sleep(wait_period)
	pwm.stop()
	current_position = desired_position
	

#check which button is pressed
def get_button():
	if not GPIO.input(b1Pin):
		return int(1)
	elif not GPIO.input(b2Pin):
		return int(2)
	elif not GPIO.input(b3Pin):
		return int(3)
	elif not GPIO.input(b4Pin):
		return int(4)
	elif not GPIO.input(b5Pin):
		return int(5)
	else:
		return int(0)
		
#define action on each button
def on_button(button):
	if button == 1:
		print "Playing MBE"
		GPIO.output(ledPin, True)
		move(0)
		response = requests.get('http://www.kcrw.com/music/shows/morning-becomes-eclectic/latest-show/player.json')
		data = response.json()
		media = data['media']
		url = media[0]['url']
		subprocess.call('mpc clear', shell=True)
		string = 'mpc add '+ url
		subprocess.call(string, shell=True)
		subprocess.call('mpc play', shell=True)
			
	elif button == 2:
		print "Playing KCRW on air"
		GPIO.output(ledPin, True)
		move(45)
		url = 'https://kcrw.streamguys1.com/kcrw_192k_mp3_on_air'
		string = 'mpc add '+ url
		subprocess.call('mpc clear', shell=True)
		subprocess.call(string, shell=True)
		subprocess.call('mpc play', shell=True)
		
	elif button == 3:	
		print "Playing KQED"
		move(90)
		url = 'https://streams2.kqed.org/kqedradio'
		string = 'mpc add '+ url
		subprocess.call('mpc clear', shell=True)
		subprocess.call(string, shell=True)
		subprocess.call('mpc play', shell=True)
		
	elif button == 4:
		print "button 4"
		move(135)
		url = 'http://live-mp3-128.kexp.org:80/kexp128.mp3'
		string = 'mpc add '+ url
		subprocess.call('mpc clear', shell=True)
		subprocess.call(string, shell=True)
		subprocess.call('mpc play', shell=True)
	elif button ==5:
		print "Spotify mode"
		move(180)

	else:
		print "no buttons pressed, stopping music"
		subprocess.call('mpc clear', shell=True)
		GPIO.output(ledPin, False)
				
last_button = get_button()
#sets dial to 90 deg
current_position = 45
move(90)

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

last_read = 0       # this keeps track of the last potentiometer value
# to keep from being jittery we'll only change
trim_pot_changed = False 

		
while True:
	button = get_button() #check which button is pressed
	if button != last_button: #compare against last time it checked
		on_button(button)
	last_button = button
	pot_status, current_read = check_volume(trim_pot_changed, last_read)
	trim_pot_changed = pot_status
	last_read = current_read
	time.sleep (1)
