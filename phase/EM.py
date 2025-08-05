import serial
import time
import math
import warnings
import RPi.GPIO as GPIO
from ultralytics import YOLO
import cv2
import numpy as np
from picamera2 import Picamera2

# センサ類import
from bno055 import BNO055
from bme280 import BME280Sensor
import motordrive
import gps
import make_csv
import camera as cam
import hcsr04 as ultrasonic


# --------------------------- #
#             入力            #
# --------------------------- #
# モータを起動させたときの機体の回転速度ω[rad/s]
omega = math.pi / 2  # rad/s

# 初期位置の緯度経度を取得
start_lat, start_lon = gps.idokeido()

# 移動していない判定のカウンター
no_movement_count = 0

# 同じディレクトリに重みを置く
pt_path = "./SC-27_yolo_ver1.pt"

# 途中でカメラを起動するためのフラグ
cam_flag = False

def main():

    # BNO055とBME280のインスタンス生成
    bno = BNO055()
    bme = BME280Sensor(bus_number=1)

    # BNO055初期化
    if not bno.begin():
        print("Failed bno initialize")
    # 外部クリスタル使用
    bno.set_external_crystal(True)

    # 温湿度気圧センサセットアップ
    try:
        for i in range(20):
            try:
                bme.read_data()
            except Exception as e:
                print(f"An error occurred during empty measurement in BME: {e}")
                make_csv.print('msg', f"An error occurred during empty measurement in BME: {e}")

        pressure = bme.pressure()
        make_csv.print("alt_base_press", pressure)
        baseline = bme.baseline()
        make_csv.print("msg", "all clear(bme280)")

    except Exception as e:
        print(f"An error occurred in setting bme object: {e}")
        make_csv.print('serious_error', f"An error occurred in setting bme280 object: {e}")
        return

    # 9軸センサセットアップ
    try:
        if not bno.begin():
            print("Error initializing device")
            make_csv.print("serious_error", "Error initializing device")
            return
        time.sleep(1)
        bno.set_external_crystal(True)
        make_csv.print("msg", "all clear(bno055)")

    except Exception as e:
        print(f"An error occurred in setting bno055: {e}")
        make_csv.print("serious_error", f"An error occurred in setting bno055: {e}")
        return

    #落下フェーズの終わりから開始
    phase = 0

    try:
        print("セットアップ完了")
        make_csv.print("msg", "セットアップ完了")
        make_csv.print("phase", 0)

        # ここから無限ループ
        while True:

            # --------------------------- #
            #        待機フェーズ         #
            # --------------------------- #
            if phase == 0:
                try:
                    temperature = bme.temperature()
                    pressure = bme.pressure()
                    # humidity = bme.humidity()
                    time.sleep(1.0)
                    alt_1 = bme.altitude(pressure, qnh=baseline)
                    print(f"alt_1: {alt_1}")
                    time.sleep(0.5)

                    if  alt_1 >= 10:
                        phase = 1
                        print("Go to falling phase")
                        make_csv.print("msg", "Go to falling phase")
                        make_csv.print("phase", 1)
                    else:
                        print("落下を検知できませんでした")

                    time.sleep(1)

                except Exception as e:
                    print(f"An error occurred in phase 0: {e}")
                    make_csv.print("error", f"An error occurred in phase 0: {e}")


            # --------------------------- #
            #        落下フェーズ         #
            # --------------------------- #
            elif phase == 1:
                try:
                    consecutive_count = 0

                    for _ in range(10):
                        pressure = bme.pressure()
                        alt_2 = bme.altitude(pressure, qnh=baseline)

                        linear_accel = bno.linear_acceleration()
                        accel_x, accel_y, accel_z = linear_accel

                        print(f"accel_x: {accel_x}, accel_y: {accel_y}, accel_z: {accel_z}")

                        if abs(accel_x) + abs(accel_y) + abs(accel_z) < 0.1 and alt_2 <= 0.1:
                            consecutive_count += 1
                            print(f"落下終了の条件を満たしました: {consecutive_count}/5")
                            make_csv.print("msg", f"落下終了の条件を満たしました: {consecutive_count}/5")
                            time.sleep(1)
                        else:
                            consecutive_count = 0
                            print(f"落下終了の条件を満たしませんでした")
                            time.sleep(0.5)

                        if consecutive_count >= 5:
                            make_csv.print("msg","ニクロム線切断開始")
                            print("ニクロム線切断開始")

                            #ニクロム線切断
                            pin = 16
                            '''
                            GPIO.setmode(GPIO.BCM)
                            GPIO.setup(pin, GPIO.OUT)
                            GPIO.output(pin, 1)
                            time.sleep(5)
                            GPIO.output(pin, 0)
                            '''
                            make_csv.print("msg","ニクロム線切断完了")
                            print("ニクロム線切断完了")
                            
                            #ここにニクロム線を切るコード
                            #ニクロム線を切ったあと
                            #遠距離フェーズ最初の5秒前進を実行
                            motordrive.move('w', 1.0, 5.0)
                            motordrive.stop()
                            time.sleep(1)

                            #5秒進んだ先での現在位置を得る
                            current_lat, current_lon = gps.idokeido()

                            # FutureWarningを抑制
                            warnings.filterwarnings("ignore", category=FutureWarning)

                            phase = 2

                except Exception as e:
                    print(f"An error occurred in phase 1: {e}")
                    make_csv.print("error", f"An error occurred in phase 1: {e}")


            # --------------------------- #
            #        遠距離フェーズ       #
            # --------------------------- #
            elif phase == 2:
                print(current_lat, current_lon)  # 現在位置

                # 距離と角度を計算し、表示
                distance_to_goal, angle_to_goal = gps.calculate_distance_and_angle(current_lat, current_lon, start_lat, start_lon, goal_lat, goal_lon)
                print("現在地からゴール地点までの距離:", distance_to_goal, "メートル")
                print("theta_for_goal°:", str(angle_to_goal * 180 / math.pi) + "°")

                # 移動していない判定
                if distance_to_goal == 2323232323:  # gps.calculate_distance_and_angle関数で移動していないと判定された場合
                    no_movement_count += 1
                    print("移動していない判定:", no_movement_count, "回")
                    if no_movement_count >= 23:
                        print("移動していない判定が23回に達しました。強制的に近距離フェーズに移行します。")
                        phase = 3  # 近距離フェーズに移行
                else:
                    no_movement_count = 0  # 移動が検出されたらカウンターをリセット

                    # 進行方向を決定
                    if angle_to_goal > 0:
                        print("進行方向に対して左方向にゴールがあります")
                        # ゴールへの角度に比例した時間だけ左回転
                        rotation_time = angle_to_goal / omega  # 回転時間 = 角度 / 回転速度
                        # 左に計算された時間だけ回転
                        motordrive.move('a', 1.0, rotation_time)

                        motordrive.stop()
                        time.sleep(1)

                    else:
                        print("進行方向に対して右方向にゴールがあります")
                        # ゴールへの角度に比例した時間だけ右回転
                        rotation_time = abs(angle_to_goal) / omega  # 回転時間 = 角度 / 回転速度
                        # 右に計算された時間だけ回転
                        motordrive.move('d', 1.0, rotation_time)

                        motordrive.stop()
                        time.sleep(1)

                    ###5秒前進 & スタック検知###
                    is_stacked = motordrive.move('w', 1.0, 5.0)

                    #スタック検知がyesの場合
                    motordrive.check_stuck(is_stacked)
                    #スタックしたときの処理が行われる
                    
                    #モーター止める
                    motordrive.stop()
                    time.sleep(1)

                        # 機体がひっくり返ってたら回る
                    try:
                        accel_start_time = time.time()
                        if 0 < bno.gravity()[2]:
                            while 0 < bno.gravity()[2] and time.time()-accel_start_time < 5:
                                print('muki_hantai')
                                make_csv.print('warning', 'muki_hantai')
                                motordrive.move('w', 1.0, 0.5)
                        else:
                            if time.time()-accel_start_time >= 5:
                            # 5秒以内に元の向きに戻らなかった場合
                                motordrive.move('d', 1.0, 0.5)
                                time.sleep(0.5)
                                motordrive.move('a', 1.0, 0.5)
                                time.sleep(0.5)
                                continue
                            else:
                                print('muki_naotta')
                                make_csv.print('msg', 'muki_naotta')
                                motordrive.stop()
                    except Exception as e:
                        print(f"An error occured while changing the orientation: {e}")
                        make_csv.print('error', f"An error occured while changing the orientation: {e}")

                # 現在地を更新
                current_lat, current_lon = gps.idokeido()

                # ゴールの10 m以内に到達したらループを抜け近距離フェーズへ
                if distance_to_goal <= 10:
                    print("近距離フェーズに移行")
                    phase = 3


            # --------------------------- #
            #        近距離フェーズ       #
            # --------------------------- #
            elif phase == 3:
                try:
                    if cam_frag == False:
                        picam2 = Picamera2()
                        config = picam2.create_preview_configuration({"format": 'XRGB8888', "size": (1024, 768)})
                        picam2.configure(config)  # カメラの初期設定
                        picam2.start()
                        cam_frag = True

                    # フレームを取得
                    frame = picam2.capture_array()
                    frame = cv2.rotate(frame, cv2.ROTATE_180)

                    try:
                        relative_cone_x = 0
                        frame, relative_cone_x, camera_order = cam.judge_cone(frame)
                    except Exception as e:
                        print(f"An error occured in judging relative_cone : {e}")

                    # 結果表示
                    cv2.imshow('kekka', frame)
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        print('q interrupted direction by camera')
                        continue

                    # 結果に応じてモーターを駆動
                    # 120度で1/3回転なので，1秒の1/3で0.666...秒が120度分
                    rotation_time = abs(relative_cone_x) / 120 * (1/3)  # 1秒で360度回転と仮定

                    if camera_order == 0:
                        # コーンが見つからなかったとき
                        motordrive.move('d', 1.0, 0.2)
                        # あとでmotordriveを確認する
                        # motordrive.stop()
                        time.sleep(0.8)

                    elif camera_order == 1:
                        # コーンが正面にあったとき
                        motordrive.move('w', 1.0, 0.5)
                        time.sleep(0.5)

                    elif camera_order == 2:
                        # コーンが右にあったとき
                        motordrive.move('d', 1.0, rotation_time)
                        time.sleep(0.5)

                    elif camera_order == 3:
                        # コーンが左にあったとき
                        motordrive.move('a', 1.0, rotation_time)
                        time.sleep(0.5)

                    elif camera_order == 4:
                        # コーンが十分に大きく見えるとき，ゴールフェーズへ
                        # あとでここに距離センサのコードを用意する
                        goal_distance = ultrasonic.distance()
                        print(f"goal_distance: {goal_distance} cm")
                        if goal_distance < 60:
                            motordrive.move('w', 0.8, 0.1)
                            phase = 4
                            print("ended short phase")
                
                except Exception as e:
                    print(f"An error occured in short phase: {e}")


            # --------------------------- #
            #        ゴールフェーズ       #
            # --------------------------- #
            elif phase == 4:
                try:
                    pass
                    print("goal goal goal")
                
                except Exception as e:
                    print(f"An error occured in goal phase: {e}")
            
    except Exception as e:
        print(f"遠距離フェーズでエラーが発生: {e}")

if __name__ == "__main__":
    main()
