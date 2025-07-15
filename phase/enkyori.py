import time
import motordrive
import bno
import gps

##################################################
#                      入力                      #
##################################################
# モータを起動させたときの機体の回転速度ω[rad/s]
omega = math.pi / 2  # rad/s

# WGS84楕円体のパラメータを定義
a = 6378137.0
b = 6356752.314245
f = (a - b) / a

##################################################
#                      入力                      #
##################################################
# 能代宇宙広場 (ゴール地点の例)
# 緯度経度をWGS84楕円体に基づいて設定
goal_lat, goal_lon = 40.14389563045866, 139.98732883121738 # 緯度，経度

# pyprojを使ってWGS84楕円体に基づく投影を定義
wgs84 = pyproj.Proj('+proj=latlong +ellps=WGS84')

# 初期位置の緯度経度を取得
start_lat, start_lon = gps.get_latitude(), gps.get_longitude()

# 移動していない判定のカウンター
no_movement_count = 0
#遠距離フェーズ最初の5秒前進を実行
motordrive.move(w, 1.0, 5.0)
motordrive.stop()
time.sleep(1)

#5秒進んだ先での現在位置を得る
current_lat = gps.get_latitude()
current_lon = gps.get_longitude()

phase = 2
            if phase != 2:
                phase = 2
            elif phase == 2:
                print(current_lat, current_lon)  # 現在位置

                # 距離と角度を計算し、表示
                distance_to_goal, angle_to_goal = gps.calculate_distance_and_angle(current_lat, current_lon, start_lat, start_lon)
                print("現在地からゴール地点までの距離:", distance_to_goal, "メートル")
                print("theta_for_goal°:", str(angle_to_goal * 180 / math.pi) + "°")

                # 移動していない判定
                if distance_to_goal == 2323232323:  # calculate_distance_and_angle関数で移動していないと判定された場合
                    no_movement_count += 1
                    print("移動していない判定:", no_movement_count, "回")
                    if no_movement_count >= 23:
                        print("移動していない判定が23回に達しました。強制的に近距離フェーズに移行します。")
                        break  # whileループを抜けて近距離フェーズに移行
                    else:
                        no_movement_count = 0  # 移動が検出されたらカウンターをリセット

                # 進行方向を決定
                if angle_to_goal > 0:
                    print("進行方向に対して左方向にゴールがあります")
                    # ゴールへの角度に比例した時間だけ左回転
                    rotation_time = angle_to_goal / omega  # 回転時間 = 角度 / 回転速度
                    # 左に計算された時間だけ回転
                    motordrive.move(a, 1.0, rotation_time)

                    motordrive.stop()
                    time.sleep(1)

                else:
                    print("進行方向に対して右方向にゴールがあります")
                    # ゴールへの角度に比例した時間だけ右回転
                    rotation_time = abs(angle_to_goal) / omega  # 回転時間 = 角度 / 回転速度
                    # 右に計算された時間だけ回転
                    motordrive.move(d, 1.0, rotation_time)

                    motordrive.stop()
                    time.sleep(1)

                ###5秒前進 & スタック検知###
                is_stacked = motordrive.move(w, 1.0, 5.0)

                #スタック検知がyesの場合
                motordrive.check_stuck(is_stacked)
                #スタックしたときの処理が行われる
                
                #モーター止める
                motordrive.stop()
                time.sleep(1)

                    # 機体がひっくり返ってたら回る
                try:
                    accel_start_time = time.time()
                    if 0 < bno.getVector(BNO055.VECTOR_GRAVITY)[2]:
                        while 0 < bno.getVector(BNO055.VECTOR_GRAVITY)[2] and time.time()-accel_start_time < 5:
                            print('muki_hantai')
                            make_csv.print('warning', 'muki_hantai')
                            motordrive.move(w, 1.0, 0.5)
                    else:
                        if time.time()-accel_start_time >= 5:
                        # 5秒以内に元の向きに戻らなかった場合
                            motordrive.move(d, 1.0, 0.5)
                            time.sleep(0.5)
                            motordrive.move(a, 1.0, 0.5)
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
                current_lat = gps.get_latitude()
                current_lon = gps.get_longitude()

                # ゴールの10 m以内に到達したらループを抜け近距離フェーズへ
                if distance_to_goal <= 10:
                    print("近距離フェーズに移行")
                    phase = 3
                    break
