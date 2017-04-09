#!/usr/bin/env python
# Read the analog sensor value via MCP3002.

import spidev
import time
import subprocess
import basicPubSub
import led

# open SPI device 0.0
spi = spidev.SpiDev()
spi.open(0, 0)

#define
SLEEP_TIME=3
CHECK_CNT=3
FILL_THR=20
LOW_RATE=0.2
HIGH_RATE=0.8
ERROR_RATE_UNDER=0.95
ERROR_RATE_UPPER=1.05

# set minimum
def set_minimum():
    print "start set_minimum"
    try:
        min_data=-1
        min_count=0
        while True:
            resp = spi.xfer2([0x68, 0x00])
            value = (resp[0] * 256 + resp[1]) & 0x3ff
            print value
            if min_count <= CHECK_CNT :
                # set minimum weight
                if min_data == -1 :
                    if value > 0 :
                        min_data=value
                        min_count=1
                else :
                    if min_data >= 0 :
                        if  min_data*ERROR_RATE_UNDER <= value and value <= min_data*ERROR_RATE_UPPER :
                            min_count=min_count+1
                            if value > min_data :
                                min_data=value
                        else :
                            min_data=value
                            min_count=1
                            led.light_off_all_red()

                # light red LED
                led.light_on_red(min_count)
            else :
                return min_data
                break
            time.sleep(SLEEP_TIME) 
    except KeyboardInterrupt:
        spi.close()

# set maximum
def set_maximum(min_data):
    print "start set_maximum"
    try:
        max_data=-1
        max_count=0
        while True:
            resp = spi.xfer2([0x68, 0x00])
            value = (resp[0] * 256 + resp[1]) & 0x3ff
            print value
            if max_count <= CHECK_CNT :
                # set maximum weight
                if value > min_data+FILL_THR :
                    if max_data == -1 :
                        max_data=value
                        max_count=1                        
                    if max_data >= 0 :
                        if max_data*ERROR_RATE_UNDER <= value and value <= max_data*ERROR_RATE_UPPER :
                            max_count=max_count+1
                            if value > max_data :
                                max_data=value
                        else :                
                            max_data=value
                            max_count=1
                            led.light_off_all_green()

                # light green LED
                led.light_on_green(max_count)

            else :
                return max_data
                break
            time.sleep(SLEEP_TIME) 

    except KeyboardInterrupt:
        spi.close()


def check_weight(min_data, max_data) :
    print "start check_weight"
    try:
        order_flag=0
        low_thr=(max_data-min_data)*LOW_RATE+min_data
        print "low_thr=%s" % low_thr
        high_thr=(max_data-min_data)*HIGH_RATE+min_data
        print "high_thr=%s" % high_thr

        order_count=0
        fill_count=0
        while True:
            resp = spi.xfer2([0x68, 0x00])
            value = (resp[0] * 256 + resp[1]) & 0x3ff
            print value

            if low_thr !=- 1 and high_thr !=- 1 :
                if low_thr > value and order_flag == 0 :
                    order_count = order_count+1;
                    if order_count >= CHECK_CNT :
                        basicPubSub.sendmsg(myAWSIoTMQTTClient)
                        order_flag=1
                        order_count=0
                        fill_count=0
                        led.flashing(37,3)
                        led.light_off_all_green()
                if high_thr < value :
                    order_flag=0
                    fill_count = fill_count+1
                    led.light_on_green(fill_count)
                    

            time.sleep(SLEEP_TIME) 

    except KeyboardInterrupt:
        spi.close()


try:
    print "mqtt init start"
    myAWSIoTMQTTClient = basicPubSub.init_mqtt()
    myAWSIoTMQTTClient = basicPubSub.connect_aws(myAWSIoTMQTTClient)

    led.all_off()
    min_data = set_minimum()
    max_data = set_maximum(min_data)
    check_weight(min_data, max_data)

except KeyboardInterrupt:
    spi.close()
