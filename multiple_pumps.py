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
    Runs the two I2C SPMs and a UART pump (e.g. GP driver) all at the same time.
    The SPMs need to be configured with different I2C addresses and by using configure_spm_for_multiple_i2c_pumps.py
    For I2C SPM the Mains PSU needs to be connected to the Dev board.
    """

    try:
        # create disc pump instances
        spmI2C_1 = LVDiscPump()
        spmI2C_2 = LVDiscPump()
        gp = LVDiscPump()

        # connect the two I2C SPMs and the UART GP driver
        spmI2C_1.connect_pump(i2c_address=40)    # first I2C SPM
        spmI2C_2.connect_pump(i2c_address=41)    # second I2C SPM
        gp.connect_pump(com_port="COM6")   # UART GP driver. Replace COM port number with the COM port you are using

        # turn the pumps off whilst configuring system
        spmI2C_1.write_reg(LVRegister.PUMP_ENABLE, 0)
        spmI2C_2.write_reg(LVRegister.PUMP_ENABLE, 0)
        gp.write_reg(LVRegister.PUMP_ENABLE, 0)

        # change the LED colour on the pumps so we can easily identify which is which.
        # Do not use red as red is used by the system to indicate error state
        spmI2C_1.set_status_led_colour(31, 31, 0)       # Orange / Yellow
        spmI2C_2.set_status_led_colour(0, 0, 31)        # Blue
        gp.set_status_led_colour(31, 0, 31)             # Purple

        # set the pumps to manual control mode with power input to the SetVal register
        spmI2C_1.set_manual_power_control_with_set_val()
        spmI2C_2.set_manual_power_control_with_set_val()
        gp.set_manual_power_control_with_set_val()

        # set the drive power set points to 1000mW
        spmI2C_1.write_reg(LVRegister.SET_VAL, 1000)
        spmI2C_2.write_reg(LVRegister.SET_VAL, 1000)
        gp.write_reg(LVRegister.SET_VAL, 1000)

        # turn the pumps on
        spmI2C_1.write_reg(LVRegister.PUMP_ENABLE, 1)
        spmI2C_2.write_reg(LVRegister.PUMP_ENABLE, 1)
        gp.write_reg(LVRegister.PUMP_ENABLE, 1)

        # wait for a second
        time.sleep(1)

        # turn the pumps off
        spmI2C_1.write_reg(LVRegister.PUMP_ENABLE, 0)
        spmI2C_2.write_reg(LVRegister.PUMP_ENABLE, 0)
        gp.write_reg(LVRegister.PUMP_ENABLE, 0)

        # close serial port / I2C connections
        spmI2C_1.disconnect_pump()
        spmI2C_2.disconnect_pump()
        gp.disconnect_pump()
    except Exception as e:
        print("Something went wrong in communicating to the board or reading values from it.")
        print("Make sure both SPMs are configured with different I2C addresses using configure_spm_for_multiple_i2c_pumps.py")
        print(e)
