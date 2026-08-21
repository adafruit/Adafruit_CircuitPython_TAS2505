# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
Print the PLL and divider settings the driver solves for each sample rate.

``configure_clocks`` works out P, R, J, D, NDAC, MDAC and DOSR from whatever
clock the board supplies, so this is a quick way to see what it picked -- and
which rates the board's clocking can reach at all. Nothing is played, and no
amplifier is powered up, so it is safe to run with headphones plugged in.

Pin names are the Teenage Engineering SP-1's, the only board this driver has
been run on. ``board.TAS_RESET`` has to be released before ``board.I2C()``:
the SP-1 holds both codec RESET lines low at the start of every VM run, and a
chip in reset does not ACK, so constructing the driver first would raise
``ValueError: No I2C device at address: 0x18``.

The rates that fail on a bare bit clock fail for a real reason: at 32 bit
clocks per frame, 8000 Hz means a 256 kHz bit clock, which is below the PLL's
512 kHz input minimum. Supply an MCLK and those come back.
"""

import time

import board
import digitalio

import adafruit_tas2505

RATES = (8000, 11025, 16000, 22050, 32000, 44100, 48000)

# Set this to the MCLK frequency your board supplies, or leave it None to run
# everything from the I2S bit clock.
MCLK = None

reset_pin = digitalio.DigitalInOut(board.TAS_RESET)
reset_pin.direction = digitalio.Direction.OUTPUT
reset_pin.value = False
time.sleep(0.01)
reset_pin.value = True
time.sleep(0.01)

dac = adafruit_tas2505.TAS2505(board.I2C())

for rate in RATES:
    try:
        config = dac.configure_clocks(sample_rate=rate, mclk_freq=MCLK)
    except ValueError as error:
        print(f"{rate:6d} Hz: {error}")
        continue
    pll_out = config["p"], config["r"], config["j"], config["d"]
    print(
        f"{rate:6d} Hz: CODEC_CLKIN {config['codec_clkin'] / 1e6:8.4f} MHz  "
        f"P={pll_out[0]} R={pll_out[1]} J={pll_out[2]} D={pll_out[3]}  "
        f"NDAC={config['ndac']} MDAC={config['mdac']} DOSR={config['dosr']}"
    )

# Leave the chip on a sensible setting rather than the last one tried
dac.configure_clocks(sample_rate=44100, mclk_freq=MCLK)

# Nothing was powered up, so there is nothing to shut down -- but the pin still
# has to go back, or at the REPL a re-import fails with "TAS_RESET in use".
# Note that releasing it leaves the chip *out* of reset: the line goes high
# once nothing is driving it, so only a VM restart parks the codec again.
reset_pin.deinit()
