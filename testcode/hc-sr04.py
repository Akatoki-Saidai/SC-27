import pigpio
import time

# GPIOピンの設定
TRIG = 6  # トリガー
ECHO = 25  # エコー

# 音の速度
sound_velosity = 34370

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
    timeout_start = pi.get_current_tick()
    while pi.read(ECHO) == 0:
        if pi.get_current_tick() - timeout_start > 10000000: # 10秒タイムアウト
            return None
    pulse_start = pi.get_current_tick()

    # ECHOピンがLOWになるのを待つ（パルス終了）
    timeout_start = pi.get_current_tick()
    while pi.read(ECHO) == 1:
        if pi.get_current_tick() - timeout_start > 10000000: # 10秒タイムアウト
            return None
    pulse_end = pi.get_current_tick()

    # パルス幅から距離を計算
    pulse_duration = pulse_end - pulse_start
    
    # 距離(cm) = (時間(s) * 音速(cm/s)) / 2
    distance = (pulse_duration / 1000000.0) * (sound_velosity / 2)
    
    return round(distance, 2)

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
