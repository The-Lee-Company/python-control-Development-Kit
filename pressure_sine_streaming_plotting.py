"""
DISCLAIMER
This Python demo is provided "as is" and without any warranty of any kind, and its use is at your
own risk. LEE Ventus does not warrant the performance or results that you may obtain by using
this Python demo. LEE Ventus makes no warranties regarding this Python demo, express
or implied, including as to non-infringement, merchantability, or fitness for any particular purpose.
To the maximum extent permitted by law LEE Ventus disclaims liability for any loss or damage
resulting from use of this Python demo, whether arising under contract, tort (including
negligence), strict liability, or otherwise, and whether direct, consequential, indirect, or otherwise,
even if LEE Ventus has been advised of the possibility of such damages, or for any claim from any
third party.

Lee Ventus python demo
Date: 29/05/2024
Author: Ruzhev, Dimitar
Python version: 3.10

For up-to-date information on the UART or I2C commands and functionality please refer to:
Technical Note TN003: Communications Guide
"""

import time
from lee_ventus_disc_pump import *
import math
from matplotlib import pyplot as plt

if __name__ == '__main__':
    """"
    Sets the pump to track a sine wave pressure. The drive power and pressure are recorded and plotted.
    It is recommended to connect a bleed orifice for this example as this improves pressure tracking.
    The pump can be connected either via I2C or UART. For I2C SPM the Mains PSU needs to be connected to the Dev board.
    Note that I2C streaming is only supported on SPMs with Firmware version 6.16 and later.
    """

    # create a Disc Pump instance
    myPump = LVDiscPump()

    # A GP driver always uses UART. The SPM can be connected through either I2C or UART
    myPump.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using
    # myPump.connect_pump(i2c_address=37)  # replace the I2C address with the address you are using (37 is the default)

    # turn off data streaming mode while configuring the system
    myPump.streaming_mode_disable()

    # turn the pump off whilst configuring system
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # set the pump to PID pressure control with target pressure to the SetVal register
    myPump.set_pid_digital_pressure_control_with_set_val(p_term=0, i_term=50)  # SPM and Dev kit use digital pressure
    # myPump.set_pid_analog_pressure_control_with_set_val(p_term=0, i_term=50)  # Evaluation kit uses analog pressure

    # set the initial target to 0
    myPump.write_reg(LVRegister.SET_VAL, 0)

    # turn the pump on
    myPump.write_reg(LVRegister.PUMP_ENABLE, 1)

    # enable streaming mode back on
    myPump.streaming_mode_enable()

    # Create a sine-wave, from 0->100
    sine_wave = ((math.sin(i * math.pi / 10) + 1) * 50 + 25
                 for i in range(95))

    pressures = []
    powers = []
    # Send sine-wave to the driver
    for target_pressure in sine_wave:
        # Record streaming data from the driver, so it can be plotted afterwards
        stream_output = myPump.streaming_mode_get_output()
        pressures.append(stream_output[LVStreamingModeOutputIndexes.PRESSURE])
        powers.append(stream_output[LVStreamingModeOutputIndexes.VOLTAGE] * stream_output[LVStreamingModeOutputIndexes.CURRENT])

        myPump.write_reg(LVRegister.SET_VAL, target_pressure)  # Update target pressure
        time.sleep(0.05)  # Pause between updates

    # turn the pump off
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # close serial port / I2C connection
    myPump.disconnect_pump()

    # plot the captured pressure and power values
    plt.figure(figsize=(8, 6))
    plt.plot(pressures, label="Pressure mBar")
    plt.plot(powers, label="Power mW")
    plt.xlabel("Number of samples")
    plt.ylabel("Pressure [mBar] / Power [mW]")
    plt.title("Pressure sine wave")
    plt.legend()
    plt.show()


