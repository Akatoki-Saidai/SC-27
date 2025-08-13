import serial
import time

# シリアルポートの設定
ser = serial.Serial('/dev/ttyS0', 9600)  # Raspberry Pi 4BのUART0を使用する場合

try:
    count = 0
    while True:
        count += 1
        # print(f"がんばれgps，{count}回目だ！")
        line = ser.readline().decode('utf-8').rstrip()
        if line.startswith('$GPGGA'):  # GPGGA sentence (GPS fix data)
            print(line)
            # ここで取得したデータを処理する
        elif line.startswith('$GPRMC'):  # GPRMC sentence (Recommended minimum data for GPS)
            print(line)
            # ここで取得したデータを処理する
        time.sleep(1)

except KeyboardInterrupt:
    ser.close()
    print('Serial communication closed.')
