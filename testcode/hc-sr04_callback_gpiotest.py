import pigpio
import time

# GPIOピンの設定
TRIG = 6
ECHO = 25

# --- コールバック関数 ---
# この関数はECHOピンの状態が変化した瞬間に自動的に呼び出される
def echo_callback(gpio, level, tick):
    if gpio == ECHO:
        print(f"--- !!! ECHOピンに状態変化を検知 !!! ---")
        print(f"GPIO: {gpio}, 状態(Level): {level}, 時刻(tick): {tick}")
        if level == 1:
            print(">>> ECHOがHIGHになりました (反射波の開始)")
        elif level == 0:
            print("<<< ECHOがLOWになりました (反射波の終了)")

# pigpioデーモンに接続
pi = pigpio.pi()
if not pi.connected:
    print("pigpioデーモンに接続できません。")
    exit()

# GPIOピンのモード設定
pi.set_mode(TRIG, pigpio.OUTPUT)
pi.set_mode(ECHO, pigpio.INPUT)
pi.write(TRIG, 0)

# --- コールバックを設定 ---
# ECHOピンの立ち上がり(RISING)と立ち下がり(FALLING)の両方を監視
# EITHER_EDGE は両方の変化を検知する
cb = pi.callback(ECHO, pigpio.EITHER_EDGE, echo_callback)

print("コールバックによるECHOピン反応テストを開始します。")
print("ECHOピンの状態が変化した場合のみ、メッセージが表示されます。")
print("Ctrl+Cで終了します。")

try:
    while True:
        # TRIGパルスを送信して超音波を発射させる
        print("\nTRIG信号を送信...")
        pi.write(TRIG, 1)
        time.sleep(0.00001) # 10us
        pi.write(TRIG, 0)
        
        # 2秒待機して次のテストへ
        # この待機中にECHOピンに変化があれば、コールバック関数が自動でメッセージを表示する
        time.sleep(2)

except KeyboardInterrupt:
    print("\nテストを終了します。")
finally:
    # コールバックをキャンセル
    if 'cb' in locals() and cb.is_set():
        cb.cancel()
    pi.stop()

