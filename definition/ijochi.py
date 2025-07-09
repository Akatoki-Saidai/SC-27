def ijochi(sensor_name, value):
# ここから先は消してかまいません．
    correct_values = []
    if sensor_name == "temperature":
        for val in value: # valueがリストの場合、各要素をループで処理
            if 0 <= val <= 100:  # 例: 温度が0〜100の範囲なら正常
                correct_values.append(val)
            else:
                print(f"異常値検出: センサー'{sensor_name}', 値'{val}'")
                # ここで異常値に対する具体的な処理（例: Noneを追加、デフォルト値を設定など）
                # correct_values.append(None)
    elif sensor_name == "pressure":
        for val in value:
            if 500 <= val <= 1500: # 例: 圧力が500〜1500の範囲なら正常
                correct_values.append(val)
            else:
                print(f"異常値検出: センサー'{sensor_name}', 値'{val}'")
                # correct_values.append(None)
    # その他のセンサーの処理...
    return correct_values

# 使用例
temperature_data = [20, 25, 105, 30, -5, 22]
corrected_temps = ijochi("temperature", temperature_data)
print(f"補正された温度データ: {corrected_temps}")

pressure_data = [800, 1200, 450, 1000]
corrected_pressures = ijochi("pressure", pressure_data)
print(f"補正された圧力データ: {corrected_pressures}")
