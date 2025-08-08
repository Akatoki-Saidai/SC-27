import smbus
import time
# import make_csv

from bme280 import BME280Sensor

try:
    
    bus = smbus.SMBus(1)
    bme = BME280Sensor(bus_number=1)

    # 初めは異常値が出てくるので，空測定
    for i in range(20):
        try:
            bme.read_data()
        except Exception as e:
            print(f"An error occurred during empty measurement in BME: {e}")
    
    baseline = bme.baseline()

except Exception as e:
    print(f"An error occurred in setting bme object: {e}")

while True:
    try:
        temperature = bme.temperature()
        pressure = bme.pressure()
        # humidity = bme.humidity()
        # make_csv.print("alt_base_press", pressure)
        altitude = bme.altitude(pressure, qnh=baseline)

        print(f"Temperature: {temperature} °C")
        print(f"Pressure: {pressure} hPa")
        # print(f"Baseline Pressure: {baseline} hPa")
        print(f"Altitude: {altitude} m")
        # time.sleep(0.2)
    
    except Exception as e:
        print(f"An error occurred in running bme object: {e}")





# ぼくは、、、、も、、う、、、、、、、、
# ここにたどり着いた人へ。
# ディスコードのアクティビティの表示には気を付けよう！
