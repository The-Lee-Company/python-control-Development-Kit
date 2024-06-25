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
    This function configures both valve output on the GP driver. It should be run once to set the values, then the
    board should be power cycled and the rest of the program can resume.
    GPIO B (Valve 1) needs to be set to "slow mode default off" (default pin mode is in "fast mode default off").
    GPIO C (Valve 2) needs to be set to "slow mode default off" (default pin mode is in "slow mode default off").
    "Slow mode" allows for longer pulses (up to 30s) to be generated, however it has a lower time resolution of 1ms.
    "Fast mode" allows for more accurate pulses to be generated (resolution of 10us), however they are limited to 300ms.
    For more information check the Development Kit User Manual.
    """

    # set both valve outputs to be slow mode default off
    disc_pump_instance.write_reg(LVRegister.GPIO_B_PIN_MODE, LVGpioPinMode.OUTPUT_SLOW_MODE_DEF_LOW)    # Valve 1
    disc_pump_instance.write_reg(LVRegister.GPIO_C_PIN_MODE, LVGpioPinMode.OUTPUT_SLOW_MODE_DEF_LOW)    # Valve 2

    # store settings to the board
    disc_pump_instance.store_current_settings_to_board()

    # close serial port
    disc_pump_instance.disconnect_pump()

    while True:
        print("Valves have been configured. Power cycle the board and restart the program.")
        time.sleep(60)


if __name__ == '__main__':
    """"
    Uses two HDI valves to reverse the direction of the pump (generating pressure and vacuum). 
    This example uses the LFMX0534570B manifold from the Lee Company equipped with two 3/2 12V HDI valves. 
    The SPIKE ENABLE jumper on the Dev motherboard should be removed as an HDI valve is used (and not a VHS valve).
    The Mains PSU needs to be connected to the Dev motherboard to provide power for the valves.
    The pump can be only be a GP driver on a Development kit. Valve control is not supported on the SPM or the Eval kit.
    """

    # create a Disc Pump instance
    myPump = LVDiscPump()

    # connect the pump
    myPump.connect_pump(com_port="COM6")  # replace COM port number with the COM port you are using

    # turn off data streaming mode
    myPump.streaming_mode_disable()

    # This function configures both valve output on the GP driver if not set correctly. It should be run once to set
    # the values, then the board should be power cycled (as these settings take effect on startup).
    # The function will automatically be skipped once the valves are configured.
    if myPump.read_register(LVRegister.GPIO_B_PIN_MODE) != LVGpioPinMode.OUTPUT_SLOW_MODE_DEF_LOW or \
            myPump.read_register(LVRegister.GPIO_C_PIN_MODE) != LVGpioPinMode.OUTPUT_SLOW_MODE_DEF_LOW:
        configure_valves(myPump)

    # turn the pump off whilst configuring system
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # set the pump to manual control mode with power input to the SetVal register
    myPump.set_manual_power_control_with_set_val()

    # set the drive power set point to 500 mW
    myPump.write_reg(LVRegister.SET_VAL, 500)

    # turn the pump on
    myPump.write_reg(LVRegister.PUMP_ENABLE, 1)

    print("Generating pulses manually")
    # set both valves to off to generate pressure
    # sleep_after is set to zero so there is minimal delay between sending the two commands
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_OFF, sleep_after=0)     # Valve 1
    myPump.write_reg(LVRegister.GPIO_C_STATE, LVGpioStaticStates.STATIC_OFF)                    # Valve 2
    # wait for 1s and print the pressure reached
    time.sleep(1)
    print(f'Generating positive pressure of {myPump.read_register(LVRegister.MEAS_DIGITAL_PRESSURE)} mBar')

    # set both valves to on to generate vacuum
    # sleep_after is set to zero so there is minimal delay between sending the two commands
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_ON, sleep_after=0)      # Valve 1
    myPump.write_reg(LVRegister.GPIO_C_STATE, LVGpioStaticStates.STATIC_ON)                     # Valve 2
    # wait for 1s and print the pressure reached
    time.sleep(1)
    print(f'Generating negative pressure of {myPump.read_register(LVRegister.MEAS_DIGITAL_PRESSURE):.1f} mBar')

    # set one valve to on and the other one to off to vent the pressure
    myPump.write_reg(LVRegister.GPIO_B_STATE, LVGpioStaticStates.STATIC_OFF)                    # Valve 1
    myPump.write_reg(LVRegister.GPIO_C_STATE, LVGpioStaticStates.STATIC_ON)                     # Valve 1
    # wait for 1s and print the pressure reached
    time.sleep(1)
    print(f'Pressure vented {myPump.read_register(LVRegister.MEAS_DIGITAL_PRESSURE):.1f} mBar')

    # wait before starting the next section of the program
    time.sleep(5)
    print("Generating pulses automatically")

    # Automate the switching of back and forth between pressure and vacuum by generating automatic pulses from the board
    # The following commands configure the gpio to generate pulses that are 1500ms (1.5s) on and 1000ms (1s) off
    # in slow mode 1 unit is 1ms
    myPump.write_reg(LVRegister.GPIO_B_PULSE_DURATION, 1000)    # on time Valve 1
    myPump.write_reg(LVRegister.GPIO_C_PULSE_DURATION, 1000)    # on time Valve 2
    myPump.write_reg(LVRegister.GPIO_B_PULSE_PERIOD, 2500)      # on + off time Valve 1
    myPump.write_reg(LVRegister.GPIO_C_PULSE_PERIOD, 2500)      # on + off time Valve 2
    # Start a train of 10 pulses on both valves
    # sleep_after is set to zero so there is minimal delay between sending the two commands
    myPump.write_reg(LVRegister.GPIO_B_STATE, 10, sleep_after=0)    # Valve 1
    myPump.write_reg(LVRegister.GPIO_C_STATE, 10)                   # Valve 2

    # print out the pressure every half second for 25 seconds
    start_time = float(time.time())
    current_time = start_time
    while current_time - start_time < 25:
        time.sleep(0.5)
        current_time = float(time.time())
        print(f'Generating {myPump.read_register(LVRegister.MEAS_DIGITAL_PRESSURE):.1f} mBar')

    # turn the pump off
    myPump.write_reg(LVRegister.PUMP_ENABLE, 0)

    # close serial port / I2C connection
    myPump.disconnect_pump()
