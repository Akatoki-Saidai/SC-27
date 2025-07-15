import serial
import pynmea2
import time
from datetime import datetime, timedelta

port = "/dev/serial0"
baudrate = 9600

def idokeido():
    """
    緯度と経度を抽出します
    一定時間（15秒）GPSデータが取得できなかったらNoneを返します
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            start_time = time.time()
            while (time.time() - start_time) < 15:  # 15秒間試行
                line = ser.readline().decode('ascii', errors='replace')
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    try:
                        msg = pynmea2.parse(line)
                        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                            lat = msg.latitude
                            lon = msg.longitude
                            return lat, lon
                    except pynmea2.ParseError:
                        continue
            print("idokeido: 15秒以内にGPSデータが取得できませんでした。")
            return None, None
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None, None

def zikan():
    """
    日本時間を抽出します
    一定時間（15秒）GPSデータが取得できなかったらNoneを返します
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            start_time = time.time()
            while (time.time() - start_time) < 15:  # 15秒間試行
                line = ser.readline().decode('ascii', errors='replace')
                if line.startswith('$GPRMC'):
                    try:
                        msg = pynmea2.parse(line)
                        if msg.datestamp and msg.timestamp:
                            dt_utc = datetime.combine(msg.datestamp, msg.timestamp)
                            dt_jst = dt_utc + timedelta(hours=9)
                            return dt_jst.strftime('%Y-%m-%d %H:%M:%S')
                    except pynmea2.ParseError:
                        continue
            print("zikan: 15秒以内にGPSデータが取得できませんでした。")
            return None
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None

def youbi(datetime_str):
    """
    曜日を抽出します
    """
    try:
        # 文字列を datetime オブジェクトに変換
        dt_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        weekday = dt_object.strftime('%A')
        return weekday
    except ValueError:
        print(f"エラー: 無効な日時文字列のフォーマットです: {datetime_str}")
        return None

