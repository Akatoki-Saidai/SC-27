import serial
import pynmea2
import time
from datetime import datetime, timedelta
import pyproj
import math

port = "/dev/serial0"
baudrate = 38400

goal_lat, goal_lon = 40.142661833333335, 139.9876495 # 能代宇宙広場 (ゴール地点)

# pyprojを使ってWGS84楕円体に基づく投影を定義
wgs84 = pyproj.CRS('EPSG:4326')
utm = pyproj.CRS('+proj=utm +zone=54 +ellps=WGS84')
transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)


class GpsManager:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.latitude = None
        self.longitude = None
        self.timestamp_jst = None
        
        # UART開始
        if self.ser is None or not self.ser.is_open:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                print("Successfully connected to serial port.")
            except serial.SerialException as e:
                print(f"Failed to connect to serial port: {e}")
                self.ser = None

    def update(self):
        # UARTバッファを全て読み込み、最新に更新
        if not self.ser:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                print("Successfully reconnected to serial port.")
            except serial.SerialException as e:
                print(f"Failed to connect to serial port: {e}")
                self.ser = None
            if not self.ser:
                return

        try:
            # バッファのデータ全て読み込み
            if self.ser.in_waiting > 0:
                buffer = self.ser.read(self.ser.in_waiting).decode('ascii', errors='replace')
                line_list = buffer.split('\n')

                temp_lat = None
                temp_lon = None
                temp_dt_jst = None
                
                for line in line_list:
                    try:
                        msg = pynmea2.parse(line)

                        # 有効な緯度経度データかチェック
                        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude') and msg.latitude != 0.0:
                            temp_lat = msg.latitude
                            temp_lon = msg.longitude
                        
                        # 日付と時刻を含むRMCセンテンスから情報を更新
                        if isinstance(msg, pynmea2.types.talker.RMC):
                            if msg.datestamp and msg.timestamp:
                                dt_utc = datetime.combine(msg.datestamp, msg.timestamp)
                                temp_dt_jst = dt_utc + timedelta(hours=9)
                    except pynmea2.ParseError:
                        continue
                    except Exception as e:
                        print(f"An error occured in parse uart line")
                
                if temp_lat is not None:
                    self.latitude = temp_lat
                    self.longitude = temp_lon
                if temp_dt_jst is not None:
                    self.timestamp_jst = temp_dt_jst.strftime('%Y-%m-%d %H:%M:%S')
                    
        except serial.SerialException as e:
            print(f"Error during serial read: {e}")
            self.ser.close()
            self.ser = None

      
gps_manager = GpsManager(port, baudrate)

def idokeido():
    # 緯度と経度を抽出、内部でGPSデータを最新に更新
    gps_manager.update()
    latitude = gps_manager.latitude
    longitude = gps_manager.longitude

    # データが一度も取得できていない場合はNoneを返す
    if latitude is None or longitude is None:
        print("idokeido: 有効なGPSデータが取得できませんでした")
        return None, None
    return latitude, longitude

def zikan():
    # 日本時間を抽出、内部でGPSデータを最新に更新
    gps_manager.update()
    time_jst = gps_manager.timestamp_jst
    
    # データが一度も取得できていない場合はNoneを返す
    if time_jst is None:
        print("zikan: 有効なGPSデータが取得できませんでした")
        return None
    return time_jst

def youbi(datetime_str):
    # 曜日を抽出します
    try:
        # 文字列を datetime オブジェクトに変換
        dt_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        weekday = dt_object.strftime('%A')
        return weekday
    except ValueError:
        print(f"エラー: 無効な日時文字列のフォーマットです: {datetime_str}")
        return None

# 余弦定理でゴール角度を計算
def calculate_distance_and_angle(current_lat, current_lon, start_lat, start_lon, goal_lat, goal_lon):
    # 現在地の緯度経度をメートルに変換
    current_x, current_y = transformer.transform(current_lon, current_lat)

    # 前回の現在地（スタート地点）の緯度経度をメートルに変換
    start_x, start_y = transformer.transform(start_lon, start_lat)

    # ゴール地点の緯度経度をメートルに変換
    goal_x, goal_y = transformer.transform(goal_lon, goal_lat)

    # スタート地点から現在地までの距離を計算する
    distance_start_current = math.sqrt((current_x - start_x)**2 + (current_y - start_y)**2)

    # スタート地点からゴール地点までの距離を計算
    distance_start_goal = math.sqrt((goal_x - start_x)**2 + (goal_y - start_y)**2)

    # 現在地からゴール地点までの距離を計算
    distance_current_goal = math.sqrt((goal_x - current_x)**2 + (goal_y - current_y)**2)

    # ゴールへの方向を計算 (ラジアン)
    try:
        theta_for_goal = math.pi - math.acos((distance_start_current ** 2 + distance_start_goal ** 2 - distance_current_goal ** 2) / (2 * distance_start_current * distance_current_goal))
        return distance_start_goal, theta_for_goal
    except Exception as e:
        print(f"移動していません: {e}")
        return 2727272727, math.pi * 2
