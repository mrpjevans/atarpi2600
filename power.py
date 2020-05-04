#!/bin/python
# Simple script for shutting down the Raspberry Pi after a button has been held for n seconds
# Also, if momentary pressed, emits a keypress
# by PJ Evans @mrpjevans
# Insipred by Inderpreet Singh

import RPi.GPIO as GPIO
import time
import os
import uinput

# Time tracking
start = elapsed = 0

# Button state (prevents mistaken readings as the button changes state)
isDown = False

# Hold duration to trigger shutdown (seconds)
holdFor = 3

# LED
ledPin = 17
ledState = True

# Input pins and keypresses
powerPin = 4
pins = {
        4: uinput.KEY_Q,        # Power
        18: uinput.KEY_T,       # TV Mode
        27: uinput.KEY_E,       # P1 Difficulty
        22: uinput.KEY_R,       # P2 Difficulty
}

# Convert keypresses into array for uinput to understand
kbdArray = []
for key, value in pins.iteritems():
        kbdArray.append(value)
kbd = uinput.Device(kbdArray)

# Use the Broadcom SOC Pin numbers
# Setup the Pin with Internal pullups enabled and PIN in reading mode.
GPIO.setmode(GPIO.BCM)

# Setup the pins
for key, value in pins.iteritems():
        GPIO.setup(key, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Light the LED
GPIO.setup(ledPin, GPIO.OUT)
GPIO.output(ledPin, True)

# Our function on what to do when the button is pressed
def Shutdown(channel):
        global start, end, elapsed, isDown, powerPin, kbd, keyPress

        # Read the button
        state = GPIO.input(powerPin)

        if state == 0 and isDown == False: # Button down (ignore any additional signals until button comes up again)
                start = time.time()
                isDown = True

        elif state == 1 and isDown == True: # Momentary push, send keystroke and make sure led is on
                isDown = False
                kbd.emit_click(pins[powerPin])
                GPIO.output(ledPin, True)

# Fired when a button is pressed other than power, emit its corresponding keystroke
def switchToggle(channel):
                kbd.emit_click(pins[channel])

# Add our function to execute when the button pressed event happens
GPIO.add_event_detect(powerPin, GPIO.BOTH, callback = Shutdown)

# Add callbacks for all our pins (except power, which is a special case)
for key, value in pins.iteritems():
        if key != powerPin:
                GPIO.add_event_detect(key, GPIO.BOTH, callback = switchToggle, bouncetime = 600)

# Now wait!
while 1:

        if isDown == True:

                # Blink LED
                ledState = not ledState
                GPIO.output(ledPin, ledState)

                # How long has past, if longer than the threshold, initiate Shutdown
                elapsed = time.time() - start
                if elapsed >= holdFor:

                        # Prevent multiple calls to os
                        isDown = False

                        # Shutdown
                        print "Shutdown"
                        os.system("sudo shutdown -h now")

        time.sleep(.2)

    