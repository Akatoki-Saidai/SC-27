import gps

# 使用例
if __name__ == '__main__':
    print("緯度経度を取得中...")
    latitude, longitude = gps.idokeido()
    if latitude is not None and longitude is not None:
        print(f"緯度: {latitude}, 経度: {longitude}")
    else:
        print("緯度経度の取得に失敗しました。")


    print("\n日本時間を取得中...")
    japan_time = gps.zikan()
    if japan_time is not None:
        print(f"日本時間: {japan_time}")
        print("\n曜日を抽出中...")
        weekday_result = gps.youbi(japan_time)
        if weekday_result is not None:
            print(f"曜日: {weekday_result}")
        else:
            print("曜日の抽出に失敗しました。")
    else:
        print("日本時間の取得に失敗しました。")
    print("全てのデータを表示")
    while True:
        gps.zenbu()
        pass

