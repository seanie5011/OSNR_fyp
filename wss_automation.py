import pyvisa
from pyvisa import constants
import time
import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
from create_URA import *

# CONSTANTS

# default for port 3, all attenuation 0 (no attenuation)
URA_DEFAULT = 'URA 52,3,0.0;53,3,0.0;54,3,0.0;55,3,0.0;56,3,0.0;57,3,0.0;58,3,0.0;59,3,0.0;60,3,0.0;61,3,0.0;62,3,0.0;63,3,0.0;64,3,0.0;65,3,0.0;66,3,0.0;67,3,0.0;68,3,0.0;69,3,0.0;70,3,0.0;71,3,0.0;72,3,0.0;73,3,0.0;74,3,0.0;75,3,0.0;76,3,0.0;77,3,0.0;78,3,0.0;79,3,0.0;80,3,0.0;81,3,0.0;82,3,0.0;83,3,0.0;84,3,0.0;85,3,0.0;86,3,0.0;87,3,0.0'

# basic channel command (52 on (start), 80 on (end), 81-87 inclusive on (markers), otherwise odd numbers are off)
URA_BASIC = 'URA 52,3,0.0;53,3,99.9;54,3,0.0;55,3,99.9;56,3,0.0;57,3,99.9;58,3,0.0;59,3,99.9;60,3,0.0;61,3,99.9;62,3,0.0;63,3,99.9;64,3,0.0;65,3,99.9;66,3,0.0;67,3,99.9;68,3,0.0;69,3,99.9;70,3,0.0;71,3,99.9;72,3,0.0;73,3,99.9;74,3,0.0;75,3,99.9;76,3,0.0;77,3,99.9;78,3,0.0;79,3,99.9;80,3,0.0;81,3,0.0;82,3,0.0;83,3,0.0;84,3,0.0;85,3,0.0;86,3,0.0;87,3,0.0'

# HELPER FUNCTIONS
def read(device='Dev1', sample_rate=10, acquire_time=1):
    '''
    Creates a plot of the Voltage over Time on ``device`` for \
    ``acquire_time`` seconds at a sample rate of ``sample_rate`` Hz.

    ``device``: the name of the device used as listed in NI MAX
    ``sample_rate``: sample rate in Hz
    ``acquire_time``: number of seconds over which to acquire data
    '''

    # the number of samples to take
    number_samples = int(sample_rate * acquire_time)
    print(f'Acquiring {number_samples} data points.')

    # create task of this name
    with nidaqmx.Task('read') as task:
        # configure task
        task.ai_channels.add_ai_voltage_chan(f'{device}/ai0')
        task.timing.cfg_samp_clk_timing(
            sample_rate, 
            samps_per_chan=number_samples, 
            sample_mode=nidaqmx.constants.AcquisitionType(10178)
        )

        # start task         
        task.start()
        # begin reading
        data = task.read(number_of_samples_per_channel=number_samples)

        # convert to numpy array for easy manipulation
        data_arr = np.array(data)
        total_span = np.abs(data_arr.max() - data_arr.min())

        # the times at which we acquire data
        acquisition_times = [(acquire_time / number_samples) * i for i in range(len(data))]
        acquisition_times = np.array(acquisition_times)

        return np.array([acquisition_times, data_arr]).T

# function so we can reset easily
def reset_default():
	'''
	Resets all port 3 channels of the wss to the default (no attenuation, all on)
	'''

	wss.write(URA_DEFAULT)
	print(wss.read())
	print(wss.read())

	# applies these attentuations
	wss.write('RSW')
	print(wss.read())
	print(wss.read())

	# print all channels again
	print(wss.query('RRA?'))
	print(wss.read())
	print(wss.read())

# function so we can set to basic (52 on (start), 80 on (end), 81-87 inclusive on (markers), otherwise odd numbers are off) easily
def reset_basic():
	'''
	Resets all port 3 channels of the wss to the basic (52 on (start), 80 on (end), 81-87 inclusive on (markers), otherwise odd numbers are off)
	'''

	wss.write(URA_BASIC)
	print(wss.read())
	print(wss.read())

	# applies these attentuations
	wss.write('RSW')
	print(wss.read())
	print(wss.read())

	# print all channels again
	print(wss.query('RRA?'))
	print(wss.read())
	print(wss.read())

# takes in a list of the URAs to set
# waits seconds second after command before reading from the DAC
# returns an array of the times and data collected from the DAC
def set_URA(URA, seconds=5):
	'''

	'''

	# set the new URA
	wss.write(URA)
	print(wss.read())
	print(wss.read())

	# apply these attentuations
	wss.write('RSW')
	print(wss.read())
	print(wss.read())

	# print all channels again
	print(wss.query('RRA?'))
	print(wss.read())
	print(wss.read())

	# allow some time to settle
	time.sleep(seconds)

	# save data and times
	reading_arr = read(device='Dev1', sample_rate=1e3, acquire_time=2)

	return reading_arr


