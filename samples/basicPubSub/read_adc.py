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
#感圧センサの入力チェック間隔（3秒）
SLEEP_TIME=3
#感圧センサの入力チェック回数（3回）
CHECK_CNT=3
#お米が満たされたかを判定する時の閾値
FILL_THR=20
#お米が無くなった事を判定する割合（2割を切ったらカートに追加する）
LOW_RATE=0.2
#お米が補充された事を判定する割合（8割を超えたら補充完了）
HIGH_RATE=0.8
#感圧センサの誤差教養範囲（±5%）
ERROR_RATE_UNDER=0.95
ERROR_RATE_UPPER=1.05


# set minimum
#米びつが空の時の重さを設定
def set_minimum():
    print "start set_minimum"
    try:
        min_data=-1
        min_count=0
        while True:
            resp = spi.xfer2([0x68, 0x00])
            value = (resp[0] * 256 + resp[1]) & 0x3ff
            print value
            #3秒×3回、重さが変わらなければ空の重さの設定が完了
            if min_count <= CHECK_CNT :
                # set minimum weight
                if min_data == -1 :
                    if value > 0 :
                        min_data=value
                        min_count=1
                else :
                    if min_data >= 0 :
                        #感圧センサの値に対し、±5%は許容する
                        if  min_data*ERROR_RATE_UNDER <= value and value <= min_data*ERROR_RATE_UPPER :
                            min_count=min_count+1
                            if value > min_data :
                                min_data=value
                        else :
                            min_data=value
                            min_count=1
                            led.light_off_all_red()

                # light red LED
                #1回測定するたびに赤いLEDが点灯していく。（３つ点いたら完了）
                led.light_on_red(min_count)
            else :
                return min_data
                break
            time.sleep(SLEEP_TIME) 
    except KeyboardInterrupt:
        spi.close()

# set maximum
#米びつが満たされた時の重さを設定
def set_maximum(min_data):
    print "start set_maximum"
    try:
        max_data=-1
        max_count=0
        while True:
            resp = spi.xfer2([0x68, 0x00])
            value = (resp[0] * 256 + resp[1]) & 0x3ff
            print value
            #3秒×3回、重さが変わらなければ満タンの時の重さの設定が完了
            if max_count <= CHECK_CNT :
                # set maximum weight
                if value > min_data+FILL_THR :
                    if max_data == -1 :
                        max_data=value
                        max_count=1                        
                    if max_data >= 0 :
                        #感圧センサの値に対し、±5%は許容する
                        if max_data*ERROR_RATE_UNDER <= value and value <= max_data*ERROR_RATE_UPPER :
                            max_count=max_count+1
                            if value > max_data :
                                max_data=value
                        else :                
                            max_data=value
                            max_count=1
                            led.light_off_all_green()

                # light green LED
                #1回測定するたびに緑のLEDが点灯していく。（３つ点いたら完了）
                led.light_on_green(max_count)

            else :
                return max_data
                break
            time.sleep(SLEEP_TIME) 

    except KeyboardInterrupt:
        spi.close()

#米の残量をチェック
def check_weight(min_data, max_data) :
    print "start check_weight"
    try:
        order_flag=0
        #米が無くなった判定を行う閾値
        low_thr=(max_data-min_data)*LOW_RATE+min_data
        print "low_thr=%s" % low_thr
        #米が満たされた判定を行う閾値
        high_thr=(max_data-min_data)*HIGH_RATE+min_data
        print "high_thr=%s" % high_thr

        #カート追加済みを管理するフラグ
        order_count=0
        #お米が満たされた事を管理するフラグ
        fill_count=0
        while True:
            resp = spi.xfer2([0x68, 0x00])
            value = (resp[0] * 256 + resp[1]) & 0x3ff
            print value

            if low_thr !=- 1 and high_thr !=- 1 :
                #閾値を下回り、カート未追加の場合はAWS IoTへリクエストを送る
                if low_thr > value and order_flag == 0 :
                    order_count = order_count+1;
                    if order_count >= CHECK_CNT :
                        basicPubSub.sendmsg(myAWSIoTMQTTClient)
                        order_flag=1
                        order_count=0
                        fill_count=0
                        led.flashing(37,3)
                        led.light_off_all_green()
                #閾値を超えた場合は、お米が補充されたとみなす
                if high_thr < value :
                    order_flag=0
                    fill_count = fill_count+1
                    led.light_on_green(fill_count)
                    

            time.sleep(SLEEP_TIME) 

    except KeyboardInterrupt:
        spi.close()


#メイン処理
try:
    print "mqtt init start"
    #メイン処理
    myAWSIoTMQTTClient = basicPubSub.init_mqtt()
    myAWSIoTMQTTClient = basicPubSub.connect_aws(myAWSIoTMQTTClient)

    led.all_off()
    #米びつが空の時の重さを設定
    min_data = set_minimum()
    #米びつが満たされた時の重さを設定
    max_data = set_maximum(min_data)
    #米の残量をチェック
    check_weight(min_data, max_data)

except KeyboardInterrupt:
    spi.close()
