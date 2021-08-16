def div10(val, *args, **kwargs):
    return val / 10


def div100(val, *args, **kwargs):
    return val / 100


def energy(value, mapped_sensor_data, *args, **kwargs):
    value += mapped_sensor_data['Total Feed-in Energy Resets'] * 65535
    value = value / 100
    return value


def consumption(value, mapped_sensor_data, *args, **kwargs):
    value += mapped_sensor_data['Total Consumption Resets'] * 65535
    value = value / 100
    return value


def twoway_current(val, _):
    return to_signed(val, None) / 10


def to_signed(val, _):
    if val > 32767:
        val -= 65535
    return val
