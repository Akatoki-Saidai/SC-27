import smbus
import time
# import make_csv

from bme280 import BME280Sensor

try:
    bus = smbus.SMBus(1)
    bme = BME280Sensor(bus_number=1)

    # 初めは異常値が出てくるので，空測定
    for i in range(10):
        try:
            bme.read_data()
        except Exception as e:
            print(f"An error occurred during empty measurement in BME: {e}")
            # make_csv.print('msg', f"An error occurred during empty measurement in BME: {e}")

    data = bme.read_data()  # ここでデータを取得
    pressure = bme.compensate_P(data)  # 気圧を補正して取得
    # make_csv.print("alt_base_press", pressure)
    baseline = bme.baseline(pressure)

except Exception as e:
    print(f"An error occurred in setting bme object: {e}")
    # make_csv.print('serious_error', f"An error occurred in setting bme280 object: {e}")

# ぼくは、、、、も、、う、、、、、、、、
# ここにたどり着いた人へ。
# ディスコードのアクティビティの表示には気を付けよう！
