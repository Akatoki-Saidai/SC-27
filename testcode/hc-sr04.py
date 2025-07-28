import pigpio
import time

# 定数
SOUND_VELOCITY = 34370  # 音の速度 (cm/s)

# GPIOピンの設定
TRIG_PIN = 6
ECHO_PIN = 25

class HCSR04:
    def __init__(self, pi, trig_pin, echo_pin):
        self.pi = pi
        self.trig = trig_pin
        self.echo = echo_pin

        # 内部で使う状態変数
        self._pulse_start = 0
        self._pulse_end = 0

        # GPIOピンのモード設定
        self.pi.set_mode(self.trig, pigpio.OUTPUT)
        self.pi.set_mode(self.echo, pigpio.INPUT)

        # トリガーピンをLOWに初期化
        self.pi.write(self.trig, 0)

        # コールバックを設定
        self._callback = self.pi.callback(self.echo, pigpio.EITHER_EDGE, self._echo_callback)
        time.sleep(0.1) # 安定待機

    def _echo_callback(self, gpio, level, tick):
        # コールバック
        if level == 1:
            self._pulse_start = tick
        elif level == 0:
            self._pulse_end = tick

    def measure(self):
        # 前回の測定値をリセット
        self._pulse_start = 0
        self._pulse_end = 0
        
        # 10μ秒のトリガーパルスを送信
        self.pi.gpio_trigger(self.trig, 10)

        # 測定完了を待つ
        start_time = time.time()
        while self._pulse_end == 0:
            if time.time() - start_time > 0.2:
                return None

        pulse_duration = self._pulse_end - self._pulse_start
        distance = (pulse_duration * SOUND_VELOCITY) / (1000000 * 2)
        
        return round(distance, 2)

    def cancel(self):
        """コールバックを解除してリソースを解放する"""
        self._callback.cancel()

# --- メインの処理 ---
if __name__ == "__main__":

    pi = None
    ultrasonic = None
    try:
        # pigpioデーモンに接続
        pi = pigpio.pi()
        if not pi.connected:
            print("pigpioデーモンに接続できません")
            exit()
        
        # センサーのインスタンスを作成
        ultrasonic = HCSR04(pi, TRIG_PIN, ECHO_PIN)
        
        while True:
            dist = ultrasonic.measure()
            if dist is not None:
                print(f"距離: {dist} cm")
            else:
                print("測定失敗")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n測定を終了します")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        if ultrasonic:
            ultrasonic.cancel()
        if pi:
            pi.stop()