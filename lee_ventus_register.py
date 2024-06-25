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

from enum import IntEnum


# -----------------------------------------------------------------------------
# Useful values
# -----------------------------------------------------------------------------


class LVControlSource(IntEnum):
    SETVAL = 0
    ANA_A = 1
    ANA_B = 2
    ANA_C = 3
    FLOW = 4
    DIGITAL_PRESSURE = 5


class LVControlMode(IntEnum):
    MANUAL = 0
    PID = 1
    BANG_BANG = 2


class LVStreamingModes(IntEnum):
    DISABLED = 0
    STREAMING_UART = 1
    STREAMING_I2C = 2


class LVStreamingModeOutputIndexes(IntEnum):
    PUMP_ENABLED = 0
    VOLTAGE = 1
    CURRENT = 2
    FREQUENCY = 3
    ANA_A = 4
    PRESSURE = 5
    ANA_B = 5
    ANA_C = 6
    FLOW = 7


class LVSPMCommunicationsProtocol(IntEnum):
    AUTODETECT_UART_I2C = 1849
    ONLY_UART = 1892
    ONLY_I2C = 1935


class LVDeviceType(IntEnum):
    FAST_RESPONSE_OBSOLETE = 1
    GP = 2
    SPM = 3


class LVMeasUnits(IntEnum):
    DIGITAL_PRESSURE_mBar = 0
    DIGITAL_PRESSURE_mmHg = 1
    DIGITAL_PRESSURE_PSI = 2
    DIGITAL_PRESSURE_kPa = 3
    DIGITAL_PRESSURE_inHg = 4
    DIGITAL_PRESSURE_inH2O = 5
    DIGITAL_PRESSURE_cmH2O = 6

    FLOW_L_PER_MIN = 0
    FLOW_mL_PER_MIN = 1
    FLOW_uL_PER_MIN = 2
    FLOW_nL_PER_MIN = 3


class LVGpioPinMode(IntEnum):
    OUTPUT_FAST_MODE_DEF_HIGH = 0
    OUTPUT_FAST_MODE_DEF_LOW = 1
    OUTPUT_SLOW_MODE_DEF_HIGH = 2
    OUTPUT_SLOW_MODE_DEF_LOW = 3
    INPUT_NO_PULL = 4
    INPUT_PULL_UP = 5
    INPUT_PULL_DOWN = 6
    DISABLED = 7


class LVGpioStaticStates(IntEnum):
    STATIC_OFF = 0
    STATIC_ON = -1

# ***********************************************************************************
# * Registers list below
# ***********************************************************************************


class LVRegister(IntEnum):
    # -----------------------------------------------------------------------------
    # General settings
    # -----------------------------------------------------------------------------

    PUMP_ENABLE = 0
    POWER_LIMIT_MILLIWATTS = 1

    STREAM_MODE = 2

    # -----------------------------------------------------------------------------
    # Measurements
    # -----------------------------------------------------------------------------

    MEAS_DRIVE_VOLTS = 3
    MEAS_DRIVE_MILLIAMPS = 4
    MEAS_DRIVE_MILLIWATTS = 5
    MEAS_DRIVE_FREQ = 6
    MEAS_ANA_A = 7
    MEAS_ANA_B = 8
    MEAS_ANA_C = 9
    MEAS_FLOW = 32
    MEAS_DIGITAL_PRESSURE = 39

    # -----------------------------------------------------------------------------
    # Measurement settings
    # -----------------------------------------------------------------------------

    SET_VAL = 23

    ANA_A_OFFSET = 24
    ANA_A_GAIN = 25
    ANA_B_OFFSET = 26
    ANA_B_GAIN = 27
    ANA_C_OFFSET = 28
    ANA_C_GAIN = 29

    DIGITAL_PRESSURE_OFFSET = 40
    DIGITAL_PRESSURE_MEAS_UNIT = 58

    FLOW_MEAS_UNIT = 59

    # -----------------------------------------------------------------------------
    # Control settings
    # -----------------------------------------------------------------------------

    # Control mode
    CONTROL_MODE = 10

    # Manual control settings
    MANUAL_MODE_SETPOINT_SOURCE = 11

    # PID control settings
    PID_MODE_SETPOINT_SOURCE = 12
    PID_MODE_MEAS_SOURCE = 13
    PID_PROPORTIONAL_COEFF = 14
    PID_INTEGRAL_COEFF = 15
    PID_INTEGRAL_LIMIT_COEFF = 16
    PID_DIFFERENTIAL_COEFF = 17
    RESET_PID_ON_TURNON = 33

    # Bang bang control settings
    BANG_BANG_MEAS_SOURCE = 18
    BANG_BANG_LOWER_THRESH = 19
    BANG_BANG_UPPER_THRESH = 20
    BANG_BANG_LOWER_POWER_MILLIWATTS = 21
    BANG_BANG_UPPER_POWER_MILLIWATTS = 22

    # -----------------------------------------------------------------------------
    # Miscellaneous settings
    # -----------------------------------------------------------------------------

    STORE_CURRENT_SETTINGS = 30

    ERROR_CODE = 31

    USE_FREQUENCY_TRACKING = 34
    MANUAL_DRIVE_FREQUENCY = 35

    FIRMWARE_VERSION = 36
    DEVICE_TYPE = 37
    FIRMWARE_MINOR_VERSION = 38

    STATUS_LED_COLOUR = 57

    # -----------------------------------------------------------------------------
    # Communication settings
    # -----------------------------------------------------------------------------

    DRIVER_I2C_ADDRESS = 42
    COMMUNICATION_INTERFACE = 43

    # -----------------------------------------------------------------------------
    # Communication settings
    # -----------------------------------------------------------------------------

    GPIO_A_PIN_MODE = 44
    GPIO_A_STATE = 45
    GPIO_A_PULSE_DURATION = 46
    GPIO_A_PULSE_PERIOD = 47

    GPIO_B_PIN_MODE = 48
    GPIO_B_STATE = 49
    GPIO_B_PULSE_DURATION = 50
    GPIO_B_PULSE_PERIOD = 51

    GPIO_C_PIN_MODE = 52
    GPIO_C_STATE = 53
    GPIO_C_PULSE_DURATION = 54
    GPIO_C_PULSE_PERIOD = 55

    GPIO_D_STATE = 56


