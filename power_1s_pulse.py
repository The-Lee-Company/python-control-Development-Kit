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
    Turn the pump on at 1W for 1 second, then turn it off.
    The pump can be connected either via I2C or UART. For I2C SPM the Mains PSU needs to be connected to the Dev board.
    """

    # create a Disc Pump instance
    myPump = LVDiscPump()

    # connect the pump – uncomment the row depending if your pump is connected over UART (com port) or I2C
    # A GP driver always uses UART. The SPM can be connected through either I2C or UART
    myPump.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using
    # myPump.connect_pump(i2c_address=37)  # replace the I2C address with the address you are using (37 is the default)

    # turn off data streaming mode
    myPump.streaming_mode_disable()

    # turn the pump off whilst configuring system
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # set the pump to manual control mode with power input to the SetVal register
    myPump.set_manual_power_control_with_set_val()

    # set the drive power set point to 1000 mW
    myPump.write_reg(LVRegister.SET_VAL, 1000)

    # turn the pump on
    myPump.write_reg(LVRegister.PUMP_ENABLE, 1)

    # wait for 1 second
    time.sleep(1)

    # turn the pump off
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # close serial port / I2C connection
    myPump.disconnect_pump()
