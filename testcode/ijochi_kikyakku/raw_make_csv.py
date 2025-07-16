# csvの書き込み（フィルタ前用）

import copy
import inspect
import sys
import time
import traceback

try:
    DEBUG = True

    msg_types = ['time', 'file', 'func', 'line', 'serious_error', 'error', 'warning', 'msg', 'format_exception', 'phase', 'gnss_time', 'date', 'lat', 'lon', 'alt', 'alt_base_press', 'goal_lat', 'goal_lon', 'raw_temp', 'raw_press', 'raw_hum', 'raw_accel_all_x', 'raw_accel_all_y', 'raw_accel_all_z', 'raw_accel_line_x', 'raw_accel_line_y', 'raw_accel_line_z', 'raw_mag_x', 'raw_mag_y', 'raw_mag_z', 'raw_gyro_x', 'raw_gyro_y', 'raw_gyro_z', 'raw_grav_x', 'raw_grav_y', 'raw_grav_z']
    DEFAULT_DICT = {x : '' for x in msg_types}

    filename = f'raw_log_{time.time()}.csv'

    with open(filename, 'a') as f:
        f.write('\n\n\n\n' + ','.join(msg_types) + '\n')
except Exception as e:
    print(f"An error occured in init raw csv: {e}")

def print(msg_type : str, msg_data):
    try:
        output_dict = copy.copy(DEFAULT_DICT)
        if (msg_type == 'raw_accel_all') or (msg_type == 'raw_accel_line') or (msg_type == 'raw_mag') or (msg_type == 'raw_gyro') or (msg_type == 'raw_grav'):
            output_dict[msg_type + '_x'] = '"' + str(msg_data[0]).replace('"', '""') + '"'
            output_dict[msg_type + '_y'] = '"' + str(msg_data[1]).replace('"', '""') + '"'
            output_dict[msg_type + '_z'] = '"' + str(msg_data[2]).replace('"', '""') + '"'
        else:
            output_dict[msg_type] = '"' + str(msg_data).replace('"', '""') + '"'

        output_dict['time'] = '"' + str(time.monotonic()) + '"'
        if DEBUG:
            try:
                frame = inspect.currentframe().f_back
                output_dict['file'] = '"' + str(frame.f_code.co_filename) + '"'
                output_dict['func'] = '"' + str(frame.f_code.co_name) + '"'
                output_dict['line'] = '"' + str(frame.f_lineno) + '"'
            except Exception as e:
                print(f"An error occured in inspecting fileinfo: {e}")
            
            try:
                e_type, e_obj, e_trace = sys.exc_info()
                if e_obj is not None:
                    f_exp = traceback.format_exception(e_type, e_obj, e_trace)
                    output_dict['format_exception'] = '"' + str(f_exp[0] + f_exp[1] + f_exp[2]).replace('"', '""') + '"'
            except Exception as e:
                print(f"An error occured in inspecting error_info: {e}")

        output_msg = ','.join(output_dict.values())
        # print(output_msg)
        with open(filename, 'a') as f:
            f.write(output_msg + '\n')
    except Exception as e:
        print(f"An error occured in printing to raw csv: {e}") 