import numpy as np
import matplotlib.pyplot as plt

reading_arr = np.loadtxt('adjacent_channels/reading_004.txt', delimiter=',', skiprows=1).T

# plot min
plt.axhline(reading_arr[1].min(), color='k', ls='--')
# plot max
plt.axhline(reading_arr[1].max(), color='k', ls='--')
# plot voltage vs time
plt.plot(
    reading_arr[0],
    reading_arr[1],
)
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.grid()
plt.show()