import RPi.GPIO as GPIO
import time
import sys

trig_pin = 6                            # GPIO 6
echo_pin = 27                           # GPIO 27
speed_of_sound = 34370                  # 20℃での音速(cm/s)

GPIO.setmode(GPIO.BCM)                  # GPIOをBCMモードで使用
GPIO.setwarnings(False)                 # BPIO警告無効化
GPIO.setup(trig_pin, GPIO.OUT)          # Trigピン出力モード設定
GPIO.setup(echo_pin, GPIO.IN)           # Echoピン入力モード設定

def get_distance():
    # Trigピンを10μsだけHIGHにして超音波の発信開始
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(trig_pin, GPIO.LOW)

    start_time = time.time()
    while not GPIO.input(echo_pin):
        if (time.time() - start_time) > 0.1: # 0.1秒経ってもHIGHにならない場合
            return -1 # -1などエラー値を返す
    t1 = time.time()

    start_time = time.time()
    while GPIO.input(echo_pin):
        if (time.time() - start_time) > 0.1: # 0.1秒経ってもLOWにならない場合
            return -1 # -1などエラー値を返す
    t2 = time.time()

    return (t2 - t1) * speed_of_sound / 2


while True:                                         # 繰り返し処理
    try:
        print("測定中")
        distance = '{:.1f}'.format(get_distance())  # 小数点1までまるめ
        print("Distance: " + distance + "cm")       # 表示
        print("測定完了")
        time.sleep(1)                               # 1秒まつ

    except KeyboardInterrupt:                       # Ctrl + C押されたたら
        GPIO.cleanup()                              # GPIOお片付け
        sys.exit()                                  # プログラム終了
