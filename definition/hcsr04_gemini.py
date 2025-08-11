import pigpio
import time

# GPIOピンの設定
TRIG = 6  # トリガー
ECHO = 25  # エコー

# 音の速度[cm/s]
sound_velocity = 34300  # 20℃の場合の音速（cm/s）。温度によって微調整可能。
# sound_velocity = 33150 + 60 * 25 # 元のコードの式

pi = pigpio.pi()
if not pi.connected:
    print("pigpioデーモンに接続できません")
    exit()

# ピンモード設定
pi.set_mode(TRIG, pigpio.OUTPUT)
pi.set_mode(ECHO, pigpio.INPUT)

pi.write(TRIG, 0)
time.sleep(0.1)  # センサーの安定化のため待機

def distance():
    # タイムアウトの設定 (μs)
    # HC-SR04の最大測定距離は約4m。往復で約8m。
    # 8m / 343m/s = 0.0233s = 23300μs。
    # 余裕をもって50ms(50000μs)程度のタイムアウトを設定。
    timeout_us = 50000

    # トリガーパルス生成
    pi.write(TRIG, 1)
    time.sleep(0.00001)  # 10μs待機
    pi.write(TRIG, 0)

    start_tick = pi.get_current_tick()
    pulse_start = 0
    pulse_end = 0

    # エコーパルスの立ち上がり（HIGH）を待つ
    while pi.read(ECHO) == 0:
        pulse_start = pi.get_current_tick()
        if pi.get_current_tick() - start_tick > timeout_us:
            print("タイムアウト1: ECHOがHIGHになりませんでした。")
            return None

    # エコーパルスの立ち下がり（LOW）を待つ
    while pi.read(ECHO) == 1:
        pulse_end = pi.get_current_tick()
        if pi.get_current_tick() - start_tick > timeout_us:
            print("タイムアウト2: ECHOがLOWになりませんでした。")
            return None

    if pulse_end < pulse_start: # タイムスタンプが一周した場合の処理
        pulse_duration = pulse_end + (2**32 - pulse_start)
    else:
        pulse_duration = pulse_end - pulse_start

    # パルス幅から距離を計算
    # 距離(cm) = (時間(s) * 音速(cm/s)) / 2
    distance = (pulse_duration / 1000000.0) * sound_velocity / 2

    return round(distance, 2)

if __name__ == "__main__":
    try:
        while True:
            dist = distance()
            if dist is not None:
                print(f"距離: {dist} cm")
            else:
                print("測定失敗")
            time.sleep(1)
    except KeyboardInterrupt:
        print("測定を終了します")
    finally:
        pi.stop()
