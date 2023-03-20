import pyvisa

rm = pyvisa.ResourceManager('@py')

afg_name = 'USB0::1689::835::C021197::0::INSTR'
afg = rm.open_resource(afg_name)

afg.query_delay = 0.1
afg.baud_rate = 9600
afg.write_termination = '\n'
afg.read_termination = '\n'

print(f'Trying {afg_name}')

afg.write("*RST")
afg.write("*CLS")

valid_measurement = False
while ((valid_measurement == False)):
	try:
		print("Connected to", afg.query('*IDN?'))

		afg.write("FUNCTION RAMP")  # Set output waveform to RAMP
		afg.write("SOURce1:FUNCtion:RAMP:SYMMetry 50")  # sets ramp to 100% symmetry
		afg.write("FREQUENCY 9.61")  # Set frequency 645kHz
		afg.write("VOLTAGE:AMPLITUDE 0.1")  # Set amplitude 2Vpp
		afg.write("VOLTAGE:OFFSET 5.75")  # Set offset 0V
		afg.write("PHASE:ADJUST 0DEG")  # Set phase 0degree

		afg.write("OUTPut1:STATe 1")  # Turns on channel 1
		#print(f'Channel 1 on? == {afg.query(f"OUTPut1:STATe?")}')  # 1 if yes

		valid_measurement = True
		print('SUCCESS')
	except Exception as e:
		print(f'FAILURE: {e}')
		print('Trying again...')

afg.close()
