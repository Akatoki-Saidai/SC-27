import RPi.GPIO as GPIO
import time
import sys

trig_pin = 15                           # GPIO 15
echo_pin = 14                           # GPIO 14
speed_of_sound = 34370                  # 20℃での音速(cm/s)

GPIO.setmode(GPIO.BCM)                  # GPIOをBCMモードで使用
GPIO.setwarnings(False)                 # GPIO警告無効化
GPIO.setup(trig_pin, GPIO.OUT)          # Trigピン出力モード設定
GPIO.setup(echo_pin, GPIO.IN)           # Echoピン入力モード設定

def get_distance():
    #Trigピンを10μsだけHIGHにして超音波の発信開始
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(trig_pin, GPIO.LOW)

    start_time = time.time()
    timeout = 0.1 # タイムアウトを0.1秒に設定（より短い時間に）

    # EchoピンがHIGHになるのを待つ
    while not GPIO.input(echo_pin):
        if time.time() - start_time > timeout:
            return -1 # タイムアウトした場合、-1を返す

    t1 = time.time() # 超音波発信時刻（EchoピンがHIGHになった時刻）格納

    # EchoピンがLOWになるのを待つ
    while GPIO.input(echo_pin):
        if time.time() - t1 > timeout:
            return -1 # タイムアウトした場合、-1を返す

    t2 = time.time() # 超音波受信時刻（EchoピンがLOWになった時刻）格納
    
    distance = (t2 - t1) * speed_of_sound / 2 # 時間差から対象物までの距離計算
    
    # 最小測定距離（例: 2cm）以下の値は無視する
    if distance < 2:
        return -2 # 最小測定距離以下の場合は-2を返す
    
    return distance

i = 1
while True:                                         # 繰り返し処理
    try:
        print(f"{i}回目")
        distance_val = get_distance()

        if distance_val == -1:
            print("Error: センサーが応答しませんでした")
        elif distance_val == -2:
            print("Error: 最小測定距離を下回っています")
        else:
            distance = '{:.1f}'.format(distance_val)  # 小数点1までまるめ
            print("Distance: " + distance + "cm")       # 表示

        i = i + 1
        time.sleep(1)                               # 1秒まつ

    except KeyboardInterrupt:                       # Ctrl + C押されたたら
        GPIO.cleanup()                              # GPIOお片付け
        sys.exit()                                  # プログラム終了
