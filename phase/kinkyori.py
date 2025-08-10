# definitionファイル内から，当フェーズを完成させるために必要なものをまずimportして，フローチャートを満たすようにコードを書いてほしい．

import time
from ultralytics import YOLO
import cv2
import numpy as np

import camera as cam
import motordrive
import bno
import hcsr04 as ultrasonic


# 同じディレクトリに重みを置く
pt_path = "./SC-27_yolo_ver1.pt"

# 途中でカメラを起動するためのフラグ
cam_frag =False


def main():

    picam2 = Picamera2()
    config = picam2.create_preview_configuration({"format": 'XRGB8888', "size": (640, 480)})
    picam2.configure(config)  # カメラの初期設定

    while True:
        
        # --------------------------- #
        #        待機フェーズ         #
        # --------------------------- #
        try:
            if phase == 0:
                #フェーズ0(スターク)の処理
                phase = 1
        except Exception as e:
            print(f"An error occured in waiting phase: {e}")
    

        # --------------------------- #
        #        落下フェーズ         #
        # --------------------------- #
        try:
            if phase == 1:
                #フェーズ1(コブラ)の処理
                phase = 2
        except Exception as e:
            print(f"An error occured in falling phase: {e}")

        # --------------------------- #
        #        遠距離フェーズ       #
        # --------------------------- #
        try:
            if phase == 2:
                #フェーズ2(ドラゴン)の処理
                phase = 3
        except Exception as e:
            print(f"An error occured in long phase: {e}")


        try:

            if phase == 2:
                #フェーズ3(ラピッド)の処理

                if cam_frag == False:
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
                    motordrive.stop()
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

            # フェーズ4(ブラックホール)の処理
        try:
            if phase == 4:
                pass
                print("goal goal goal")
            
        except Exception as e:
            print(f"An error occured in goal phase: {e}")

