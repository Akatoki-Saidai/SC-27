# import RPi.GPIO as GPIO  # GPIOモジュールをインポート
from time import sleep
import motordrive # 作成したmotordrive.pyをインポート

def main():
    # GPIOピン番号モードの設定
    # GPIO.setmode(GPIO.BCM)  # または GPIO.setmode(GPIO.BOARD)

    try:
        print("--- motordrive.py の move() 関数テスト ---")

        print("前進 (w): 強さ1.0で、5秒間動かす")
        motordrive.move('w', 1.0, 5)
        sleep(1)
        """

        print("後退 (s): 強さ1.0で、1.5秒間動かす")
        motordrive.move('s', 1.0, 1.5)
        sleep(1)

        print("右モーターのみ前進 (e): 強さ1.0で、2秒間動かす")
        motordrive.move('e', 1.0, 2)
        sleep(1)

        print("左モーターのみ前進 (q): 強さ1.0で、2秒間動かす")
        motordrive.move('q', 1.0, 2)
        sleep(1)

        print("左旋回 (a): 強さ0.9で、1.5秒間動かす")
        motordrive.move('a', 0.9, 1.5)
        sleep(1)

        print("右旋回 (d): 強さ0.9で、1.5秒間動かす")
        motordrive.move('d', 0.9, 1.5)
        sleep(1)
        """
        
        print("Finish!!!!!!!!!!")

    except KeyboardInterrupt:
        print("\nプログラムが中断されました。モーターを停止します。")
        # setup_motors()でモーターオブジェクトが取得できている場合は、安全のため停止処理を実行
        motor_right, motor_left = motordrive.setup_motors()
        if motor_right and motor_left:
            motordrive.stop_motors(motor_right, motor_left)
    finally:
        # GPIOクリーンアップ
        # GPIO.cleanup()
        print("GPIOクリーンアップ完了。")

if __name__ == "__main__":
    main()
