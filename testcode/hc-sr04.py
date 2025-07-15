import pigpio
import time

# GPIOピンの設定
TRIG = 23  # トリガーピン
ECHO = 24  # エコーピン

pi = pigpio.pi()
if not pi.connected:
    print("pigpioデーモンに接続できません")
    exit()

pi.set_mode(TRIG, pigpio.OUTPUT)
pi.set_mode(ECHO, pigpio.INPUT)
pi.write(TRIG, 0)

def measure_distance():
    # トリガーを10μsだけHIGHにする
    pi.write(TRIG, 0)
    time.sleep(0.0002)
    pi.write(TRIG, 1)
    time.sleep(0.00001)
    pi.write(TRIG, 0)

    # エコーパルスの立ち上がりを待つ
    start_time = time.time()
    while pi.read(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - start_time > 1:
            return None  # タイムアウト

    # エコーパルスの立ち下がりを待つ
    start_time = time.time()
    while pi.read(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - start_time > 1:
            return None  # タイムアウト

    pulse_duration = pulse_end - pulse_start
    # 距離を計算（音速は約34300cm/s）
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

if __name__ == "__main__":
    try:
        while True:
            try:
                dist = measure_distance()
                if dist is not None:
                    print("距離: {} cm".format(dist))
                else:
                    print("測定失敗")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("測定を終了します")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
    finally:
        pi.stop()
