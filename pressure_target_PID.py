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

if __name__ == '__main__':
    """"
    Sets the pump to track a target constant pressure for 10 seconds. The drive power and pressure are printed out.
    The pump can be connected either via I2C or UART. For I2C SPM the Mains PSU needs to be connected to the Dev board.
    """

    # create a Disc Pump instance
    myPump = LVDiscPump()

    # A GP driver always uses UART. The SPM can be connected through either I2C or UART
    myPump.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using
    # myPump.connect_pump(i2c_address=37)  # replace the I2C address with the address you are using (37 is the default)

    # turn off data streaming mode
    myPump.streaming_mode_disable()

    # turn the pump off whilst configuring system
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # Note that if you want to PID control to vacuum, the PID terms and the SetVal pressure target need to be negative
    # set the pump to PID pressure control with target pressure to the SetVal register
    myPump.set_pid_digital_pressure_control_with_set_val(p_term=5, i_term=10)  # SPM and Dev kit use digital pressure
    # myPump.set_pid_analog_pressure_control_with_set_val(p_term=5, i_term=10)  # Evaluation kit uses analog pressure

    # set the target pressure to 123mBar
    # Note that the pump power cannot exceed 1000mW by default
    myPump.write_reg(LVRegister.SET_VAL, 123)

    # turn the pump on
    myPump.write_reg(LVRegister.PUMP_ENABLE, 1)

    # loop for 30s
    start_time = float(time.time())
    current_time = start_time
    while current_time - start_time < 30:
        # read the drive power and pressure of the pump and print them every 0.5s
        drive_power = myPump.read_register(LVRegister.MEAS_DRIVE_MILLIWATTS)
        pressure = myPump.read_register(LVRegister.MEAS_DIGITAL_PRESSURE)
        current_time = float(time.time())
        print(f'Time [s] {current_time - start_time:.1f}, Drive power [mW] {drive_power:.1f}, Pressure [mBar] {pressure:.1f}')
        time.sleep(0.5)

    # turn the pump off
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # close serial port / I2C connection
    myPump.disconnect_pump()
