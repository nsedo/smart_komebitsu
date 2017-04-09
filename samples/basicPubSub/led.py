#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(33,GPIO.OUT)
GPIO.setup(35,GPIO.OUT)
GPIO.setup(37,GPIO.OUT)

def flashing(pin,fcnt):
	count = 0;
	while count < fcnt:
		GPIO.output(pin,True)
		time.sleep(0.5)
		GPIO.output(pin,False)
		time.sleep(0.5)
		count += 1

def light_on(pin):
        GPIO.output(pin,True)

def light_off(pin):
        GPIO.output(pin,False)

def light_on_red(num):
        pin = 11
        if num == 1 :
                pin = 11
        elif num == 2 :
                pin = 13
        elif num == 3 :
                pin = 15
        light_on(pin)

def light_on_green(num):
        pin = 33
        if num == 1 :
                pin = 33
        elif num == 2 :
                pin = 35
        elif num == 3 :
                pin = 37
        light_on(pin)

def light_off_all_red():
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,False)

def light_off_all_green():
        GPIO.output(33,False)
        GPIO.output(35,False)
        GPIO.output(37,False)

def all_off():
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,False)
        GPIO.output(33,False)
        GPIO.output(35,False)
        GPIO.output(37,False)