# takes in a list of the URAs to set
# applies each one in seconds second intervals
# reads from the DAC each iteration
# returns an array of the times and data collected from the DAC
def set_URAs(URA_list, seconds=5):
	'''

	'''

	# store each reading from the DAC in a list
	reading_arrs = []

	# now pass each of these URAs into the wss, leaving some time between
	for URA in URA_list:
		# set the new URA
		wss.write(URA)
		print(wss.read())
		print(wss.read())

		# apply these attentuations
		wss.write('RSW')
		print(wss.read())
		print(wss.read())

		# print all channels again
		print(wss.query('RRA?'))
		print(wss.read())
		print(wss.read())

		# allow some time to settle
		time.sleep(seconds)

		# save data and times
		reading_arrs.append(read(device='Dev1', sample_rate=1e3, acquire_time=2))

	return reading_arrs

# SETTING UP CONNECTIONS
rm = pyvisa.ResourceManager('@py')

# open wss
wss_name = 'ASRL4::INSTR'  #'ASRL/dev/ttyUSB0::INSTR'
wss = rm.open_resource(wss_name)

# settings
wss.query_delay = 0.1
wss.baud_rate = 115200
wss.write_termination = '\r\n'
wss.read_termination = '\r\n'
wss.data_bits = 8
wss.stop_bits = constants.VI_ASRL_STOP_ONE

print(f'Trying {wss_name}')

# check serial number
# query performs write command and read command in one line, so writes then returns the command that was written
# after every command must have 2 reads (the output of the command, and the confirmation 'OK')
print(wss.query('SNO?'))
print(wss.read())
print(wss.read())

# manufacturing date
print(wss.query('MFD?'))
print(wss.read())
print(wss.read())

# print all channels
print(wss.query('RRA?'))
print(wss.read())
print(wss.read())

# default channels
reset_default()

# CHANNEL SIM, TURNING OFF ONE AT A TIME

# define the range of channels we want to look at
channel_start = 54
channel_end = 80

# set to basic as this is the starting point
reset_basic()
# read this
reading_arrs = [read(device='Dev1', sample_rate=1e3, acquire_time=2)]

# now turn off even numbers from 54 to (and including) 80
URA_list = [URA_BASIC]
for i in range(channel_start, channel_end + 1, 2):
	# reset each time
	reset_basic()

	# new URA is turning off only channel i
	new_URA = change_one_channel(i, 99.9)

	# save command as a comment by combining with basic
	URA_list.append(URA_BASIC + '\n' + new_URA)

	# apply this command and add to list
	reading_arrs.append(set_URA(new_URA))

# default
reset_default()

# save each to a text file, along with the command used
file_index = 0
for i, reading_arr in enumerate(reading_arrs):
	# save to text file, where column 1 is all the times, and column 2 is all the data points
	# the header is the URA command used
	np.savetxt(f'Data/channel_sim_off_onebyone/reading_{file_index:03}.txt', reading_arr, delimiter=',', header=URA_list[i])

	# increase file index so we dont override file
	file_index += 1

# TURN ON ALL CHANNELS

# define the range of channels we want to look at
channel_start = 52
channel_end = 87

# whether to use all on or off channels
new_URA = toggle_all(True, channel_start, channel_end)

# creates a list of this command but repeated
URA_list = []
for i in range(0, 10):
	# add to URA list
	URA_list.append(new_URA)

# apply each
reading_arrs = set_URAs(URA_list, seconds=3)

# default
reset_default()

# save each to a text file, along with the command used
file_index = 0
for i, reading_arr in enumerate(reading_arrs):
	# save to text file, where column 1 is all the times, and column 2 is all the data points
	# the header is the URA command used
	np.savetxt(f'Data/on_channels/reading_{file_index:03}.txt', reading_arr, delimiter=',', header=URA_list[i])

	# increase file index so we dont override file
	file_index += 1

# EVERY SECOND CHANNEL (channel simulation)

# set basic
reset_basic()

# have to sleep to allow settle
time.sleep(3)

# get the reading for this
reading_arr = read(device='Dev1', sample_rate=1e3, acquire_time=2)

# save to text file, where column 1 is all the times, and column 2 is all the data points
# the header is the URA command used
np.savetxt(f'Data/channel_simulation.txt', reading_arr, delimiter=',', header=URA_BASIC)

# default
reset_default()

# EVERY K CHANNEL

# define the range of channels we want to look at
channel_start = 52
channel_end = 79

# keeping 52, 80, and 81-87 on
URA_list = []
for k in range(2, channel_end - channel_start):
	URA_list.append(turn_on_every_k(channel_start, channel_end, k))

# apply each
reading_arrs = set_URAs(URA_list, seconds=3)

# default
reset_default()

# save each to a text file, along with the command used
file_index = 0
for i, reading_arr in enumerate(reading_arrs):
	# save to text file, where column 1 is all the times, and column 2 is all the data points
	# the header is the URA command used
	np.savetxt(f'Data/every_k/reading_{file_index:03}.txt', reading_arr, delimiter=',', header=URA_list[i])

	# increase file index so we dont override file
	file_index += 1

# on: 10*3 = 30seconds
# every second: 1*3 = 3seconds
# every k: 25*3 = 75seconds
# total: 108s = 1m48s