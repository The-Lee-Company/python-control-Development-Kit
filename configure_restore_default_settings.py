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
import EasyMCP2221

if __name__ == '__main__':
    """"
    Resets a pump to its default settings. 
    The pump can be connected either via I2C or UART. For I2C SPM the Mains PSU needs to be connected to the Dev board.
    """

    # Brief section of the program to scan the I2C bus for devices.
    # This is useful if you are unsure if an SPM was properly configured to the correct I2C address.
    # Comment this section out if you are not using a Development kit.
    try:
        # Connect to I2C chip on the Dev motherboard
        devMotherboardI2C = EasyMCP2221.Device()

        print("Scanning Development motherboard I2C bus for connected drivers:")
        for i2cAddress in range(127):
            try:
                devMotherboardI2C.I2C_read(i2cAddress)
                print(f'\tDriver found at address {i2cAddress}')
            except EasyMCP2221.exceptions.NotAckError:
                pass
    except Exception as e:
        print("Development motherboard not found. Make sure the Development motherboard is connected and powered.")
        print("if you are not using the Development motherboard, ignore this message and comment out the I2C scan section of the code")
        print(e)

    print("")   # empty line so we can easily tell the two sections of the program apart

    try:
        # create a Disc Pump instance
        pump_to_be_reset = LVDiscPump()

        # connect the pump over UART or I2C
        # pump_to_be_reset.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using
        pump_to_be_reset.connect_pump(i2c_address=40)  # replace the I2C address with the address you are using

        # turn off data streaming mode
        pump_to_be_reset.streaming_mode_disable()

        # turn the pump off whilst configuring system
        pump_to_be_reset.write_reg(LVRegister.PUMP_ENABLE, 0)

        # write a dummy value to the setVal register, so we can check if settings have been restored successfully
        # check that the dummy value was successfully written to the board
        dummyValue = 12345
        pump_to_be_reset.write_reg(LVRegister.SET_VAL, dummyValue)
        actualDummyValue = pump_to_be_reset.read_register(LVRegister.SET_VAL)

        # Restore Default board Settings
        pump_to_be_reset.restore_default_settings()

        # Check settings were restored
        returnedDummyValue = pump_to_be_reset.read_register(LVRegister.SET_VAL)
        if returnedDummyValue == actualDummyValue or dummyValue != actualDummyValue:
            # if we didnt successfully write the value in the first place
            # or value was not changed we didnt restore settings
            print("Values were not restored.")
            print("Please make sure that the board is connected over the correct I2C address or COM port.")
            print(
                "If an SPM was configured to I2C only mode it needs to be connected over I2C or it will not communicate.")
        else:
            print("Values successfully restored to default.")
            # store settings to the board
            pump_to_be_reset.store_current_settings_to_board()

        # close serial port / I2C port
        pump_to_be_reset.disconnect_pump()
    except Exception as e:
        print("Something went wrong in communicating to the board or reading values from it. Values were not restored.")
        print("Please make sure that the board is connected over the correct I2C address or COM port.")
        print("If an SPM was configured to I2C only mode it needs to be connected over I2C or it will not communicate.")
        print(e)
