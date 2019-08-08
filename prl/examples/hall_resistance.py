import time
import numpy as np
from prl.api import (
    add_instrument, setup_experiment, add_measurement, 
    run_measurement, create_data_container, export_data_container, 
    plot_2d
)

# Declare and connect to instruments
lockin = add_instrument(name="SR830", protocol="GPIB", address=8)
lockin2 = add_instrument(name="SR860", protocol="GPIB", address=9)
magnet = add_instrument(name="CryoMag", protocol="RS-232", address=3)

# Declare data container
vxx = create_data_container(name="V_xx", dim=1)
vxy = create_data_container(name="V_xy", dim=1) 
b_record = create_data_container(name="Magnetic field", dim=1)

# Define the process of measurement
def measure_hall_resistance(max_b, sweep_rate, record_rate):
    b_change_per_record = sweep_rate / record_rate
    record_period = 1 / record_rate
    b_seq = np.linspace(0, max_b, step=b_change_per_record)  
    for b in b_seq:
        magnet.set('B'. b)
        b_record.append(b)
        vxx.append(lockin.read('X'))
        vxy.append(lockin2.read('X'))
        time.sleep(record_period)
    
exp = setup_experiment(name="My Experiment")
add_measurement(
    name="Hall Resistance",
    experiment=exp, measurement=measure_hall_resistance, 
    max_b=3, sweep_rate=0.1, record_rate=10
)
# Show plotting window which should update upon new data entry
plot_2d(x=b_record, y=[vxx, vxy])
# Should pop up a window for emergency stop
exp.run_measurement("Hall Ressitance")  

# Save results
export_data_container(vxx, "D:\\my_data\\vxx.csv")
export_data_container(vxy, "D:\\my_data\\vxy.csv")
export_data_container(b_record, "D:\\my_data\\b_record.csv")
