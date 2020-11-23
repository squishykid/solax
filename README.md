# Solax

[![Build Status](https://github.com/squishykid/solax/workflows/tests/badge.svg)](https://github.com/squishykid/solax/actions)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/solax.svg)](https://pypi.org/project/solax)

Read energy usage data from the real-time API on Solax solar inverters.

* Real time power, current and voltage
* Grid power information
* Battery level
* Temperature and inverter health
* Daily/Total energy summaries

## Usage

`pip install solax`

Then from within your project:

```
import solax
import asyncio

async def work():
    r = await solax.real_time_api('10.0.0.1')
    return await r.get_data()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
data = loop.run_until_complete(work())
print(data)
```

## Confirmed Supported Inverters

These inverters have been tested and confirmed to be working. If your inverter is not listed below, this library may still work- please create an issue so we can add your inverter to the list 😊.

* SK-TL5000E