# -----------------------------------------------------------------------------
# Internal functions
# -----------------------------------------------------------------------------


def LVRegister_is_int(reg_id: int):
    return _is_register_int[reg_id]


def LVRegister_is_float(reg_id: int):
    return not _is_register_int[reg_id]


def LVRegister_get_number_settings():
    return len(_default_values_spm)


def LVRegister_get_default_reg_value_spm(reg_id: int):
    return _default_values_spm[reg_id]


def LVRegister_get_default_reg_value_gp(reg_id: int):
    return _default_values_gp[reg_id]

# -----------------------------------------------------------------------------
# Internal variables
# -----------------------------------------------------------------------------


_default_values_spm = [1,  # PUMP_ENABLE = 0
                       1000,  # POWER_LIMIT_MILLIWATTS = 1
                       0,  # STREAM_MODE = 2
                       None,  # MEAS_DRIVE_VOLTS = 3
                       None,  # MEAS_DRIVE_MILLIAMPS = 4
                       None,  # MEAS_DRIVE_MILLIWATTS = 5
                       None,  # MEAS_DRIVE_FREQ = 6
                       None,  # MEAS_ANA_1 = 7
                       None,  # MEAS_ANA_2 = 8
                       None,  # MEAS_ANA_3 = 9
                       0,  # CONTROL_MODE = 10
                       3,  # MANUAL_MODE_SETPOINT_SOURCE = 11
                       3,  # PID_MODE_SETPOINT_SOURCE = 12
                       5,  # PID_MODE_MEAS_SOURCE = 13
                       5,  # PID_PROPORTIONAL_COEFF = 14
                       10,  # PID_INTEGRAL_COEFF = 15
                       1400,  # PID_INTEGRAL_LIMIT_COEFF = 16
                       0,  # PID_DIFFERENTIAL_COEFF = 17
                       5,  # BANG_BANG_MEAS_SOURCE = 18
                       10,  # BANG_BANG_LOWER_THRESH = 19
                       50,  # BANG_BANG_UPPER_THRESH = 20
                       1000,  # BANG_BANG_LOWER_POWER_MILLIWATTS = 21
                       0,  # BANG_BANG_UPPER_POWER_MILLIWATTS = 22
                       250,  # SET_VAL = 23
                       None,  # ANA_1_OFFSET = 24
                       None,  # ANA_1_GAIN = 25
                       None,  # ANA_2_OFFSET = 26
                       None,  # ANA_2_GAIN = 27
                       0,  # ANA_3_OFFSET = 28
                       1000,  # ANA_3_GAIN = 29
                       0,  # STORE_CURRENT_SETTINGS = 30
                       None,  # ERROR_CODE = 31
                       None,  # MEAS_FLOW = 32
                       1,  # RESET_PID_ON_TURNON = 33
                       1,  # USE_FREQUENCY_TRACKING = 34
                       21000,  # MANUAL_DRIVE_FREQUENCY = 35
                       None,  # FIRMWARE_VERSION = 36
                       None,  # DEVICE_TYPE = 37
                       None,  # FIRMWARE_MINOR_VERSION = 38
                       None,  # MEAS_DIGITAL_PRESSURE = 39
                       0,  # DIGITAL_PRESSURE_OFFSET = 40
                       None,  # Reserved for future use = 41
                       37,  # DRIVER_I2C_ADDRESS = 42
                       1849,  # COMMUNICATION_INTERFACE = 43
                       None,  # GPIO_A_PIN_MODE = 44
                       None,  # GPIO_A_STATE = 45
                       None,  # GPIO_A_PULSE_DURATION = 46
                       None,  # GPIO_A_PULSE_PERIOD = 47
                       None,  # GPIO_B_PIN_MODE = 48
                       None,  # GPIO_B_STATE = 49
                       None,  # GPIO_B_PULSE_DURATION = 50
                       None,  # GPIO_B_PULSE_PERIOD = 51
                       None,  # GPIO_C_PIN_MODE = 52
                       None,  # GPIO_C_STATE = 53
                       None,  # GPIO_C_PULSE_DURATION = 54
                       None,  # GPIO_C_PULSE_PERIOD = 55
                       None,  # GPIO_D_STATE = 56
                       992,  # STATUS_LED_COLOUR = 57
                       0,  # DIGITAL_PRESSURE_MEAS_UNIT = 58
                       None  # FLOW_MEAS_UNIT = 59
                       ]

