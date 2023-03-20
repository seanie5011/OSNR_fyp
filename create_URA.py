# FUNCTIONS FOR URA COMMANDS

# function to generate URA commands given a list of channels and a list of attenuations corresponding to each channel
# channels and attenuations MUST HAVE SAME LENGTH
# port can be assigned but default is 3
def get_URA(channels: list, attenuations: list, port=3):
	'''
	Generates URA commands given a list of channels and corresponding attenuations, for the designated port.

	channels: list of integers
	attenuations: list of floats (len(attenuations) = len(channels))
	port: the port to use (default: 3)
	'''

	# will add to this string
	URA = 'URA '

	# lambda function to get string for each individual channel
	URA_template = lambda channel, attenuation: f'{channel},{port},{attenuation};'

	# pass in each channel and attenuation to this template and add to the URA string
	for i in range(len(channels)):
		URA += URA_template(channels[i], attenuations[i])

	return URA

# function to write URA commands to a file with comments
def write_URA(URA: str, filename='URA_commands', comment=''):
	'''
	Writes a URA command to a text file in the current working directory, with a comment detailing what the command does. \
	Will create the textfile if not already, if it is created already will append to that textfile. \
	So commands will always have structure: {empty line} -> {comment} -> {command} \
	Returns the text written.

	URA: string of the URA command to use
	filename: string of the name of the .txt file to use
	comment: string that will be added in the line above this command (preceded by a '#', will have '# {comment}')
	'''

	# correct filename
	filename = f'{filename}.txt'
	# correct comment
	comment = f'# {comment}'
	# text to write
	text = f'\n{comment}\n{URA}\n'

	# append text to file
	with open(filename, 'a') as file:
		file.write(text)

	return text

# function to read URA commands from a file with comments
# so if you want a command from a particular line, simply index for that line number
def read_URA(filename: str):
	'''
	Reads all lines from a file with the corresponding comments. \
	Assumes the text file is only of URA commands and comments in the above format. \
	Preprocesses so that there is an extra line at the start, ensures that the line number and index match. \
	Further, removes the '\n' from every command and every comment.
	Returns a list of every line in the file, with the preprocessing.

	filename: string of the name of the .txt file to use
	'''

	# correct filename
	filename = f'{filename}.txt'

	# read all lines from file
	with open(filename, 'r') as file:
		all_text = file.readlines()

	# new text variable to store the preprocessed text
	# add a new empty line at the start to match line number
	text = ['\n']
	# now pass through and process each command and comment
	for line in all_text:
		# if this line starts with a '#' or 'U', it is a comment or command
		# so we want to remove the '\n' at the end (last character as '\n' counts as 1)
		# then (and otherwise), append this line
		if line[0] == '#' or line[0] == 'U':
			text.append(line[:-1])
		else:
			text.append(line)

	return text

# creates URAs of either attenuation 0.0 or 99.9, taking from a list of 0 (on) or 1 (off)
# where 0 refers to 99.9 attenuation, and 1 refers to 0.0 attenuation
# assumes port 3 default
def URA_from_binary(channels: list, binary: list, port=3):
	'''
	Generates a URA command from a list called binary acting on channels, for port. \
	Where binary is a list of 0s or 1s (or 'off' or 'on' respectively), where 0 binary ('off') refers to 99.9 attenuation; \
	and where 1 binary ('on') refers to 0.0 attenuation

	channels: list of integers
	binary: list of either 0s or 1s
	port: the port to use (default: 3)
	'''

	# create attenuations list
	attenuations = []
	# pass through each element in binary
	for value in binary:
		# convert 0s or 'off's to 99.9s and 1s or 'on's to 0.0s
		if value == 1 or value == 'on':
			attenuations.append('0.0')
		elif value == 0 or value == 'off':
			attenuations.append('99.9')


	# generate URA command
	URA = get_URA(channels, attenuations, port)

	return URA

# FUNCTIONS TO GENERATE VARIOUS URA PATTERNS

