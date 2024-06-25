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

from typing import List

import serial
import time
import struct
import EasyMCP2221

from lee_ventus_register import *


# ***********************************************************************************
# * LVDiscPump class
# ***********************************************************************************


class LVDiscPump:
    # -----------------------------------------------------------------------------
    # Public functions
    # -----------------------------------------------------------------------------

    def connect_pump(self, com_port='', i2c_address=-1):
        """
            Connects a pump via I2C or UART.
            Either a COM port or an I2C address needs to be defined (but not both).

            Args:
                com_port (str, optional): The COM port the pump should be connected to e.g. "COM6"
                i2c_address (int, optional): The I2C address the pump should be connected to e.g. 37
            Returns:
                None
        """
        if com_port != '' and i2c_address == -1:
            self._is_uart = True
            self._connect_pump_uart(com_port)
            return
        if com_port == '' and i2c_address != -1:
            self._is_uart = False
            self._connect_pump_i2c(i2c_address)
            return
        raise Exception(f'Invalid configuration for connecting a pump.')

    def write_reg(self, reg_id: int, value, rounding_decimal_places=3, sleep_after=0.005):
        """
            Writes a value to a given register.
            Works for both I2C and UART connected pumps.

            Args:
                reg_id (int): The register ID (number) to be written to. E.g. 0 for Pump enable.
                value (int or float): The value to be written. E.g. 0 or 10.5.
                rounding_decimal_places (int, optional): Optional setting for setting rounding in the
                    decimal places for value.
                sleep_after (float, optional): Optional setting for the delay in seconds that the function will wait
                    after writing the register. Useful in not overloading the driver when many commands are being sent.
            Returns:
                None
        """
        if self._is_uart:
            self._write_reg_uart(reg_id, value, rounding_decimal_places=rounding_decimal_places, sleep_after=sleep_after)
        else:
            self._write_reg_i2c(reg_id, value, sleep_after=sleep_after)

    def read_register(self, reg_id: int, timeout=1) -> float:
        """
            Reads a value from a given register.
            Works for both I2C and UART connected pumps.

            Args:
                reg_id (int): The register ID (number) to be read. E.g. 39 for Digital pressure measurement.
                timeout (float, optional): Optional setting for the timeout in seconds that the function will wait
                    for a response. Useful in preventing the program from stopping if the board is not responding.
            Returns:
                float: The value of the given register.
        """
        if self._is_uart:
            return self._read_register_uart(reg_id, timeout=timeout)
        else:
            return self._read_register_i2c(reg_id, timeout=timeout)

    def disconnect_pump(self):
        """
            Disconnects a pump.
            Works for both I2C and UART connected pumps.

            Args:

            Returns:
                None
        """
        if self._is_uart:
            self._disconnect_pump_uart()
        else:
            self._disconnect_pump_i2c()

    def streaming_mode_disable(self):
        """
            Disables streaming mode output of the driver.
            Works for both I2C and UART connected pumps.

            Args:

            Returns:
                None
        """
        self.write_reg(LVRegister.STREAM_MODE, LVStreamingModes.DISABLED)

    def streaming_mode_enable(self):
        """
            Enables streaming mode output of the driver.
            Works for both I2C and UART connected pumps.

            Args:

            Returns:
                None
        """
        if self._is_uart:
            self.write_reg(LVRegister.STREAM_MODE, LVStreamingModes.STREAMING_UART)
        else:
            self.write_reg(LVRegister.STREAM_MODE, LVStreamingModes.STREAMING_I2C)

    def streaming_mode_get_output(self, timeout=1) -> list[float]:
        """
            Returns the streaming mode output of the pump of the driver (as listed in LVStreamingModeOutputIndexes):
             - GP - [PUMP_ENABLED,VOLTAGE,CURRENT,FREQUENCY,ANA_A,ANA_B (analog pressure) / digital pressure,ANA_C,FLOW]
             - SPM - [PUMP_ENABLED,VOLTAGE,CURRENT,FREQUENCY,0,digital pressure,ANA_C,0]
            Works for both I2C and UART connected pumps.

            Args:
                timeout (float, optional): Optional setting for the timeout in seconds that the function will wait
                    for a response. Useful in preventing the program from stopping if the board is not responding.
            Returns:
                list[float]: The streaming mode output.
        """
        if self._is_uart:
            return self._streaming_mode_get_output_uart(timeout=timeout)
        else:
            return self._streaming_mode_get_output_i2c(timeout=timeout)

    def set_manual_power_control_with_set_val(self):
        """
            Configures the pump to have manual power control.
            The value for the target power is set by the SetVal register.
            Works for both I2C and UART connected pumps.

            Args:

            Returns:
                None
        """
        # set the pump to manual control mode
        self.write_reg(LVRegister.CONTROL_MODE, LVControlMode.MANUAL)
        # set the drive power input to register 23
        self.write_reg(LVRegister.MANUAL_MODE_SETPOINT_SOURCE, LVControlSource.SETVAL)

    def set_pid_digital_pressure_control_with_set_val(self, p_term=5, i_term=10, d_term=0):
        """
            Configures the pump to use PID to track target digital pressure. The value for the target pressure is set
            by the SetVal register.Note that digital pressure only available on the SPM and the Development Kit.
            Works for both I2C and UART connected pumps.

            Args:
                p_term (int, optional): Optional setting for the proportional gain of the PID controller.
                i_term (int, optional): Optional setting for the integral gain of the PID controller.
                d_term (int, optional): Optional setting for the differential gain of the PID controller.
            Returns:
                None
        """
        # set the pump to pid control mode
        self.write_reg(LVRegister.CONTROL_MODE, LVControlMode.PID)
        # set the pid tracking value to digital pressure. Note that this only works on the SPM and Dev kit
        self.write_reg(LVRegister.PID_MODE_MEAS_SOURCE, LVControlSource.DIGITAL_PRESSURE)
        # set the pressure target input to register 23
        self.write_reg(LVRegister.PID_MODE_SETPOINT_SOURCE, LVControlSource.SETVAL)

        # set PID values
        self.write_reg(LVRegister.PID_PROPORTIONAL_COEFF, p_term)
        self.write_reg(LVRegister.PID_INTEGRAL_COEFF, i_term)
        self.write_reg(LVRegister.PID_DIFFERENTIAL_COEFF, d_term)

    def set_pid_analog_pressure_control_with_set_val(self, p_term=5, i_term=10, d_term=0):
        """
            Configures the pump to use PID to track target analog pressure. The value for the target pressure is set
            by the SetVal register.Note that analog pressure only available on the Evaluation Kit.
            Works for both I2C and UART connected pumps.

            Args:
                p_term (int, optional): Optional setting for the proportional gain of the PID controller.
                i_term (int, optional): Optional setting for the integral gain of the PID controller.
                d_term (int, optional): Optional setting for the differential gain of the PID controller.
            Returns:
                None
        """
        # set the pump to pid control mode
        self.write_reg(LVRegister.CONTROL_MODE, LVControlMode.PID)
        # set the pid tracking value to the analog pressure sensor on the Eval kit
        self.write_reg(LVRegister.PID_MODE_MEAS_SOURCE, LVControlSource.ANA_B)
        # set the pressure target input to register 23
        self.write_reg(LVRegister.PID_MODE_SETPOINT_SOURCE, LVControlSource.SETVAL)

        # set PID values
        self.write_reg(LVRegister.PID_PROPORTIONAL_COEFF, p_term)
        self.write_reg(LVRegister.PID_INTEGRAL_COEFF, i_term)
        self.write_reg(LVRegister.PID_DIFFERENTIAL_COEFF, d_term)

    def set_pid_flow_control_with_set_val(self, p_term=5, i_term=10, d_term=0):
        """
            Configures the pump to use PID to track target flow (from an external flow sensor). The value for the
            target flow is set by the SetVal register. Note that flow is only available with the GP driver.

            Args:
                p_term (int, optional): Optional setting for the proportional gain of the PID controller.
                i_term (int, optional): Optional setting for the integral gain of the PID controller.
                d_term (int, optional): Optional setting for the differential gain of the PID controller.
            Returns:
                None
        """
        # set the pump to pid control mode
        self.write_reg(LVRegister.CONTROL_MODE, LVControlMode.PID)
        # set the pid tracking value to the external flow sensor for the Dev kit / Eval kit
        self.write_reg(LVRegister.PID_MODE_MEAS_SOURCE, LVControlSource.FLOW)
        # set the pressure target input to register 23
        self.write_reg(LVRegister.PID_MODE_SETPOINT_SOURCE, LVControlSource.SETVAL)

        # set PID values
        self.write_reg(LVRegister.PID_PROPORTIONAL_COEFF, p_term)
        self.write_reg(LVRegister.PID_INTEGRAL_COEFF, i_term)
        self.write_reg(LVRegister.PID_DIFFERENTIAL_COEFF, d_term)

    def configure_spm_i2c_only_mode(self, i2c_address=37):
        """
            Configures an SPM to work in I2C only mode with a given I2C address. This should be used when multiple
            SPMs are controlled on the same I2C bus. The SPMs should be configured with different I2C addresses.
            Works for both I2C and UART connected pumps.

            Args:
                i2c_address (int, optional): Optional setting the I2C address for the board.
            Returns:
                None
        """
        # set I2C address
        self.write_reg(LVRegister.DRIVER_I2C_ADDRESS, i2c_address)
        # disable I2C / UART autodiscover and set I2C only mode
        self.write_reg(LVRegister.COMMUNICATION_INTERFACE, LVSPMCommunicationsProtocol.ONLY_I2C)

    def store_current_settings_to_board(self, verbose=True):
        """
            Stores the current setting to the board. This can be used to save a drive configuration on system boot-up
            or to configure some settings which only take effect on startup (e.g. I2C address or GPIO pin mode).
            Works for both I2C and UART connected pumps.

            Args:
                verbose (bool, optional): Optional setting prompting the user to reboot the board.
            Returns:
                None
        """
        # save settings to board
        self.write_reg(LVRegister.STORE_CURRENT_SETTINGS, 1)
        # allow some time for the settings to be stored
        time.sleep(1)

        if verbose:
            # prompt the user to reboot the board if needed
            print("Settings have been stored to board.")
            print("If any of the settings require rebooting please power cycle the board.")

    def restore_default_settings(self):
        """
            Restores the default settings to the board.
            Works for both I2C and UART connected pumps.

            Args:

            Returns:
                None
        """
        # read the board type
        device_type = self.read_register(LVRegister.DEVICE_TYPE)

        # depending on the device type write the relevant default values
        if device_type == LVDeviceType.GP:
            for index in range(LVRegister_get_number_settings()):
                default_value = LVRegister_get_default_reg_value_gp(index)
                if default_value is not None:
                    self.write_reg(index, default_value)

        if device_type == LVDeviceType.SPM:
            for index in range(LVRegister_get_number_settings()):
                default_value = LVRegister_get_default_reg_value_spm(index)
                if default_value is not None:
                    self.write_reg(index, default_value)

    def set_status_led_colour(self, red: int, green: int, blue: int):
        """
            Sets the status LED colour by R, G and B values. Uses 5-5-5 bit colour. It is not recommended to use
            colours that are close to red as red is used to indicate errors.
            Works for both I2C and UART connected pumps.

            Args:
                red (int): The red component of the colour. Value between 0 and 31.
                green (int): The green component of the colour. Value between 0 and 31.
                blue (int): The blue component of the colour. Value between 0 and 31.
            Returns:
                None
        """
        # limit values to 0 - 31
        if red > 31:
            red = 31
        if red < 0:
            red = 0
        if green > 31:
            green = 31
        if green < 0:
            green = 0
        if blue > 31:
            blue = 31
        if blue < 0:
            blue = 0

        # the led register uses 5-5-5bit colour
        led_register_val = red * 32 * 32 + green * 32 + blue
        self.write_reg(LVRegister.STATUS_LED_COLOUR, led_register_val)

    # -----------------------------------------------------------------------------
    # Initialisation / de-initialisation functions
    # -----------------------------------------------------------------------------

    def __init__(self):
        self._is_uart = None
        self._com_port = None
        self._i2c_address = None

    def __del__(self):
        self.disconnect_pump()

    # -----------------------------------------------------------------------------
    # Private variables
    # -----------------------------------------------------------------------------

    # static variable for the MCP2221 usb to I2C interface as this is shared for all I2C pumps
    _i2c_port = None
    # static variable for all I2C device addresses connected so we can monitor how many devices are left
    _i2c_target_addresses = []

    # -----------------------------------------------------------------------------
    # Private functions
    # -----------------------------------------------------------------------------

    def _write_reg_uart(self, reg_id: int, value, rounding_decimal_places=3, sleep_after=0.005):
        if LVRegister_is_int(reg_id):
            self._com_port.write(f'#W{reg_id},{round(value, rounding_decimal_places)}\n'.encode('ascii'))
        else:
            self._com_port.write(f'#W{reg_id},{int(value)}\n'.encode('ascii'))
        if sleep_after != 0:
            time.sleep(sleep_after)

    def _read_register_uart(self, reg_id: int, timeout=1) -> float:
        self._com_port.read_all()   # flushes the buffer
        self._com_port.write(f'#R{reg_id}\n'.encode('ascii'))
        start_time = float(time.time())
        while float(time.time()) - start_time < timeout:
            line_chars = self._com_port.readline()
            if any(char >= 128 for char in line_chars):
                # Ignore this line, as we've read a
                # byte that can't be decoded
                continue
            line = line_chars.decode('ascii')
            if f'#R{reg_id},' in line:
                return float(line.split(',')[1])

        raise Exception("Didn't get expected response from driver")

    def _connect_pump_uart(self, com_port: str):
        self._com_port = serial.Serial(port=com_port,
                                       baudrate=115200,
                                       bytesize=8,
                                       timeout=2,
                                       stopbits=serial.STOPBITS_ONE)

    def _disconnect_pump_uart(self):
        self._is_uart = None
        # if pump is already disconnected or was never connected there is nothing to do
        if self._com_port is None:
            return

        self._com_port.close()
        del self._com_port
        self._com_port = None

    def _streaming_mode_get_output_uart(self, timeout=1) -> list[float]:
        self._com_port.read_all()   # flushes the buffer
        start_time = float(time.time())
        while float(time.time()) - start_time < timeout:
            line_chars = self._com_port.readline()
            if any(char >= 128 for char in line_chars):
                # Ignore this line, as we've read a
                # byte that can't be decoded
                continue
            line = line_chars.decode('ascii')
            if "#S" in line:
                all_values = line[2:-1].split(',')  # remove the "#S" at the beginning
                return [float(all_values[0]),  # pump enabled
                        float(all_values[1]),  # voltage
                        float(all_values[2]),  # current
                        float(all_values[3]),  # frequency
                        float(all_values[4]),  # ana a (GP) / 0 (SPM)
                        float(all_values[5]),  # ana b (analog pressure) / digital pressure
                        float(all_values[6]),  # ana c
                        float(all_values[7])]  # flow (GP) / 0 (SPM)

    def _write_reg_i2c(self, reg_id: int, value, sleep_after=0.005):
        data_to_send = struct.pack("B", reg_id)
        if LVRegister_is_int(reg_id):
            data_to_send = data_to_send + struct.pack("h", int(value))
        else:
            data_to_send = data_to_send + struct.pack("f", float(value))
        LVDiscPump._i2c_port.I2C_write(addr=self._i2c_address, data=data_to_send)
        if sleep_after != 0:
            time.sleep(sleep_after)

    def _read_register_i2c(self, reg_id: int, timeout=1) -> float:
        data_to_send = struct.pack("B", reg_id + 128)
        LVDiscPump._i2c_port.I2C_write(addr=self._i2c_address, data=data_to_send)
        if LVRegister_is_int(reg_id):
            data_received = LVDiscPump._i2c_port.I2C_read(addr=self._i2c_address, size=2, timeout_ms=1000*timeout)
            return float(struct.unpack("h", bytes(data_received[0:2]))[0])
        else:
            data_received = LVDiscPump._i2c_port.I2C_read(addr=self._i2c_address, size=4, timeout_ms=1000*timeout)
            return float(struct.unpack("f", bytes(data_received[0:4]))[0])

    def _connect_pump_i2c(self, i2c_address: int):
        self._i2c_address = i2c_address
        LVDiscPump._i2c_target_addresses.append(self._i2c_address)
        if LVDiscPump._i2c_port is None:
            LVDiscPump._i2c_port = EasyMCP2221.Device()

    def _disconnect_pump_i2c(self):
        self._is_uart = None
        # if pump is already disconnected or was never connected there is nothing to do
        if self._i2c_address is None:
            return

        LVDiscPump._i2c_target_addresses.remove(self._i2c_address)
        self._i2c_address = None
        # if there are no mode I2C devices connected to the I2C chip, disconnect from it
        if LVDiscPump._i2c_port is not None and len(LVDiscPump._i2c_target_addresses) == 0:
            del LVDiscPump._i2c_port
            LVDiscPump._i2c_port = None

    def _streaming_mode_get_output_i2c(self, timeout=1) -> list[float]:
        data_received = LVDiscPump._i2c_port.I2C_read(addr=self._i2c_address, size=29, timeout_ms=1000*timeout)
        return [float(struct.unpack("h", bytes(data_received[0:2]))[0]),  # pump enabled
                float(struct.unpack("f", bytes(data_received[2:6]))[0]),  # voltage
                float(struct.unpack("f", bytes(data_received[6:10]))[0]),  # current
                float(struct.unpack("h", bytes(data_received[10:12]))[0]),  # freq
                float(struct.unpack("f", bytes(data_received[12:16]))[0]),  # 0
                float(struct.unpack("f", bytes(data_received[16:20]))[0]),  # digital pressure
                float(struct.unpack("f", bytes(data_received[20:24]))[0]),  # ana_c
                float(struct.unpack("f", bytes(data_received[24:28]))[0])]  # 0



