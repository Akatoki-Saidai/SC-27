import serial

# シリアルポートとボーレートを設定（環境に応じて変更）
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

# 無限ループでデータを読み取り、表示
while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore')
        print(line.strip())
    except KeyboardInterrupt:
        print("終了します")
        break
