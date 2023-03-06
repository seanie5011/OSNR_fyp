import nidaqmx
import numpy as np
import matplotlib.pyplot as plt

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
        print(f'Total span in V: {total_span}')

        # the times at which we acquire data
        acquisition_times = [(acquire_time / number_samples) * i for i in range(len(data))]
        acquisition_times = np.array(acquisition_times)

        # plot min
        plt.axhline(data_arr.min(), color='k', ls='--')
        # plot max
        plt.axhline(data_arr.max(), color='k', ls='--')
        # plot voltage vs time
        plt.plot(
            acquisition_times,
            data_arr,
        )
        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [V]')
        plt.grid()
        plt.show()



if __name__ == '__main__':
      read('Dev1', 1e5, 1)