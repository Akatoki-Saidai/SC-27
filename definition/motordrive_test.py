# 新井

import RPi.GPIO as GPIO  # GPIOモジュールをインポート
from time import sleep
import motordrive # 作成したmotordrive.pyをインポート

def main():
    # GPIOピン番号モードの設定
    GPIO.setmode(GPIO.BCM)  # または GPIO.setmode(GPIO.BOARD)

    try:
        print("--- motordrive.py の move() 関数テスト ---")

        print("前進 (w): 1秒間、強さ0.7で動かす")
        motordrive.move('w', 0.7, 1)
        sleep(1)

        print("後退 (s): 1.5秒間、強さ0.5で動かす")
        motordrive.move('s', 0.5, 1.5)
        sleep(1)

        print("右モーターのみ前進 (e): 2秒間、強さ0.8で動かす")
        motordrive.move('e', 0.8, 2)
        sleep(1)

        print("左モーターのみ前進 (q): 2秒間、強さ0.8で動かす")
        motordrive.move('q', 0.8, 2)
        sleep(1)

        print("左旋回 (a): 1.5秒間、強さ0.9で動かす")
        motordrive.move('a', 0.9, 1.5)
        sleep(1)

        print("右旋回 (d): 1.5秒間、強さ0.9で動かす")
        motordrive.move('d', 0.9, 1.5)
        sleep(1)
        
        print("Finish!!!!!!!!!!")

    except KeyboardInterrupt:
        print("\nプログラムが中断されました。モーターを停止します。")
        # setup_motors()でモーターオブジェクトが取得できている場合は、安全のため停止処理を実行
        motor_right, motor_left = motordrive.setup_motors()
        if motor_right and motor_left:
            motordrive.stop_motors(motor_right, motor_left)
    finally:
        # GPIOクリーンアップ
        GPIO.cleanup()
        print("GPIOクリーンアップ完了。")

if __name__ == "__main__":
    main()
