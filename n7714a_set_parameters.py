import pyvisa
import time

rm = pyvisa.ResourceManager('@py')

tl_name = 'USB0::2391::14104::MY50701053::0::INSTR'
tl = rm.open_resource(tl_name)

tl.query_delay = 0.5
tl.baud_rate = 9600
tl.write_termination = '\n'
tl.read_termination = '\n'

print(f'Trying {tl_name}')

#tl.write("*RST")
tl.write("*CLS")

time.sleep(5)

valid_measurement = False
while ((valid_measurement == False)):
	try:
		print("Connected to", tl.query('*IDN?'))

		print("Any Errors?", tl.query("SYSTem:ERRor?"), "\n")

		i = 1  # which laser to use

		tl.write(f"sour{i}:pow:state 0")  # turn off laser
		print(f"LASER {i} OFF")

		# wavelength
		tl.write(f"sour{i}:freq:auto on")  # turns on auto mode (laser must be off to do this)
		print(f"LASER {i} MODE:", "AUTO" if tl.query(f"sour{i}:freq:auto?") == "1" else "GRID")  # if output 0 then its grid

		tl.write(f"sour{i}:wav 1550nm") # changes wavelength
		print(f"LASER {i} WAVELENGTH (m):", tl.query(f'sour{i}:wav?'))  # works only if auto mode is on
		
		# power
		tl.write(f"sour{i}:pow:state 1")  # turn on laser
		print(f"LASER {i} ON")
		time.sleep(10)

		tl.write(f'sour{i}:pow:unit 0')  # set to dBm
		tl.write(f'sour{i}:pow 6')  # set to 10dBm / 10mW
		print(f"LASER {i} POWER (dBm):", tl.query(f'sour{i}:pow?'))

		time.sleep(5)
		print(f"LASER {i} SETTINGS CHANGED")

		valid_measurement = True
		print('\nSUCCESS')
	except Exception as e:
		print(f'FAILURE: {e}')
		print('Trying again...')

tl.close()
