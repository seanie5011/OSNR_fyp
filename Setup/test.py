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

# define the range of channels we want to look at
channel_start = 52
channel_end = 87

all_channels = list(range(channel_start, channel_end + 1))
# k is the number of channels to turn off at once
# so if k=1, then we will have singles: [[52], [53], ...]
# so if k=2, then we will have doubles: [[52, 53], [53, 54], ...]
# this goes up to channel_end - channel_start, where we will have [[52, ..., 86], [53, ... 87]]
URA_list = []
for k in range(1, channel_end - channel_start + 1):
	channels_list = [list(range(i, i + k)) for i in range(channel_start, channel_end + 1 - k + 1)]
	for channels in channels_list:
		# create attenuations where only channel index is off (att 99.9)
		attenuations = [0.0] * len(all_channels)

		# get an index of which channels to turn off by seeing how the channels in this sublist compare to the total channels looked at
		indices = [channel - channel_start for channel in channels]
		for index in indices:
			attenuations[index] = 99.9

		# create URA for these attenuations
		new_URA = get_URA(all_channels, attenuations)

		# add to URA list
		URA_list.append(new_URA)

print(len(URA_list))