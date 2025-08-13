#ニクロム線切断
nichrome_pin = 16
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(nichrome_pin, GPIO.OUT)
    GPIO.output(nichrome_pin, 1)
    time.sleep(5) # 5秒あつくする
    GPIO.output(nichrome_pin, 0)

    print("ニクロム線切断完了")
except KeyboardInterrupt:
    GPIO.output(nichrome_pin, 0)
    GPIO.cleanup() # GPIOをクリーンアップ
