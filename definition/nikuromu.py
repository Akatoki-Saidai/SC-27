import RPi.GPIO as GPIO
import time

#ニクロム線切断
nichrome_pin = 16
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(nichrome_pin, GPIO.OUT)
    GPIO.output(nichrome_pin, 1)
    for i in range(1, 10 + 1):
        print(f"{i}秒目")
        time.sleep(1)
    # 10秒あつくする
    GPIO.output(nichrome_pin, 0)

    print("ニクロム線切断完了")
except KeyboardInterrupt:
    GPIO.output(nichrome_pin, 0)
    GPIO.cleanup() # GPIOをクリーンアップ
