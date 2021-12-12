def div10(val, *_args, **_kwargs):
    return val / 10


def div100(val, *_args, **_kwargs):
    return val / 100


def energy(value, mapped_sensor_data, *_args, **_kwargs):
    value += mapped_sensor_data['Total Feed-in Energy Resets'] * 65535
    value = value / 100
    return value


def consumption(value, mapped_sensor_data, *_args, **_kwargs):
    value += mapped_sensor_data['Total Consumption Resets'] * 65535
    value = value / 100
    return value


def to_signed(val, *_args, **_kwargs):
    if val > 32767:
        val -= 65535
    return val


def twoway_div10(val, *_args, **_kwargs):
    return to_signed(val, None) / 10


def twoway_div100(val, *_args, **_kwargs):
    return to_signed(val, None) / 100
