# 桜井

import gps

def main():
    """
    gps.py の関数を実行し、緯度、経度、日本時間、曜日を表示します。
    """
    print("GPSデータ取得を開始します...")

    # 緯度と経度を取得
    latitude, longitude = gps.idokeido()
    if latitude is not None and longitude is not None:
        print(f"緯度: {latitude}, 経度: {longitude}")
    else:
        print("緯度と経度の取得に失敗しました。")

    print("\n日本時間と曜日を取得します...")

    # 日本時間を取得
    japan_time_str = gps.zikan()
    if japan_time_str:
        print(f"日本時間: {japan_time_str}")

        # 曜日を取得
        day_of_week = gps.youbi(japan_time_str)
        if day_of_week:
            print(f"曜日: {day_of_week}")
        else:
            print("曜日の取得に失敗しました。")
    else:
        print("日本時間の取得に失敗しました。")

if __name__ == "__main__":
    main()
