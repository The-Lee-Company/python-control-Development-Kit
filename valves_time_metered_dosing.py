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


def configure_valves(disc_pump_instance: LVDiscPump):
    """
    This function configures GPIO B valve output on the GP driver. It should be run once to set the values, then the
    board should be power cycled and the rest of the program can resume.
    GPIO B (valve 1) needs to be set to "fast mode default off" (default pin mode is in "fast mode default off").
    "Fast mode" allows for more accurate pulses to be generated (resolution of 10us), however they are limited to 300ms.
    "Slow mode" allows for longer pulses (up to 30s) to be generated, however it has a lower time resolution of 1ms.
    For more information check the Development Kit User Manual.
    """

    # set both valve outputs to be slow mode default off
    disc_pump_instance.write_reg(LVRegister.GPIO_B_PIN_MODE, LVGpioPinMode.OUTPUT_FAST_MODE_DEF_LOW)    # Valve 1

    # store settings to the board
    disc_pump_instance.store_current_settings_to_board()

    # close serial port
    disc_pump_instance.disconnect_pump()

    while True:
        print("Valve have been configured. Power cycle the board and restart the program.")
        time.sleep(60)


if __name__ == '__main__':
    """"
    Uses one 12V VHS valve to generate droplets of water.
    The SPIKE ENABLE jumper on the Dev motherboard should be set as a VHS valve is used (and not an HDI).
    The Mains PSU needs to be connected to the Dev motherboard to provide power for the valves.
    The pump can be only be a GP driver on a Development kit. Valve control is not supported on the SPM or the Eval kit.
    """

    # create a Disc Pump instance
    myPump = LVDiscPump()

    # connect the pump
    myPump.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using

    # turn off data streaming mode
    myPump.streaming_mode_disable()

    # This function configures the valve output on the GP driver if not set correctly. It should be run once to set
    # the values, then the board should be power cycled (as these settings take effect on startup).
    # The function will automatically be skipped once the valves are configured.
    if myPump.read_register(LVRegister.GPIO_B_PIN_MODE) != LVGpioPinMode.OUTPUT_FAST_MODE_DEF_LOW:
        configure_valves(myPump)

    # turn the pump off whilst configuring system
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # set the pump to manual control mode with power input to the SetVal register
    myPump.set_pid_digital_pressure_control_with_set_val(p_term=0, i_term=50)

    # set the drive power set point to 200 mBar
    myPump.write_reg(LVRegister.SET_VAL, 200)

    # turn the pump on and wait for the pressure to settle
    myPump.write_reg(LVRegister.PUMP_ENABLE, 1)
    time.sleep(1)

    print("Generating pulses manually")
    # set valve on for 50ms then wait for 200ms and repeat
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_ON)     # Valve 1
    time.sleep(0.05)
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_OFF)    # Valve 1
    time.sleep(0.2)
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_ON)     # Valve 1
    time.sleep(0.05)
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_OFF)    # Valve 1
    time.sleep(0.2)

    # wait before starting the next section of the program
    time.sleep(2)
    print("Generating pulses automatically")

    # Automate the droplet generation by generating automatic pulses from the board
    # The following commands configure the gpio to generate pulses that are 50ms on and 200ms off
    # in fast mode 1 unit is 10us or 0.01ms
    myPump.write_reg(LVRegister.GPIO_B_PULSE_DURATION, 50 * 100)    # on time Valve 1
    myPump.write_reg(LVRegister.GPIO_B_PULSE_PERIOD, 250 * 100)     # on + off time Valve 1
    # Start a train of 10 pulses on the valve
    myPump.write_reg(LVRegister.GPIO_B_STATE, 10)                   # Valve 1

    # wait for the pulses to complete and turn the pump off
    time.sleep(2.5)
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # close serial port / I2C connection
    myPump.disconnect_pump()
