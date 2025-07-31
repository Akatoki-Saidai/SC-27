import pigpio
import time

# pigpioデーモンに接続
pi = pigpio.pi()

if not pi.connected:
    print("pigpioデーモンに接続できませんでした。")
    exit(1)

GPIO_PIN = 4

# GPIO4を出力モードに設定
pi.set_mode(GPIO_PIN, pigpio.OUTPUT)

# GPIO4をオン（HIGH）にする
pi.write(GPIO_PIN, 1)

# 5秒間オンのままにする
print("GPIO4をオンにしました。エンターでオフにします。")
input()

# GPIO4をオフ（LOW）にする
pi.write(GPIO_PIN, 0)
print("GPIO4をオフにしました。")

# pigpioとの接続を終了
pi.stop()
