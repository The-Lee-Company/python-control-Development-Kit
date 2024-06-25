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
    Configures two SPMs to work simultaneously over I2C. For this example the SPM configuration is done 
    over UART, but it can also be done over I2C.
        The first SPM should be plugged to UART and the program should be ran to configure it. Reboot the SPM.
        Change the I2C address to a different value.
        Then the second one should be connected over UART. Run the program to configure the second SPM and reboot it.
    For I2C SPM the Mains PSU needs to be connected to the Dev board.
    """

    # target I2C address. The I2C address of each SPM should be different (values must be between 0 and 127)
    targetI2CAddress = 41

    try:
        # create a Disc Pump instance
        spm_to_be_configured = LVDiscPump()

        # connect the SPM over UART
        spm_to_be_configured.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using

        # configure spm to I2C only mode and set I2C address
        spm_to_be_configured.configure_spm_i2c_only_mode(i2c_address=targetI2CAddress)

        # check if the settings were successfully written to the board
        if spm_to_be_configured.read_register(LVRegister.DRIVER_I2C_ADDRESS) != targetI2CAddress \
                or spm_to_be_configured.read_register(LVRegister.COMMUNICATION_INTERFACE) != LVSPMCommunicationsProtocol.ONLY_I2C:
            print("SPM was not configured.")
            print("Restore the SPM default settings by using the configure_restore_default_settings.py and try again.")
        else:
            print(f'SPM configured successfully to I2C address {targetI2CAddress}')
            # store settings to the board
            spm_to_be_configured.store_current_settings_to_board()

        # close serial port
        spm_to_be_configured.disconnect_pump()

    except Exception as e:
        print("Something went wrong in communicating to the board or reading values from it. SPM was not configured.")
        print("Restore the SPM default settings by using the configure_restore_default_settings.py and try again.")
        print(e)

