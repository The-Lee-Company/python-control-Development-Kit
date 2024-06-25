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
    Sets the pump to track a pressure set on the dial for 30 seconds. The drive power and pressure are printed out.
    The pump can be connected only over UART as the dial is only available on the UART SPM / GP slot
    """

    # create a Disc Pump instance
    myPump = LVDiscPump()

    # connect the pump
    myPump.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using

    # select dial analog source – uncomment the two rows depending on the system used
    dial_analog_source = LVControlSource.ANA_A  # GP driver uses analog A for dial
    # dial_analog_source = LVControlSource.ANA_C  # SPM driver uses analog C for dial
    dial_analog_scaling_register = LVRegister.ANA_A_GAIN  # GP driver uses analog A for dial
    # dial_analog_scaling_register = LVRegister.ANA_C_GAIN  # SPM driver uses analog C for dial

    # select pressure sensor – uncomment the row depending on the system used
    pressure_sensor = LVControlSource.DIGITAL_PRESSURE  # SPM and Dev kit use digital pressure
    # pressure_sensor = LVControlSource.ANA_B  # Evaluation kit uses analog pressure on analog B

    # turn off data streaming mode
    myPump.streaming_mode_disable()

    # turn the pump off whilst configuring system
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # Note that if you want to PID control to vacuum, the PID terms and the Dial scaling need to be negative
    # set the pump to PID pressure control with target pressure to the dial input.
    # set the pump to pid control mode
    myPump.write_reg(LVRegister.CONTROL_MODE, LVControlMode.PID)
    # set the pid sensor source to the pressure sensor used
    myPump.write_reg(LVRegister.PID_MODE_MEAS_SOURCE, pressure_sensor)
    # set the pressure target input to dial
    myPump.write_reg(LVRegister.PID_MODE_SETPOINT_SOURCE, dial_analog_source)

    # set PID values
    myPump.write_reg(LVRegister.PID_PROPORTIONAL_COEFF, 5)
    myPump.write_reg(LVRegister.PID_INTEGRAL_COEFF, 10)
    myPump.write_reg(LVRegister.PID_DIFFERENTIAL_COEFF, 0)

    # scale the dial to range between 0 and 200mBar
    # Note that the pump power cannot exceed 1000mW by default
    myPump.write_reg(dial_analog_scaling_register, 200)

    # turn the pump on
    myPump.write_reg(LVRegister.PUMP_ENABLE, 1)

    # loop for 30s
    start_time = float(time.time())
    current_time = start_time
    while current_time - start_time < 30:
        time.sleep(0.5)
        # read the drive power and pressure of the pump and print them every 0.5s
        drive_power = myPump.read_register(LVRegister.MEAS_DRIVE_MILLIWATTS)
        pressure = myPump.read_register(LVRegister.MEAS_DIGITAL_PRESSURE)
        current_time = float(time.time())
        print(f'Time [s] {current_time - start_time:.1f}, Drive power [mW] {drive_power:.1f}, Pressure [mBar] {pressure:.1f}')

    # turn the pump off
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # close serial port / I2C connection
    myPump.disconnect_pump()
