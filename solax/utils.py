from voluptuous import Invalid


def startswith(something):
    def inner(actual):
        if isinstance(actual, str):
            if actual.startswith(something):
                return actual
        raise Invalid(f"{str(actual)} does not start with {something}")

    return inner


def div10(val, *_args, **_kwargs):
    return val / 10


def div100(val, *_args, **_kwargs):
    return val / 100


def to_signed(val, *_args, **_kwargs):
    if val > 32767:
        val -= 65535
    return val


def twoway_div10(val, *_args, **_kwargs):
    return to_signed(val, None) / 10


def twoway_div100(val, *_args, **_kwargs):
    return to_signed(val, None) / 100
