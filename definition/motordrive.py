import RPi.GPIO as GPIO  # GPIOモジュールをインポート
from gpiozero import Motor
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import numpy as np

from bno055 import BNO055 # BNO055を使う場合はコメント解除
import make_csv as csv # CSV出力を使う場合はコメント解除

delta_power = 0.1 # スムーズな加速・減速のための刻み幅

# DCモータのピン設定
# 回路図に基づいたピン割り当て
# Motor Driver 2 (U4) for Right Motor
PIN_RIGHT_FORWARD = 23 # 回路図のU4, IN2 (GPIO23)
PIN_RIGHT_BACKWARD = 18 # 回路図のU4, IN1 (GPIO18)

# Motor Driver 1 (U5) for Left Motor
PIN_LEFT_FORWARD = 24 # 回路図のU5, IN2 (GPIO24)
PIN_LEFT_BACKWARD = 13 # 回路図のU5, IN1 (GPIO13)

# BNO055センサーの初期化
try:
    bno = BNO055()
    bno.setup()
    print("BNO055 initialized successfully.")
except Exception as e:
    print(f"Error initializing BNO055: {e}")
    bno = None # 初期化に失敗した場合はNoneを設定

def setup_motors():
    """
    モーターを初期化し、Motorオブジェクトを返します。
    """
    try:
        factory = PiGPIOFactory()
        motor_left = Motor(forward=PIN_LEFT_FORWARD, backward=PIN_LEFT_BACKWARD, pin_factory=factory)
        motor_right = Motor(forward=PIN_RIGHT_FORWARD, backward=PIN_RIGHT_BACKWARD, pin_factory=factory)
        return motor_right, motor_left
    except Exception as e:
        print(f"An error occurred in setting motor_driver: {e}")
        csv.print('serious_error', f"An error occurred in setting motor_driver: {e}")
        return None, None

def stop_motors(motor_right, motor_left):
    """
    モーターを停止させます。
    徐々に減速して停止します。
    """
    if not (motor_right and motor_left):
        return

    current_power_r = motor_right.value
    current_power_l = motor_left.value

    # 現在のパワーから0へ徐々に減速
    steps = int(max(abs(current_power_r), abs(current_power_l)) / delta_power) + 1
    if steps == 0: # 既に停止している場合
        motor_right.value = 0.0
        motor_left.value = 0.0
        return

    for i in range(steps + 1):
        # 0からstepsまでで、powerが0になるように調整
        target_r = current_power_r * (1 - i / steps)
        target_l = current_power_l * (1 - i / steps)

        # 浮動小数点演算の誤差で非常に小さな値が残る可能性があるので、最終ステップでは完全に0にする
        if i == steps:
            target_r = 0.0
            target_l = 0.0

        motor_right.value = target_r
        motor_left.value = target_l
        sleep(0.05) # 短い間隔で更新

    motor_right.value = 0.0
    motor_left.value = 0.0
    time.sleep(0.1) # 完全に停止するのを待つ

