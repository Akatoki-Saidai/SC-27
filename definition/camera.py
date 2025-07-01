# 神田，吉澤、宍倉

# camera
import os
import time
from ultralytics import YOLO
import cv2
import numpy as np
from picamera2 import Picamera2 

# 同じディレクトリに重みを置く
pt_path = "./SC-27_yolo_ver1.pt"

class Camera:
    def __init__(self):
        """カメラのセットアップ"""
        try:
            self._picam2 = Picamera2()
            config = self._picam2.create_preview_configuration({"format": 'XRGB8888', "size": (320, 240)})
            self._picam2.configure(config)  # カメラの初期設定
        except Exception as e:
            print(f"An error occured in setup camera: {e}")
    
    def start(self):
        """カメラを起動"""
        try:
            self._picam2.start()
        except Exception as e:
            print(f"An error occured in starting camera {e}")

    def yolo_detect(self, frame):
        """YOLOによる画像認識でカラーコーンを探す"""
        try:
            yolo_xylist = None
            center_x = 0
            
            # YOLOv10nモデルをロード
            model = YOLO(pt_path)
            # 推論
            yolo_results = model.predict(frame, save = False, show = False)
            # print(type(yolo_results))
            # print(yolo_results)

            confidence_best = 0
            # 最も信頼性の高いBounding Boxを取得
            yolo_result = yolo_results[0]
            # print("yolo_result: ",yolo_result)
            # バウンディングボックス情報を NumPy 配列で取得
            Bounding_box = yolo_result.boxes.xyxy.numpy()
            # print("Bounding_box: ", Bounding_box)
            confidences = yolo_result.boxes.conf.numpy()
            # print("confidences: ", confidences)

            if len(Bounding_box) == 0:
                print("No objects detected.")

            else:
                for i in range(len(Bounding_box)):
                    confidence = confidences[i]
                    if confidence < confidence_best:
                        continue
                    else:
                        confidence_best = confidence
                    xmin, ymin, xmax, ymax = Bounding_box[i]
                    

                    '''
                    Bounding_box = yolo_results[0].boxes.pandas()
                    # print(Bounding_box)
                    for i in range(len(Bounding_box)):
                        confidence = Bounding_box.confidence[i]
                        # name = Bounding_box.name[i]
                        if confidence < confidence_best:
                            continue
                        else:
                            confidence_best = confidence
                        xmin = Bounding_box.xmin[i]
                        ymin = Bounding_box.ymin[i]
                        xmax = Bounding_box.xmax[i]
                        ymax = Bounding_box.ymax[i]
                    '''
                
                center_x = int(xmin + (xmax - xmin) / 2)
                yolo_xylist = [xmin, ymin, xmax, ymax, confidence]

            return yolo_xylist, center_x
        except Exception as e:
            print(f"An error occured in reasoning by yolo: {e}")


    def red_detect(self, frame):
        """画像に含まれるカラーコーンに近い赤色を探す"""
        try:
            # HSV色空間に変換
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 赤色のHSVの値域1
            hsv_min = np.array([0, 117, 104])
            hsv_max = np.array([11, 255, 255])
            mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

            # 赤色のHSVの値域2
            hsv_min = np.array([169, 117, 104])
            hsv_max = np.array([179, 255, 255])
            mask2 = cv2.inRange(hsv, hsv_min, hsv_max)

            return mask1 + mask2
        except Exception as e:
            print(f"An error occured in masking red: {e}")
    
    def analyze_red(self, mask):
        """red_detectで探した赤色のエリアの位置と大きさを分析"""
        try:
            area = 0
            center_x = 0
            center_y = 0
            
            # 画像の中にある領域を検出する
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if 0 < len(contours):
                # 輪郭群の中の最大の輪郭を取得する
                biggest_contour = max(contours, key=cv2.contourArea)

                # 最大の領域の外接矩形を取得する
                rect = cv2.boundingRect(biggest_contour)

                # #最大の領域の中心座標を取得する
                center_x = (rect[0] + rect[2] // 2)
                center_y = (rect[1] + rect[3] // 2)

                # 最大の領域の面積を取得する-
                area = cv2.contourArea(biggest_contour)

                # cv2.putText(frame, str(center_x), (center_x, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1)

            return area, center_x, center_y, rect
        except Exception as e:
            print(f"An error occured i analyzing red: {e}")


    def judge_cone(self, frame):
        """画像認識によるカラーコーンの位置と，赤色検出によるカラーコーンの大きさから進むべき方向を決定
        
        0:不明, 1:直進, 2:右へ, 3:左へ, 4:コーンが近い(ゴール)
        """
        try:
            yolo_xylist = None
            frame_center_x = frame.shape[1] // 2

            try:
                # 赤色検出
                mask = self.red_detect(frame)
                red_area, red_center_x, _red_y, red_rect = self.analyze_red(mask)
                print(f"red area: {red_area}")
            except Exception as e:
                print(f"An error occured in analize_red: {e}")

            colorcone_x = 0
            # 中心座標のx座標が画像の中心より大きいか小さいか判定
            if red_area > 7000:
                print("Close enough to red")
                camera_order = 4

            elif red_area > 3500:
                print("judge red object by color")

                colorcone_x = red_center_x - frame_center_x
                if -50 <= colorcone_x <= 50:
                    print("The red object is in the center")#直進
                    camera_order = 1
                elif colorcone_x > 50:
                    print("The red object is in the right")#右へ
                    camera_order = 2
                elif colorcone_x < -50:
                    print("The red object is in the left")#左へ
                    camera_order = 3
                else:
                    print("The red object is too minimum")
                    camera_order = 0
                

            elif red_area > 5:
                print("judge red object by yolo")

                try:
                    # YOLO
                    yolo_xylist, yolo_center_x = self.yolo_detect(frame)
                    print(f"yolo_xylist: {yolo_xylist}, yolo_center_x: {yolo_center_x}")
                except Exception as e:
                    print(f"An error occured in yolo_detect: {e}")

                colorcone_x = yolo_center_x - frame_center_x

                if -50 <= colorcone_x <= 50:
                    print("The yolo object is in the center")#直進
                    camera_order = 1
                elif colorcone_x > 50:
                    print("The yolo object is in the right")#右へ
                    camera_order = 2
                elif colorcone_x < -50:
                    print("The yolo object is in the left")#左へ
                    camera_order = 3
                else:
                    print("The yolo object is too minimum")
                    camera_order = 0
            
            else:
                print("Colorcone is None")
                camera_order = 0
            
            if yolo_xylist is not None:
                # Bounding Box描画
                cv2.rectangle(frame, (int(yolo_xylist[0]), int(yolo_xylist[1])), (int(yolo_xylist[2]), int(yolo_xylist[3])), (255, 0, 0), 2)
                cv2.putText(frame, str(yolo_xylist[4]), (int(yolo_xylist[0]), int(yolo_xylist[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0))

                # 面積表示
                cv2.putText(frame, str(red_area), (int(yolo_xylist[0]), int(yolo_xylist[3] - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255))

                # red_result = cv2.drawContours(mask, [biggest_contour], -1, (0, 255, 0), 2)
            
            else:
                # 最大の領域の長方形を表示する
                cv2.rectangle(frame, (red_rect[0], red_rect[1]), (red_rect[0] + red_rect[2], red_rect[1] + red_rect[3]), (0, 0, 255), 2)

                # 最大の領域の面積を表示する
                cv2.putText(frame, str(red_area), (red_rect[0], red_rect[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

            return frame, camera_order
        
        except Exception as e:
            print(f"An error occured in judging colorcone: {e}")
    
    
    def result(self, *, show = False, save=True):
        """画像認識及び赤色検出を行い，進むべき方向を返す
        
        返り値: 0:不明, 1:直進, 2:右へ, 3:左へ, 4:コーンが近い(ゴール)    
        show=Trueなら撮影した画像をプレビューウィンドウに表示    
        save=Trueなら撮影した画像をjpgファイルとして保存 (GUIに表示するため)    
        """
        try:
            frame = self._picam2.capture_array()
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            
            # RGBに変換
            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # BGRA → BGR（RGBと等価）            
            
            # 判断
            try:
                frame, camera_order = self.judge_cone(frame)

            except Exception as e:
                print(f"An error occured in judgement: {e}")

            # 結果表示
            try:
                if (show == True):
                    cv2.imshow('kekka', frame)
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        print('q interrupted direction by camera')
            except Exception as e:
                print(f"An error occured interrupt q: {e}")
            
            # 画像を保存
            try:
                if (save == True):
                    cv2.imwrite('camera_temp.jpg', frame)
                    os.rename('camera_temp.jpg', 'camera.jpg')
            except Exception as e:
                print(f"An error occured in saving camera jpg: {e}")

            return camera_order
        
        except Exception as e:
            print(f"An error occured in result: {e}")
    

if __name__ == '__main__':
    cam = Camera()  # カメラをセットアップ
    cam.start()  # カメラにを起動 (重くなるので使用する直前までstartしないこと)

    while True:
        camera_order = cam.result(0, show=True)  # 画像認識をしてコーンを検出 (show=Trueなら撮影した画像のプレビューを表示)
        print(f"camera_order; {camera_order=}")
        time.sleep(1)