# function to turn on or off all channels in range
# if on=True, will turn on all
# if on=False, will turn off all
def toggle_all(on, channel_start, channel_end):
	'''
	Generates a URA to turn on or off all channels in the specified channel range (inclusive).

	on: Boolean of whether channels should be turned on (True) or off (False)
	channel_start: integer of the channel number to start the pattern at
	channel_end: integer of the channel number to end the pattern at (inclusive)
	'''

	# range of all channels used
	all_channels = list(range(channel_start, channel_end + 1))

	# create URA for these attenuations
	if on:
		attenuation = 0.0
	else:
		attenuation = 99.9

	# get the URA command for this
	URA = get_URA(all_channels, [attenuation] * len(all_channels))

	return URA

# function to create the adjacent channels pattern
# eg: all on except channel i, or all on except channel i and i + 1, etc
def adjacent_channels(channel_start: int, channel_end: int):
	'''
	Returns a list of URAs for each possible adjacent channel pattern in the channel range.

	channel_start: integer of the channel number to start the pattern at
	channel_end: integer of the channel number to end the pattern at (inclusive)
	'''

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

	return URA_list

# function to turn on every k channel in channel range (including channel_start)
# will turn rest off
def turn_on_every_k(channel_start: int, channel_end: int, k: int):
	'''
	Generates the URA to turn on every k channel in the channel range. \
	eg: if k=2, and channel_start=52, will turn on 52, 54, 56, etc.

	channel_start: integer of the channel number to start the pattern at
	channel_end: integer of the channel number to end the pattern at (inclusive)
	k: integer of the stepsize
	'''

	# get each channel
	channels = range(channel_start, channel_end + 1)
	# start attenuations off
	attenuations = [99.9] * len(channels)

	# turn on every k
	for i in range(0, len(attenuations), k):
		attenuations[i] = 0.0

	URA = get_URA(channels, attenuations)

	return URA

# function to only change one channel (leave rest as is)
def change_one_channel(channel: int, attenuation: float):
	'''
	Generates the URA command to apply attenuation to only channel.
	'''

	# get_URA only accepts lists
	URA = get_URA([channel], [attenuation])

	return URA

# the default URA command (all in range 52-87 inclusive on)
URA_default = 'URA 52,3,0.0;53,3,0.0;54,3,0.0;55,3,0.0;56,3,0.0;57,3,0.0;58,3,0.0;59,3,0.0;60,3,0.0;61,3,0.0;62,3,0.0;63,3,0.0;64,3,0.0;65,3,0.0;66,3,0.0;67,3,0.0;68,3,0.0;69,3,0.0;70,3,0.0;71,3,0.0;72,3,0.0;73,3,0.0;74,3,0.0;75,3,0.0;76,3,0.0;77,3,0.0;78,3,0.0;79,3,0.0;80,3,0.0;81,3,0.0;82,3,0.0;83,3,0.0;84,3,0.0;85,3,0.0;86,3,0.0;87,3,0.0'

# basic channel command (52 on (start), 80 on (end), 81-87 inclusive on (markers), otherwise odd numbers are off)
URA_basic = 'URA 52,3,0.0;53,3,99.9;54,3,0.0;55,3,99.9;56,3,0.0;57,3,99.9;58,3,0.0;59,3,99.9;60,3,0.0;61,3,99.9;62,3,0.0;63,3,99.9;64,3,0.0;65,3,99.9;66,3,0.0;67,3,99.9;68,3,0.0;69,3,99.9;70,3,0.0;71,3,99.9;72,3,0.0;73,3,99.9;74,3,0.0;75,3,99.9;76,3,0.0;77,3,99.9;78,3,0.0;79,3,99.9;80,3,0.0;81,3,0.0;82,3,0.0;83,3,0.0;84,3,0.0;85,3,0.0;86,3,0.0;87,3,0.0'

# OPERATION
if __name__ == '__main__':
	action = input('What would you like to do? [(w)rite/(r)ead/(p)rint]\n> ').lower()
	print('\n----------\n')

	if action == 'w' or action == 'write':
		text = write_URA(URA_default, comment='Default URA command')

		print('WRITE START')
		print(text)
		print('WRITE FINISH')

	if action == 'r' or action == 'read':
		text = read_URA('URA_commands')

		print('READ START')
		print(text)
		print('READ FINISH')

	if action == 'p' or action == 'print':
		text = turn_on_every_k(52, 79, 79-52)

		print('PRINT START')
		print(text)
		print('PRINT FINISH')