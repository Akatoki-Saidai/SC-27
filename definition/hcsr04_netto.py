import RPi.GPIO as GPIO
import time
import sys

trig_pin = 6
echo_pin = 25
speed_of_sound = 34370  # 20℃での音速(cm/s)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(trig_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)

def get_distance():
    # Trigピンを10μsだけHIGHにして超音波の発信開始
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(trig_pin, GPIO.LOW)

    # EchoピンがHIGHになるまで待機（タイムアウト付き）
    start_time = time.time()
    while not GPIO.input(echo_pin):
        if (time.time() - start_time) > 0.1:
            return -1  # タイムアウト
    t1 = time.time()

    # EchoピンがLOWになるまで待機（タイムアウト付き）
    start_time = time.time()
    while GPIO.input(echo_pin):
        if (time.time() - start_time) > 0.1:
            return -1  # タイムアウト
    t2 = time.time()

    # 時間差から対象物までの距離を計算
    return (t2 - t1) * speed_of_sound / 2

try:
    while True:
        distance = get_distance()
        if distance != -1:
            print("Distance: {:.1f} cm".format(distance))
        else:
            print("測定に失敗しました")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()
