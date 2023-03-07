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

tl.write("*RST")
tl.write("*CLS")

time.sleep(5)

valid_measurement = False
while ((valid_measurement == False)):
	try:
		print("Connected to", tl.query('*IDN?'))

		print("Any Errors?", tl.query("SYSTem:ERRor?"), "\n")

		for i in range(1, 5):  # check all 4 sources
			print(f"LASER {i}")
			
			# power
			tl.write(f"sour{i}:pow:state 1")  # turn on laser
			time.sleep(10)

			tl.write(f'sour{i}:pow:unit 0')  # set to dBm
			tl.write(f'sour{i}:pow 10')  # set to 10dBm / 10mW
			print(f"sour{i}:pow?", tl.query(f'sour{i}:pow?'))

			# wavelength
			tl.write(f"sour{i}:wav:auto on")  # turn on auto mode
			print(f"sour{i}:wav:auto?", tl.query(f"sour{i}:wav:auto?"))

			tl.write(f"sour{i}:wav 1552nm")  # changes wavelength to 1552nm
			print(f"sour{i}:wav?", tl.query(f"sour{i}:wav?"), "\n")

			time.sleep(5)

		tl.write("sour1:pow:state 0")  # turn off laser
		tl.write("sour2:pow:state 0")  # turn off laser
		tl.write("sour3:pow:state 0")  # turn off laser
		tl.write("sour4:pow:state 0")  # turn off laser

		valid_measurement = True
		print('SUCCESS')
	except Exception as e:
		print(f'FAILURE: {e}')
		print('Trying again...')

tl.close()
