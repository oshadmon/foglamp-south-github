from pyftdi.i2c import I2cController, I2cNackError, I2cPort
try:
    import struct
except ImportError:
    import ustruct as struct


#pylint: disable=bad-whitespace
# Internal constants:
_INA219_DEFAULT_ADDRESS           = 0x44

_REG_CONFIG                       = 0x00
_REG_SHUNTVOLTAGE                 = 0x01
_REG_BUSVOLTAGE                   = 0x02
_REG_POWER                        = 0x03
_REG_CURRENT                      = 0x04
_REG_CALIBRATION                  = 0x05

_CONFIG_BVOLTAGERANGE_32V         = 0x2000
_CONFIG_SADCRES_12BIT_1S_532US    = 0x0018
_CONFIG_GAIN_8_320MV              = 0x1800
_CONFIG_BADCRES_12BIT             = 0x0400
_CONFIG_MODE_SANDBVOLT_CONTINUOUS = 0x0007

"""
=== _to_signed function ===
"""
def _to_signed(num):
    if num > 0x7FFF:
        num -= 0x10000
    return num

"""
====== INIT ===== 
"""
# Instanciate an I2C controller
i2c = I2cController()

# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c.configure('ftdi://ftdi:232h:FT2BZGR5/1')

try: 
    slave = i2c.get_port(_INA219_DEFAULT_ADDRESS)
except: 
    print('Unable to get Port for %s' %_INA219_DEFAULT_ADDRESS)
    exit(1)

i2c_addr =_INA219_DEFAULT_ADDRESS
# Multiplier in mA used to determine current from raw reading
_current_lsb = 0
# Multiplier in W used to determine power from raw reading
_power_lsb = 0
# Set chip to known config values to start
_cal_value = 4096
# call set_calibration_32V_2A

"""
=== set_calibration_32V_2A ===
"""
# By default we use a pretty huge range for the input voltage,
# which probably isn't the most appropriate choice for system
# that don't use a lot of power.  But all of the calculations
# are shown below if you want to change the settings.  You will
# also need to change any relevant register settings, such as
# setting the VBUS_MAX to 16V instead of 32V, etc.

# VBUS_MAX = 32V      (Assumes 32V, can also be set to 16V)
# VSHUNT_MAX = 0.32   (Assumes Gain 8, 320mV, can also be 0.16, 0.08, 0.04)
# RSHUNT = 0.1 (Resistor value in ohms)

# 1. Determine max possible current
# MaxPossible_I = VSHUNT_MAX / RSHUNT
# MaxPossible_I = 3.2A

# 2. Determine max expected current
# MaxExpected_I = 2.0A

# 3. Calculate possible range of LSBs (Min = 15-bit, Max = 12-bit)
# MinimumLSB = MaxExpected_I/32767
# MinimumLSB = 0.000061(61uA per bit)
# MaximumLSB = MaxExpected_I/4096
# MaximumLSB = 0,000488(488uA per bit)

# 4. Choose an LSB between the min and max values
#    (Preferrably a roundish number close to MinLSB)
# CurrentLSB = 0.0001 (100uA per bit)
_current_lsb = .1 # Current LSB = 100uA per bit

# 5. Compute the calibration register
# Cal = trunc (0.04096 / (Current_LSB * RSHUNT))
# Cal = 4096 (0x1000)

_cal_value = 4096

# 6. Calculate the power LSB
# PowerLSB = 20 * CurrentLSB
# PowerLSB = 0.002 (2mW per bit)
_power_lsb = .002 # Power LSB = 2mW per bit

# 7. Compute the maximum current and shunt voltage values before overflow
#
# Max_Current = Current_LSB * 32767
# Max_Current = 3.2767A before overflow
#
# If Max_Current > Max_Possible_I then
#    Max_Current_Before_Overflow = MaxPossible_I
# Else
#    Max_Current_Before_Overflow = Max_Current
# End If
#
# Max_ShuntVoltage = Max_Current_Before_Overflow * RSHUNT
# Max_ShuntVoltage = 0.32V
#
# If Max_ShuntVoltage >= VSHUNT_MAX
#    Max_ShuntVoltage_Before_Overflow = VSHUNT_MAX
# Else
#    Max_ShuntVoltage_Before_Overflow = Max_ShuntVoltage
# End If

# 8. Compute the Maximum Power
# MaximumPower = Max_Current_Before_Overflow * VBUS_MAX
# MaximumPower = 3.2 * 32V
# MaximumPower = 102.4W

"""
=== _call write_register 1 ===
"""

seq=bytearray([(_cal_value >> 8) & 0xFF, _cal_value & 0xFF])
slave.write_to(_REG_CALIBRATION, seq)

"""
=== Back to set_calibration_32V_2A ===
"""
# Set Config register to take into account the settings above
config = _CONFIG_BVOLTAGERANGE_32V | \
         _CONFIG_GAIN_8_320MV | \
         _CONFIG_BADCRES_12BIT | \
         _CONFIG_SADCRES_12BIT_1S_532US | \
         _CONFIG_MODE_SANDBVOLT_CONTINUOUS
"""
=== call write_register II === 
"""
seq=bytearray([(config >> 8) & 0xFF, config & 0xFF])
slave.write_to(_REG_CONFIG ,seq)


"""
=== bus_voltage === 
"""
buf = slave.read_from(_REG_BUSVOLTAGE, 3)
raw_voltage = (buf[0] << 8) | (buf[1])
voltage_mv = _to_signed(raw_voltage >> 3) * 4
bus_voltage = voltage_mv * 0.001
print("Bus Voltage:   {} V".format(bus_voltage))

""" 
=== shunt_vontage === 
"""
buf = slave.read_from(_REG_SHUNTVOLTAGE, 3)
raw_shunt_voltage = (buf[0] << 8) | (buf[1])
shunt_voltage_mv = _to_signed(raw_shunt_voltage)
shunt_voltage = shunt_voltage_mv * 0.00001
print("Shunt Voltage: {} mV".format(shunt_voltage / 1000))

"""
=== current_value === 
"""
# call write_register 
seq=bytearray([(_cal_value >> 8) & 0xFF, _cal_value & 0xFF])
slave.write_to(_REG_CALIBRATION, seq)

# read_register 
buf = slave.read_from(_REG_CURRENT, 3)
read_raw_current = (buf[0] << 8) | (buf[1])

raw_current = _to_signed(read_raw_current)
print("Current:       {} mA".format(raw_current * _current_lsb))


print("Load Voltage:  {} V".format(bus_voltage + shunt_voltage))
print("")

