# 桜井

import serial
import pynmea2
import time
from datetime import datetime, timedelta

port = "/dev/serial0"
baudrate = 9600
GPS_TIMEOUT = 15  # GPSデータ取得のタイムアウト時間（秒）

def get_gps_data():
    """
    緯度、経度、日本時間、曜日を抽出します。
    15秒間GPSデータが取得できなかった場合、処理を中断します。
    """
    last_gps_data_time = time.time()
    lat, lon = None, None
    jst_time_str = None

    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='replace')
                
                # GPSデータを受信したらタイムスタンプを更新
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    last_gps_data_time = time.time()
                    
                # タイムアウトチェック
                if time.time() - last_gps_data_time > GPS_TIMEOUT:
                    print(f"エラー: {GPS_TIMEOUT}秒以上GPSデータが取得できませんでした。処理を中断します。")
                    return None, None, None, None

                try:
                    msg = pynmea2.parse(line)

                    if isinstance(msg, pynmea2.types.talker.GGA):
                        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                            lat = msg.latitude
                            lon = msg.longitude
                            
                    if isinstance(msg, pynmea2.types.talker.RMC):
                        if msg.datestamp and msg.timestamp:
                            dt_utc = datetime.combine(msg.datestamp, msg.timestamp)
                            dt_jst = dt_utc + timedelta(hours=9)
                            jst_time_str = dt_jst.strftime('%Y-%m-%d %H:%M:%S')
                            
                    # 緯度、経度、日本時間の両方が取得できたら結果を返す
                    if lat is not None and lon is not None and jst_time_str is not None:
                        weekday = get_weekday_from_datetime_str(jst_time_str)
                        return lat, lon, jst_time_str, weekday

                except pynmea2.ParseError:
                    continue
                    
    except serial.SerialException as e:
        print(f"シリアルポートエラー: {e}")
        return None, None, None, None

def get_weekday_from_datetime_str(datetime_str):
    """
    日時文字列から曜日を抽出します。
    """
    try:
        dt_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        weekday = dt_object.strftime('%A')
        return weekday
    except ValueError:
        print(f"エラー: 無効な日時文字列のフォーマットです: {datetime_str}")
        return None

# 使用例
if __name__ == "__main__":
    print("GPSデータの取得を開始します。")
    latitude, longitude, japanese_time, day_of_week = get_gps_data()

    if latitude is not None and longitude is not None:
        print(f"緯度: {latitude}")
        print(f"経度: {longitude}")
        print(f"日本時間: {japanese_time}")
        print(f"曜日: {day_of_week}")
    else:
        print("GPSデータの取得に失敗しました。")
