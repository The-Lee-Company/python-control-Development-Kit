# Disc Pump Development kit / Smart Pump Module Python control - UEKA0500300x
This repository contains a Python code snippet library for The Lee Company Disc Pump Development Kit UEKA0500300x and the Smart Pump Module (SPM) UxxCxxxxxxxx.
These examples are meant to be used along with the "PCB Serial Communications Guide: TG003" and the relevant product user manual, which can be found on the Lee Company website https://www.theleeco.com/disc-pumps/.

## Example code
The following examples code snippets are provided:
* **power_1s_pulse.py** - Turn the pump on at 1W for 1 second, then turn it off.
* **pressure_target_PID.py** - Sets the pump to track a target constant pressure for 10 seconds. The drive power and pressure are printed out.
* **pressure_dial_PID.py** - ets the pump to track a pressure set on the dial for 30 seconds. The drive power and pressure are printed out.
* **flow_target_PID.py** - Sets the pump to track a target flow using an external flow sensor. 
* **power_sine_streaming_plotting.py** - Example that sets the pump to track a sine wave power. The drive power is recorded and plotted.
* **pressure_sine_streaming_plotting.py** - Sets the pump to track a sine wave pressure. The drive power and pressure are recorded and plotted.
* **valves_reversible_flow.py** - Uses two HDI valves to reverse the direction of the pump (generating pressure and vacuum). 
* **valves_time_metered_dosing.py** - Uses one 12V VHS valve to generate droplets of water.
* **multiple_pumps.py** -  Runs the two I2C SPMs and a UART pump (e.g. GP driver) all at the same time. The SPMs need to be configured with different I2C addresses and by using **configure_spm_for_multiple_i2c_pumps.py**
  - **configure_spm_for_multiple_i2c_pumps.py** - Helper program that configures two SPMs to work simultaneously over I2C.
  - **configure_restore_default_settings** - Helper program that resets a pump to its default settings. 

**Take note of the libraries dependencies in each script. Please ensure you have the relevant libraries installed, a full list of libraries can be found in "requirements.txt". For setting up a python environment you can visit https://www.jetbrains.com/help/pycharm/getting-started.html**

## Library code
The following files are setup to work like a python library providing an easy to use framework for controlling the Disc Pump Drivers.
* **lee_ventus_register.py** - Contains useful values for setting the board registers, such as a full list of registers (LVRegister) and some common values for control modes or GPIO settings. The most up to date information on the registers and their values can be found in "PCB Serial Communications Guide: TG003".
* **lee_ventus_disc_pump.py** - Contains the LVDiscPump class which wraps sending and receiving commands from the driver:
  - connect_pump - Connects a pump via I2C or UART. Either a COM port or an I2C address needs to be defined.
  - write_reg - Writes a value to a given register. Takes a register ID (number) and the new value to be written. Works for both I2C and UART connected pumps.
  - read_register - Reads the value of a given register. Takes a register ID (number). Works for both I2C and UART connected pumps.
  - disconnect_pump - Disconnects a pump. Works for both I2C and UART connected pumps.
  - There are a few other functions that help set up manual or PID control, configure spm for I2C only mode, restore default settings or save settings to the board.

## Contact us

For additional support, please visit https://www.theleeco.com/contact/ or you can call our Technical Support Line on 1-800-LEE-PLUG.

We welcome suggestions for how we can improve and build upon this repository; please feel free to share your ideas, feature requests and any bugs you identify with us using the email address above. 

## DISCLAIMER 
These Python demos are provided "as is" and without any warranty of any kind, and their use is at your own risk. The Lee Company does not warrant the performance or results that you may obtain by using these Python demos. The Lee Company makes no warranties regarding these Python demos, express or implied, including as to non-infringement, merchantability, or fitness for any particular purpose. To the maximum extent permitted by law The Lee Company disclaims liability for any loss or damage resulting from use of these Python demos, whether arising under contract, tort (including negligence), strict liability, or otherwise, and whether direct, consequential, indirect, or otherwise, even if The Lee Company has been advised of the possibility of such damages, or for any claim from any third party.
