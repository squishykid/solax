from voluptuous import Invalid


def u16_packer(*values: float) -> float:
    accumulator = 0.0
    stride = 1
    for value in values:
        accumulator += value * stride
        stride *= 2**16
    return accumulator


def startswith(something):
    def inner(actual):
        if isinstance(actual, str):
            if actual.startswith(something):
                return actual
        raise Invalid(f"{str(actual)} does not start with {something}")

    return inner


def div10(*val: float) -> float:
    assert len(val) == 1
    return val[0] / 10


def div100(*arg: float):
    val = arg[0]
    return val / 100


# def max_float(*arg: float) -> float:
#     return max(arg)


INT16_MAX = 0x7FFF
INT32_MAX = 0x7FFFFFFF


def to_signed(*arg: float):
    val = arg[0]
    if val > INT16_MAX:
        val -= 2**16
    return val


def to_signed32(*arg: float):
    val = arg[0]
    if val > INT32_MAX:
        val -= 2**32
    return val


def twoway_div10(*arg: float):
    val = arg[0]
    return to_signed(val) / 10


def twoway_div100(*arg: float):
    val = arg[0]
    return to_signed(val) / 100


def to_url(host, port):
    return f"http://{host}:{port}/"
