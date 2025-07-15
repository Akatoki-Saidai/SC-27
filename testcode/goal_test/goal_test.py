# camera
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO


# 同じディレクトリに重みを置く
pt_path = "./SC-25_yolo_ver2.pt"

if __name__ == '__main__':
    try:
        # カメラをセットアップ
        picam2 = Picamera2()
        config = picam2.create_preview_configuration({"format": 'XRGB8888'})
        # config = picam2.create_preview_configuration({"format": 'XRGB8888', "size": (480, 320)}, transform=Transform(hflip=1, vflip=1))  # カメラが逆さの場合はこれで修正
        picam2.configure(config)

        # カメラを起動
        picam2.start()
    
    except Exception as e:
        print(f"An error occured in setup camera: {e}")

    while True:
        try:
            photo_distance = input("how distance?")
            # カメラモジュールから画像を取得
            frame = picam2.capture_array()
    
            # 画像がRGBAの場合はRGBに変換
            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # BGRA → BGR(RGBと等価)

            # 写真撮影
            photo_time = int(time.time())
            photo_filename = f"photo_{photo_time}_{photo_distance}.jpg"
            cv2.imwrite(f"./goal_photo/{photo_filename}", frame)
            print(f"photo taked: {photo_filename}")
            
            # 推論
            model = YOLO(pt_path)
            results = model(f"./goal_photo/{photo_filename}",save=True)
            
            # 結果表示
            cv2.imshow('kekka', frame)
            time.sleep(0.5)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print("pressed q interrupted")

        except Exception as e:
            print(f"An error occured in getting camera frame: {e}")
