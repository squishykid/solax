# Solax

![Build Status](https://travis-ci.org/squishykid/solax.svg?branch=master)
![PyPI - Downloads](https://img.shields.io/pypi/dm/solax.svg)

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

r = solax.RealTimeAPI('10.0.0.1')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
data = loop.run_until_complete(r.get_data())
```

## Confirmed Supported Inverters

These inverters have been tested and confirmed to be working. If your inverter is not listed below, this library may still work- please create an issue so we can add your inverter to the list 😊.

* SK-TL5000E