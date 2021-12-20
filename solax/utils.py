def div10(val, *_args, **_kwargs):
    return val / 10


def div100(val, *_args, **_kwargs):
    return val / 100


def resetting_counter(value, mapped_sensor_data, key, adjust,
                      *_args, **_kwargs):
    value += mapped_sensor_data[key] * 65535
    value = adjust(value)
    return value


def total_energy(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='Total Energy Resets', adjust=div10)


def eps_total_energy(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='EPS Total Energy Resets', adjust=div10)


def feedin_energy(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='Total Feed-in Energy Resets', adjust=div100)


def charge_energy(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='Total Battery Charge Energy Resets',
                             adjust=div10)


def discharge_energy(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='Total Battery Discharge Energy Resets',
                             adjust=div10)


def pv_energy(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='Total PV Energy Resets',
                             adjust=div10)


def consumption(value, mapped_sensor_data, *_args, **_kwargs):
    return resetting_counter(value, mapped_sensor_data,
                             key='Total Consumption Resets', adjust=div100)


def to_signed(val, *_args, **_kwargs):
    if val > 32767:
        val -= 65535
    return val


def twoway_div10(val, *_args, **_kwargs):
    return to_signed(val, None) / 10


def twoway_div100(val, *_args, **_kwargs):
    return to_signed(val, None) / 100