def move(direction, power, duration):
    """
    指定された方向に、指定された強さで、指定された時間モーターを動かします。
    動き出しと停止時には徐々に加速・減速します。
    duration >= 2の場合、スタック検知と姿勢補正を行います。

    Args:
        direction (str): 'w'(前進), 's'(後退), 'a'(左旋回), 'd'(右旋回), 'q'(左モーターのみ前進), 'e'(右モーターのみ前進)
        power (float): モーターの強さ (0.0から1.0まで)
        duration (float): モーターを動かす時間 (秒) - 最大30秒
    Returns:
        int: スタックを検知した場合 1、それ以外 0
    """
    global bno # BNO055オブジェクトを参照

    if not (0.0 <= power <= 1.0):
        print("Error: powerは0.0から1.0の間で指定してください。")
        return 0
    if not (0.0 <= duration <= 30.0):
        print("Error: durationは0.0秒から30.0秒の間で指定してください。")
        return 0

    motor_right, motor_left = setup_motors()
    if not (motor_right and motor_left):
        print("モーターがセットアップされていません。")
        return 0

    # 加速フェーズ
    steps = int(power / delta_power) + 1
    acceleration_time = 0
    for i in range(steps + 1):
        current_step_power = min(i * delta_power, power) # 指定されたパワーを超えないように調整

        if direction == 'w': # 前進
            motor_right.value = current_step_power
            motor_left.value = current_step_power
        elif direction == 's': # 後退
            motor_right.value = -current_step_power
            motor_left.value = -current_step_power
        elif direction == 'a': # 左旋回 (右前、左後)
            motor_right.value = current_step_power
            motor_left.value = -current_step_power
        elif direction == 'd': # 右旋回 (左前、右後)
            motor_right.value = -current_step_power
            motor_left.value = current_step_power
        elif direction == 'q': # 左モーターのみ前進
            motor_right.value = 0.0
            motor_left.value = current_step_power
        elif direction == 'e': # 右モーターのみ前進
            motor_right.value = current_step_power
            motor_left.value = 0.0
        else:
            print("無効な方向が指定されました。")
            stop_motors(motor_right, motor_left)
            return 0
        sleep(0.025) # 短い間隔で更新
        acceleration_time += 0.025

    # 駆動フェーズ
    remaining_duration = max(0, duration - acceleration_time) # 加速にかかった時間を考慮
    
    is_stacked = 0 # スタック検知の結果 (0: スタックなし, 1: スタックあり)

    if remaining_duration > 0:
        # 指定パワーで駆動
        if direction == 'w':
            motor_right.value = power
            motor_left.value = power
        elif direction == 's':
            motor_right.value = -power
            motor_left.value = -power
        elif direction == 'a':
            motor_right.value = power
            motor_left.value = -power
        elif direction == 'd':
            motor_right.value = -power
            motor_left.value = power
        elif direction == 'q':
            motor_right.value = 0.0
            motor_left.value = power
        elif direction == 'e':
            motor_right.value = power
            motor_left.value = 0.0

        # durationが2秒以上の場合、スタック検知と姿勢補正を導入
        if duration >= 2 and bno:
            start_driving_time = time.time()
            while (time.time() - start_driving_time) < remaining_duration:
                # スタック検知
                is_current_segment_stacking = True
                for _ in range(5): # 1秒間 (0.2s * 5回) ジャイロ値をチェック
                    if not bno: # BNO055が利用できない場合はスキップ
                        is_current_segment_stacking = False
                        break
                    Gyro = bno.getVector(BNO055.VECTOR_GYROSCOPE)
                    # 旋回時と非旋回時で検知基準を変更
                    if direction in ['a', 'd']: # 旋回時
                        # 旋回方向への角速度が十分に小さい場合にスタックと判断
                        # Z軸が鉛直方向と仮定
                        if abs(Gyro[2]) > 0.75: # 旋回中であればZ軸の角速度は大きい
                            is_current_segment_stacking = False
                            break
                    else: # 非旋回時 (前進、後退、片輪駆動)
                        # 全体の角速度が小さい場合にスタックと判断
                        gyro_magnitude = np.sqrt(Gyro[0]**2 + Gyro[1]**2 + Gyro[2]**2)
                        if gyro_magnitude > 0.75:
                            is_current_segment_stacking = False
                            break
                    time.sleep(0.2) # 0.2秒待機

                if is_current_segment_stacking:
                    print("スタックを検知しました！")
                    csv.print('warning', 'stacking now!')
                    is_stacked = 1 # スタックフラグを立てる

                # 機体がひっくり返っているか検知して補正（スタック状態とは独立してチェック）
                try:
                    if bno and bno.getVector(BNO055.VECTOR_GRAVITY) is not None:
                        gravity_z = bno.getVector(BNO055.VECTOR_GRAVITY)[2]
                        if gravity_z > 0.5: # 閾値は調整が必要
                            print('機体がひっくり返っています！姿勢補正を開始します。')
                            csv.print('warning', 'muki_hantai')
                            accel_start_time = time.time()
                            while bno.getVector(BNO055.VECTOR_GRAVITY)[2] > 0.5 and (time.time() - accel_start_time) < 5:
                                motor_right.value = power
                                motor_left.value = power
                                time.sleep(0.5)
                                motor_right.value = 0.0
                                motor_left.value = 0.0 # 短く止めて再度確認
                                time.sleep(0.1)
                            if (time.time() - accel_start_time) >= 5:
                                print('5秒以内に元の向きに戻りませんでした。')
                                csv.print('warning', 'orientation_correction_failed')
                                # 姿勢補正失敗時の追加のリカバリーは、呼び出し元で判断できるように、ここでは実施しない
                            else:
                                print('姿勢が元の向きに戻りました。')
                                csv.print('msg', 'muki_naotta')
                                stop_motors(motor_right, motor_left)
                                start_driving_time = time.time() # 姿勢補正後、残り時間を再計算

                except Exception as e:
                    print(f"An error occurred while changing the orientation: {e}")
                    csv.print('error', f"An error occurred while changing the orientation: {e}")

                # 残り時間があれば駆動を続ける
                sleep(min(0.1, (start_driving_time + remaining_duration) - time.time())) # 細かくチェックしながら残り時間を待つ

    # 最終停止
    stop_motors(motor_right, motor_left)
    return is_stacked # スタック検知の結果を返す

def check_stuck(is_stacked):
    #スタック解除の動作を実行する
    try:
        # スタック検知時の処理
        if is_stacking == True:
            # GPIO5の出力を1にして、LED点灯
            for i in range(0,2):
                GPIO.output(5,1)
                time.sleep(0.5)
                GPIO.output(5,0)
                time.sleep(0.5)
            GPIO.output(5, 1)
        
            print("Stacking detected!")
            make_csv.print("warning", "Stacking detected!")

            # スタック解除のための動作
            motor.backward(motor_right, motor_left)  # 3秒後退
            time.sleep(3)
            motor.rightturn(motor_right, motor_left)  # 1秒右旋回
            time.sleep(1)
            motor.forward(motor_right, motor_left)  # 2秒前進
            time.sleep(2)
            motor.brake(motor_right, motor_left)  # 停止

            # GPIO17の出力を0にして、LED消灯
            GPIO.output(17, 0)
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred in stack check: {e}")
        make_csv.print("error", f"An error occurred in stack check: {e}")
