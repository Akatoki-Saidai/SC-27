# 新井

import RPi.GPIO as GPIO  # GPIOモジュールをインポート
from gpiozero import Motor
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import numpy as np

# from bno055 import BNO055 # BNO055を使う場合はコメント解除
# import make_csv as csv # CSV出力を使う場合はコメント解除

delta_power = 0.1 # スムーズな加速・減速のための刻み幅

# DCモータのピン設定
# 回路図に基づいたピン割り当て
# Motor Driver 2 (U4) for Right Motor
PIN_RIGHT_FORWARD = 23 # 回路図のU4, IN2 (GPIO23)
PIN_RIGHT_BACKWARD = 18 # 回路図のU4, IN1 (GPIO18)

# Motor Driver 1 (U5) for Left Motor
PIN_LEFT_FORWARD = 24 # 回路図のU5, IN2 (GPIO24)
PIN_LEFT_BACKWARD = 13 # 回路図のU5, IN1 (GPIO13)


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
        # csv.print('serious_error', f"An error occurred in setting motor_driver: {e}")
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

    Args:
        direction (str): 'w'(前進), 's'(後退), 'a'(左旋回), 'd'(右旋回), 'q'(左モーターのみ前進), 'e'(右モーターのみ前進)
        power (float): モーターの強さ (0.0から1.0まで)
        duration (float): モーターを動かす時間 (秒) - 最大30秒
    """
    if not (0.0 <= power <= 1.0):
        print("Error: powerは0.0から1.0の間で指定してください。")
        return
    if not (0.0 <= duration <= 30.0):
        print("Error: durationは0.0秒から30.0秒の間で指定してください。")
        return

    motor_right, motor_left = setup_motors()
    if not (motor_right and motor_left):
        print("モーターがセットアップされていません。")
        return

    # 徐々に加速
    steps = int(power / delta_power) + 1
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
            return
        sleep(0.05) # 短い間隔で更新

    # 指定された時間だけ駆動（加速に要した時間をdurationから引く場合は調整が必要）
    remaining_duration = max(0, duration - (steps * 0.05)) # 加速にかかった時間を考慮
    if remaining_duration > 0:
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
        sleep(remaining_duration)

    stop_motors(motor_right, motor_left)


'''
# BNO055を使用する場合にコメント解除してください。
# from bno055 import BNO055

def right_angle(bno, angle_deg, right, left):
    # csv.print('msg', f'motor: turn {angle_deg} deg to right')
    angle_rad = angle_deg * np.pi / 180
    start_time = time.time()
    prev_time = time.time()
    rot_angle = 0

    # だんだん加速
    # move('d', 1.0, 0) # 右旋回（パワー1.0、時間0秒）で徐々に加速
    # gyroセンサーで角度を監視しながら動作
    # BNO055の初期化とデータ取得ロジックが必要

    # ここにmove関数を使った右旋回の実装を記述
    # 例: move('d', power, duration) を繰り返して角度を調整
    # または、move関数を呼び出さずに直接right, leftのvalueを制御

    print(f"BNO055を使用する right_angle 関数は move 関数で直接置き換えられません。")
    print(f"角度制御ロジックを move 関数の内部に統合するか、")
    print(f"move 関数とBNO055の情報を組み合わせて再実装してください。")

    # だんだん減速
    # stop_motors(right, left)

def left_angle(bno, angle_deg, right, left):
    # csv.print('msg', f'motor: turn {angle_deg} deg to left')
    angle_rad = angle_deg * np.pi / 180
    start_time = time.time()
    prev_time = time.time()
    rot_angle = 0
    # csv.print('motor', [left.value, right.value])

    # だんだん加速
    # move('a', 1.0, 0) # 左旋回（パワー1.0、時間0秒）で徐々に加速
    # gyroセンサーで角度を監視しながら動作
    # BNO055の初期化とデータ取得ロジックが必要

    # ここにmove関数を使った左旋回の実装を記述
    # 例: move('a', power, duration) を繰り返して角度を調整
    # または、move関数を呼び出さずに直接right, leftのvalueを制御

    print(f"BNO055を使用する left_angle 関数は move 関数で直接置き換えられません。")
    print(f"角度制御ロジックを move 関数の内部に統合するか、")
    print(f"move 関数とBNO055の情報を組み合わせて再実装してください。")

    # だんだん減速
    # stop_motors(right, left)

def retreat_old(right, left):
    # この関数は move('s', power, duration) で置き換え可能です。
    # 既存のロジックを維持する場合はコメントを解除してください。
    for i in range(1, 2 + 1):
        # rightturn(right, left) は move('d', power, duration) で置き換え
        move('d', 1.0, 0.666) # 仮のパワーと時間
        stop_motors(right, left)
        # accel(right, left) は move('w', power, duration) で置き換え
        move('w', 1.0, 3) # 仮のパワーと時間
        stop_motors(right, left)
    # rightturn(right, left) は move('d', power, duration) で置き換え
    move('d', 1.0, 0.666) # 仮のパワーと時間
    stop_motors(right, left)

    # csv.print('motor', [-1, -1])
    # csv.print('msg', 'motor: accel')
'''
