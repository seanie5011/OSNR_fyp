import pyvisa
from pyvisa import constants
import time
import nidaqmx
import numpy as np
import matplotlib.pyplot as plt

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

	# default for port 3, all attenuation 0 (no attenuation)
	URA_default = 'URA 52,3,0.0;53,3,0.0;54,3,0.0;55,3,0.0;56,3,0.0;57,3,0.0;58,3,0.0;59,3,0.0;60,3,0.0;61,3,0.0;62,3,0.0;63,3,0.0;64,3,0.0;65,3,0.0;66,3,0.0;67,3,0.0;68,3,0.0;69,3,0.0;70,3,0.0;71,3,0.0;72,3,0.0;73,3,0.0;74,3,0.0;75,3,0.0;76,3,0.0;77,3,0.0;78,3,0.0;79,3,0.0;80,3,0.0;81,3,0.0;82,3,0.0;83,3,0.0;84,3,0.0;85,3,0.0;86,3,0.0;87,3,0.0'
	wss.write(URA_default)
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

# function to generate URA commands (assuming port 3)
# pass in list of channels to change
# pass in a list of their attenuations, in the same order
# channels and attenuations MUST HAVE SAME LENGTH
def get_URA(channels, attenuations):
	'''

	'''

	# will add to this string
	URA = 'URA '

	# lambda function to get string for each individual channel
	URA_template = lambda channel, attenuation: f'{channel},3,{attenuation};'

	# pass in each channel and attenuation to this template and add to the URA string
	for i in range(len(channels)):
		URA += URA_template(channels[i], attenuations[i])

	return URA

# takes in a list of the URAs to set
# applies each one in seconds second intervals
# reads from the DAC each iteration
# returns an array of the times and data collected from the DAC
def set_URA(URA_list, seconds=5):
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

# define the range of channels we want to look at
channel_start = 52
channel_end = 87
# range of all channels used
all_channels = list(range(channel_start, channel_end + 1))

# # k is the number of channels to turn off at once
# # so if k=1, then we will have singles: [[52], [53], ...]
# # so if k=2, then we will have doubles: [[52, 53], [53, 54], ...]
# # this goes up to channel_end - channel_start, where we will have [[52, ..., 86], [53, ... 87]]
# URA_list = []
# for k in range(1, channel_end - channel_start + 1):
# 	channels_list = [list(range(i, i + k)) for i in range(channel_start, channel_end + 1 - k + 1)]
# 	for channels in channels_list:
# 		# create attenuations where only channel index is off (att 99.9)
# 		attenuations = [0.0] * len(all_channels)

# 		# get an index of which channels to turn off by seeing how the channels in this sublist compare to the total channels looked at
# 		indices = [channel - channel_start for channel in channels]
# 		for index in indices:
# 			attenuations[index] = 99.9

# 		# create URA for these attenuations
# 		new_URA = get_URA(all_channels, attenuations)

# 		# add to URA list
# 		URA_list.append(new_URA)

# create URA for these attenuations
new_URA = get_URA(all_channels, [99.9]*len(all_channels))

URA_list = []
for i in range(0, 100):
	# add to URA list
	URA_list.append(new_URA)

# apply each
reading_arrs = set_URA(URA_list, seconds=3)

# default
reset_default()

# save each to a text file, along with the command used
file_index = 0
for i, reading_arr in enumerate(reading_arrs):
	# save to text file, where column 1 is all the times, and column 2 is all the data points
	# the header is the URA command used
	np.savetxt(f'off_channels/reading_{file_index:03}.txt', reading_arr, delimiter=',', header=URA_list[i])

	# increase file index so we dont override file
	file_index += 1

# 665 commands
# at 5 seconds, 55 minutes run time, above also does the single (one before)