_default_values_gp = [1,  # PUMP_ENABLE = 0
                      1000,  # POWER_LIMIT_MILLIWATTS = 1
                      0,  # STREAM_MODE = 2
                      None,  # MEAS_DRIVE_VOLTS = 3
                      None,  # MEAS_DRIVE_MILLIAMPS = 4
                      None,  # MEAS_DRIVE_MILLIWATTS = 5
                      None,  # MEAS_DRIVE_FREQ = 6
                      None,  # MEAS_ANA_1 = 7
                      None,  # MEAS_ANA_2 = 8
                      None,  # MEAS_ANA_3 = 9
                      0,  # CONTROL_MODE = 10
                      1,  # MANUAL_MODE_SETPOINT_SOURCE = 11
                      1,  # PID_MODE_SETPOINT_SOURCE = 12
                      5,  # PID_MODE_MEAS_SOURCE = 13
                      5,  # PID_PROPORTIONAL_COEFF = 14
                      10,  # PID_INTEGRAL_COEFF = 15
                      1400,  # PID_INTEGRAL_LIMIT_COEFF = 16
                      0,  # PID_DIFFERENTIAL_COEFF = 17
                      5,  # BANG_BANG_MEAS_SOURCE = 18
                      10,  # BANG_BANG_LOWER_THRESH = 19
                      50,  # BANG_BANG_UPPER_THRESH = 20
                      1000,  # BANG_BANG_LOWER_POWER_MILLIWATTS = 21
                      0,  # BANG_BANG_UPPER_POWER_MILLIWATTS = 22
                      250,  # SET_VAL = 23
                      0,  # ANA_1_OFFSET = 24
                      1000,  # ANA_1_GAIN = 25
                      -821,  # ANA_2_OFFSET = 26
                      2130,  # ANA_2_GAIN = 27
                      0,  # ANA_3_OFFSET = 28
                      1000,  # ANA_3_GAIN = 29
                      0,  # STORE_CURRENT_SETTINGS = 30
                      None,  # ERROR_CODE = 31
                      None,  # MEAS_FLOW = 32
                      1,  # RESET_PID_ON_TURNON = 33
                      1,  # USE_FREQUENCY_TRACKING = 34
                      21000,  # MANUAL_DRIVE_FREQUENCY = 35
                      None,  # FIRMWARE_VERSION = 36
                      None,  # DEVICE_TYPE = 37
                      None,  # FIRMWARE_MINOR_VERSION = 38
                      None,  # MEAS_DIGITAL_PRESSURE = 39
                      0,  # DIGITAL_PRESSURE_OFFSET = 40
                      None,  # Reserved for future use = 41
                      None,  # DRIVER_I2C_ADDRESS = 42
                      None,  # COMMUNICATION_INTERFACE = 43
                      5,  # GPIO_A_PIN_MODE = 44
                      None,  # GPIO_A_STATE = 45
                      0,  # GPIO_A_PULSE_DURATION = 46
                      0,  # GPIO_A_PULSE_PERIOD = 47
                      1,  # GPIO_B_PIN_MODE = 48
                      0,  # GPIO_B_STATE = 49
                      0,  # GPIO_B_PULSE_DURATION = 50
                      0,  # GPIO_B_PULSE_PERIOD = 51
                      3,  # GPIO_C_PIN_MODE = 52
                      0,  # GPIO_C_STATE = 53
                      0,  # GPIO_C_PULSE_DURATION = 54
                      0,  # GPIO_C_PULSE_PERIOD = 55
                      None,  # GPIO_D_STATE = 56
                      992,  # STATUS_LED_COLOUR = 57
                      0,  # DIGITAL_PRESSURE_MEAS_UNIT = 58
                      1  # FLOW_MEAS_UNIT = 59
                      ]

