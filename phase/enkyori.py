import time
import motordrive
import bno

            elif phase == 2:
                print(current_lat, current_lon)  # 現在位置

                # 距離と角度を計算し、表示
                distance_to_goal, angle_to_goal = calculate_distance_and_angle(current_lat, current_lon, start_lat, start_lon)
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
                
                motordrive.stop()
                #モーター止める

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
                current_lat = get_latitude()
                current_lon = get_longitude()

                # ゴールの10 m以内に到達したらループを抜け近距離フェーズへ
                if distance_to_goal <= 10:
                    print("近距離フェーズに移行")
                    phase = 3
                    break
