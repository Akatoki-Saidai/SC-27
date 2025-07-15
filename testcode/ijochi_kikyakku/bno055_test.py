import time
from bno055 import BNO055


try:
	# データ取得のサンプル

	# Create and configure the BNO sensor connection.  Make sure only ONE of the
	# below 'bno = ...' lines is uncommented:
	# Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
	bno = BNO055()
	# BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
	# and RST connected to pin P9_12:
	#bno = BNO055.BNO055(rst='P9_12')
	
	# Initialize the BNO055 and stop if something went wrong.
	if not bno.begin():
		raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

	# Print system status and self test result.
	status, self_test, error = bno.get_system_status()
	print('System status: {0}'.format(status))
	print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
	# Print out an error if system status is in error mode.
	if status == 0x01:
		print('System error: {0}'.format(error))
		print('See datasheet section 4.3.59 for the meaning.')

	# Print BNO055 software revision and other diagnostic data.
	sw, bl, accel, mag, gyro = bno.get_revision()
	print('Software version:   {0}'.format(sw))
	print('Bootloader version: {0}'.format(bl))
	print('Accelerometer ID:   0x{0:02X}'.format(accel))
	print('Magnetometer ID:    0x{0:02X}'.format(mag))
	print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

	print('Reading BNO055 data, press Ctrl-C to quit...')
	while True:

		# キャリブレーションの状態(これは測定値ではない！), 0=uncalibrated and 3=fully calibrated.
		_sys, gyro, accel, mag = bno.get_calibration_status()
		# Print everything out.
		print('Gyro_cal={0} Accel_cal={1} Mag_cal={2}'.format(gyro, accel, mag))

		# Other values you can optionally read:
		
		# 4元数方位
		# Orientation as a quaternion:
		#x,y,z,w = bno.quaterion()
		
		# 温度(℃)
		# temp_c = bno.temperature()

		# オイラー角(deg)
		# heading, roll, pitch = bno.euler()

		# 地磁気(μT)
		mag_x,mag_y,mag_z = bno.magnetometer()
		
		# ジャイロ(deg/s)
		gyro_x,gyro_y,gyro_z = bno.gyroscope()

		# 加速度(m s^-2)
		# Accelerometer data (in meters per second squared):
		# x,y,z = bno.accelerometer()

		# 線形加速度(m s^-2)  (全加速度から重力加速度を取り除いたもの)
		# returned in meters per second squared):
		liner_accel_x,liner_accel_y,liner_accel_z = bno.linear_acceleration()

		# 重力加速度(m s^-2)
		gravity_x,gravity_y,gravity_z = bno.gravity()

		print(f"magnetometer: \nmag_x:{mag_x:.4f}  mag_y:{mag_y:.4f}  mag_z:{mag_z:.4f}")
		print(f"gyroscope: \ngyro_x:{gyro_x:.4f}  gyro_y:{gyro_y:.4f}  mag_z:{gyro_z:.4f}")
		print(f"liner_accel: \nliner_accel_x:{liner_accel_x:.4f}  liner_accel_y:{liner_accel_y:.4f}  liner_accel_z:{liner_accel_z:.4f}")
		print(f"gravity: \ngravity_x:{gravity_x:.4f}  gravity_y:{gravity_y:.4f}  gravity_z:{gravity_z:.4f}")
		print()

		time.sleep(1)

except Exception as e:
	print(f"An error occured in BNO055: {e}")