# definitionファイル内から，当フェーズを完成させるために必要なものをまずimportして，フローチャートを満たすようにコードを書いてほしい．
# 別ファイルを参照するライブラリがあるらしい
import time
import smbus
import RPi.GPIO as GPIO
import make_csv

from bme280 import BME280Sensor
from bno055 import BNO055

def main():

    # 温湿度気圧センサセットアップ
    try:
        bus = smbus.SMBus(1)
        bme = BME280Sensor(bus_number=1)

        for i in range(10):
            try:
                bme.read_data()
            except Exception as e:
                print(f"An error occurred during empty measurement in BME: {e}")
                make_csv.print('msg', f"An error occurred during empty measurement in BME: {e}")

        data = bme.read_data()
        pressure = bme.compensate_P(data)
        make_csv.print("alt_base_press", pressure)
        baseline = bme.baseline(pressure)
        make_csv.print("msg", "all clear(bme280)")

    except Exception as e:
        print(f"An error occurred in setting bme object: {e}")
        make_csv.print('serious_error', f"An error occurred in setting bme280 object: {e}")
        return

    # 9軸センサセットアップ
    try:
        bno = BNO055()
        if bno.begin() is not True:
            print("Error initializing device")
            make_csv.print("serious_error", "Error initializing device")
            return
        time.sleep(1)
        bno.setExternalCrystalUse(True)
        make_csv.print("msg", "all clear(bno055)")

    except Exception as e:
        print(f"An error occurred in setting bno055: {e}")
        make_csv.print("serious_error", f"An error occurred in setting bno055: {e}")
        return

    phase = 1  # フェーズ0から開始
    ready = False

    try:
        print("セットアップ完了")
        make_csv.print("msg", "セットアップ完了")
        make_csv.print("phase", 0)

        while True:
            # --------------------------- #
            #        待機フェーズ         #
            # --------------------------- #
            if phase == 0:
                try:
                    data = bme.read_data()
                    pressure = bme.compensate_P(data)
                    time.sleep(1.0)
                    alt_1 = bme.altitude(pressure, qnh=baseline)
                    print(f"alt_1: {alt_1}")
                    time.sleep(0.5)

                    if  alt_1 >= 10:
                        phase = 1
                        print("Go to falling phase")
                        make_csv.print("msg", "Go to falling phase")
                        make_csv.print("phase", 1)
                    else:
                        print("落下を検知できませんでした")

                    time.sleep(1)

                except Exception as e:
                    print(f"An error occurred in phase 0: {e}")
                    make_csv.print("error", f"An error occurred in phase 0: {e}")

            # --------------------------- #
            #        落下フェーズ         #
            # --------------------------- #
            elif phase == 1:
                try:
                    consecutive_count = 0

                    for _ in range(10):
                        data = bme.read_data()
                        pressure = bme.compensate_P(data)
                        alt_2 = bme.altitude(pressure, qnh=baseline)

                        linear_accel = bno.getVector(BNO055.VECTOR_LINEARACCEL)
                        accel_x, accel_y, accel_z = linear_accel

                        print(f"accel_x: {accel_x}, accel_y: {accel_y}, accel_z: {accel_z}")

                        if abs(accel_x) + abs(accel_y) + abs(accel_z) < 0.1 and alt_2 <= 0.1:
                            consecutive_count += 1
                            print(f"落下終了の条件を満たしました: {consecutive_count}/5")
                            make_csv.print("msg", f"落下終了の条件を満たしました: {consecutive_count}/5")
                            time.sleep(1)
                        else:
                            consecutive_count = 0
                            print(f"落下終了の条件を満たしませんでした")
                            time.sleep(0.5)

                        if consecutive_count >= 5:
                            make_csv.print("msg","ニクロム線切断開始")
                            print("ニクロム線切断開始")

                            #ニクロム線切断
                            pin = 16
                            '''
                            GPIO.setmode(GPIO.BCM)
                            GPIO.setup(pin, GPIO.OUT)
                            GPIO.output(pin, 1)
                            time.sleep(5)
                            GPIO.output(pin, 0)
                            '''
                            make_csv.print("msg","ニクロム線切断完了")
                            print("ニクロム線切断完了")
                            return  # 終了

                except Exception as e:
                    print(f"An error occurred in phase 1: {e}")
                    make_csv.print("error", f"An error occurred in phase 1: {e}")

   

if __name__ == "__main__":
    main()