_is_register_int = [True,  # PUMP_ENABLE = 0
                    True,  # POWER_LIMIT_MILLIWATTS = 1
                    True,  # STREAM_MODE = 2
                    False,  # MEAS_DRIVE_VOLTS = 3
                    False,  # MEAS_DRIVE_MILLIAMPS = 4
                    False,  # MEAS_DRIVE_MILLIWATTS = 5
                    True,  # MEAS_DRIVE_FREQ = 6
                    False,  # MEAS_ANA_1 = 7
                    False,  # MEAS_ANA_2 = 8
                    False,  # MEAS_ANA_3 = 9
                    True,  # CONTROL_MODE = 10
                    True,  # MANUAL_MODE_SETPOINT_SOURCE = 11
                    True,  # PID_MODE_SETPOINT_SOURCE = 12
                    True,  # PID_MODE_MEAS_SOURCE = 13
                    False,  # PID_PROPORTIONAL_COEFF = 14
                    False,  # PID_INTEGRAL_COEFF = 15
                    False,  # PID_INTEGRAL_LIMIT_COEFF = 16
                    False,  # PID_DIFFERENTIAL_COEFF = 17
                    True,  # BANG_BANG_MEAS_SOURCE = 18
                    False,  # BANG_BANG_LOWER_THRESH = 19
                    False,  # BANG_BANG_UPPER_THRESH = 20
                    False,  # BANG_BANG_LOWER_POWER_MILLIWATTS = 21
                    False,  # BANG_BANG_UPPER_POWER_MILLIWATTS = 22
                    False,  # SET_VAL = 23
                    False,  # ANA_1_OFFSET = 24
                    False,  # ANA_1_GAIN = 25
                    False,  # ANA_2_OFFSET = 26
                    False,  # ANA_2_GAIN = 27
                    False,  # ANA_3_OFFSET = 28
                    False,  # ANA_3_GAIN = 29
                    True,  # STORE_CURRENT_SETTINGS = 30
                    True,  # ERROR_CODE = 31
                    False,  # MEAS_FLOW = 32
                    True,  # RESET_PID_ON_TURNON = 33
                    True,  # USE_FREQUENCY_TRACKING = 34
                    True,  # MANUAL_DRIVE_FREQUENCY = 35
                    True,  # FIRMWARE_VERSION = 36
                    True,  # DEVICE_TYPE = 37
                    True,  # FIRMWARE_MINOR_VERSION = 38
                    False,  # MEAS_DIGITAL_PRESSURE = 39
                    False,  # DIGITAL_PRESSURE_OFFSET = 40
                    False,  # Reserved for future use = 41
                    True,  # DRIVER_I2C_ADDRESS = 42
                    True,  # COMMUNICATION_INTERFACE = 43
                    True,  # GPIO_A_PIN_MODE = 44
                    True,  # GPIO_A_STATE = 45
                    True,  # GPIO_A_PULSE_DURATION = 46
                    True,  # GPIO_A_PULSE_PERIOD = 47
                    True,  # GPIO_B_PIN_MODE = 48
                    True,  # GPIO_B_STATE = 49
                    True,  # GPIO_B_PULSE_DURATION = 50
                    True,  # GPIO_B_PULSE_PERIOD = 51
                    True,  # GPIO_C_PIN_MODE = 52
                    True,  # GPIO_C_STATE = 53
                    True,  # GPIO_C_PULSE_DURATION = 54
                    True,  # GPIO_C_PULSE_PERIOD = 55
                    True,  # GPIO_D_STATE = 56
                    True,  # STATUS_LED_COLOUR = 57
                    True,  # DIGITAL_PRESSURE_MEAS_UNIT = 58
                    True  # FLOW_MEAS_UNIT = 59
                    ]
