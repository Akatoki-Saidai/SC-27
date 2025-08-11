import RPi.GPIO as GPIO
import time
import sys

trig_pin = 6
echo_pin = 27
speed_of_sound = 34370  # 20℃での音速(cm/s)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(trig_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)

def get_distance(trig_pulse_duration, timeout_duration):
    # Trigピンを引数で指定された時間だけHIGHにして超音波の発信開始
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(trig_pulse_duration)
    GPIO.output(trig_pin, GPIO.LOW)

    # EchoピンがHIGHになるまで待機（タイムアウト付き）
    start_time = time.time()
    while not GPIO.input(echo_pin):
        if (time.time() - start_time) > timeout_duration:
            return -1  # タイムアウト
    t1 = time.time()

    # EchoピンがLOWになるまで待機（タイムアウト付き）
    start_time = time.time()
    while GPIO.input(echo_pin):
        if (time.time() - start_time) > timeout_duration:
            return -1  # タイムアウト
    t2 = time.time()

    # 時間差から対象物までの距離を計算
    return (t2 - t1) * speed_of_sound / 2

try:
    # ユーザーからの入力を受け付ける
    TRIG_PULSE_DURATION = float(input("トリガー信号の時間（秒、推奨：0.000010）を入力してください: "))
    TIMEOUT_DURATION = float(input("タイムアウト時間（秒、推奨：0.1）を入力してください: "))
    
    i = 0
    while True:
        distance = get_distance(TRIG_PULSE_DURATION, TIMEOUT_DURATION)
        print(f"--- 測定回数: {i} ---")
        if distance != -1:
            print("Distance: {:.1f} cm".format(distance))
        else:
            print("測定に失敗しました")
        time.sleep(0.1)
        i = i + 1

except ValueError:
    print("無効な入力です。数値を入力してください。")
except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()
