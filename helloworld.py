import pyvisa

rm = pyvisa.ResourceManager('@py')

instruments = rm.list_resources()
print(f'All instruments: \n{instruments}')

for inst in instruments:
	this_resource = rm.open_resource(inst)

	this_resource.query_delay = 0.1
	this_resource.baud_rate = 115200  # usually 9600
	this_resource.write_termination = '\n'
	this_resource.read_termination = '\n'

	print(f'\nTrying {inst}')
	
	valid_measurement = False
	while ((valid_measurement == False)):
		try:
			#this_resource.write("*RST")
			this_resource.write("*CLS")
			print("Connected to ", this_resource.query('*IDN?'))
			valid_measurement = True
			print('SUCCESS')
		except Exception as e:
			print(f'FAILURE: {e}')
			print('Trying again...')

	this_resource.close()
	print(f'\nClosing {inst}')
