import pyvisa
from pyvisa import constants

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

# default for port 3, all attenuation 0 (no attenuation)
wss.write('URA 52,3,0.0;53,3,0.0;54,3,0.0;55,3,0.0;56,3,0.0;57,3,0.0;58,3,0.0;59,3,0.0;60,3,0.0;61,3,0.0;62,3,0.0;63,3,0.0;64,3,0.0;65,3,0.0;66,3,0.0;67,3,0.0;68,3,0.0;69,3,0.0;70,3,0.0;71,3,0.0;72,3,0.0;73,3,0.0;74,3,0.0;75,3,0.0;76,3,0.0;77,3,0.0;78,3,0.0;79,3,0.0;80,3,0.0;81,3,0.0;82,3,0.0;83,3,0.0;84,3,0.0;85,3,0.0;86,3,0.0;87,3,0.0')
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