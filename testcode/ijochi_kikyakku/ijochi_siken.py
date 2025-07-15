# センサーをしばらく動かして異常値がないか確認するプログラム

import smbus
import time
import make_csv
import raw_make_csv
from bme280 import BME280Sensor
from bno055 import BNO055
from ijochi import abnormal_check

try:
    bus = smbus.SMBus(1)
    bme = BME280Sensor(bus_number=1)
    bno = BNO055()
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

    # 初めは異常値が出てくるので，空測定
    for i in range(20):
        try:
            bme.read_data()
        except Exception as e:
            print(f"An error occurred during empty measurement in BME: {e}")

    while True:
        # BME280
        try:
            temp = bme.temperature()
            press = bme.pressure()
            hum = bme.humidity()
            # フィルタ前
            raw_make_csv.print('raw_temp', temp)
            raw_make_csv.print('raw_press', press)
            raw_make_csv.print('raw_hum', hum)
            # フィルタ後
            temp_f = abnormal_check('bme', 'temperature', temp)
            press_f = abnormal_check('bme', 'pressure', press)
            hum_f = abnormal_check('bme', 'humidity', hum)
            make_csv.print('temp', temp_f)
            make_csv.print('press', press_f)
            make_csv.print('hum', hum_f)
        except Exception as e:
            print(f"BME280 error: {e}")

        # BNO055
        try:
            accel = bno.read_accelerometer()
            gyro = bno.read_gyroscope()
            mag = bno.read_magnetometer()
            linear_accel = bno.read_linear_acceleration()
            gravity = bno.read_gravity()
            # フィルタ前
            raw_make_csv.print('raw_accel_all', accel)
            raw_make_csv.print('raw_gyro', gyro)
            raw_make_csv.print('raw_mag', mag)
            raw_make_csv.print('raw_accel_line', linear_accel)
            raw_make_csv.print('raw_grav', gravity)
            # フィルタ後
            accel_f = abnormal_check('bno', 'accel', list(accel))
            gyro_f = abnormal_check('bno', 'gyro', list(gyro))
            mag_f = abnormal_check('bno', 'mag', list(mag))
            linear_accel_f = abnormal_check('bno', 'linear_accel', list(linear_accel))
            gravity_f = abnormal_check('bno', 'gravity', list(gravity))
            make_csv.print('accel_all', accel_f)
            make_csv.print('gyro', gyro_f)
            make_csv.print('mag', mag_f)
            make_csv.print('accel_line', linear_accel_f)
            make_csv.print('grav', gravity_f)
        except Exception as e:
            print(f"BNO055 error: {e}")

        time.sleep(1)

except Exception as e:
    print(f"An error occurred in setting bme/bno object: {e}")

