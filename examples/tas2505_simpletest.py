# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
Play a sine wave out of the Class-D speaker amplifier.

Pin names are the Teenage Engineering SP-1's, the only board this driver has
been run on.

Two things about this chip shape the example:

* **Release RESET before touching I2C.** The TAS2505 does have a software
  reset, but a chip held in reset does not ACK, so the reset register is
  unreachable until the pin is released -- and the SP-1 parks both codec RESET
  lines low at the start of every VM run. Releasing ``board.TAS_RESET`` is
  therefore the first thing here, ahead of ``board.I2C()``.
* **The TAS2505 has no clock source of its own**: its PLL locks to the I2S bit
  clock, so ``configure_clocks`` has to be told what sample rate that clock is
  carrying. CircuitPython drives the I2S output at 16-bit stereo, which is 32
  bit clocks per frame, and that is what the driver assumes.
"""

import array
import math
import time

import audiobusio
import audiocore
import board
import digitalio

import adafruit_tas2505

RATE = 44100

# Speaker level, in dB. These three are the whole volume story: a digital
# attenuator ahead of the DAC, an analog one after it, and the Class-D
# amplifier's own gain. They are the levels the SP-1's speaker was first heard
# at, and they are *not* what ``speaker_output`` loads -- its defaults are 30 dB
# quieter than this, which on this speaker is inaudible in a normal room.
#
# CAUTION: the Class-D amplifier is loud, and it goes a lot louder than this.
# If this is too much, bring DAC_VOLUME down first -- it is the one that costs
# nothing but level.
DAC_VOLUME = 0  # digital, 0 to -63.5
SPEAKER_VOLUME = 0  # analog, 0 to -72.3
SPEAKER_GAIN = 6  # Class-D amplifier, 6 to 24

reset_pin = digitalio.DigitalInOut(board.TAS_RESET)
reset_pin.direction = digitalio.Direction.OUTPUT
reset_pin.value = False
time.sleep(0.01)
reset_pin.value = True
time.sleep(0.01)

dac = adafruit_tas2505.TAS2505(board.I2C())
dac.configure_clocks(sample_rate=RATE)

# speaker_output is a quickstart: it powers the amplifier up and routes the DAC
# to it, but it deliberately ends quiet (-20 dB digital, -10 dB analog, 6 dB of
# amplifier gain). Coming up from there is the caller's job, so do it here --
# leaving the defaults alone is what "it runs but I hear nothing" sounds like.
dac.speaker_output = True
dac.dac_volume = DAC_VOLUME
dac.speaker_volume = SPEAKER_VOLUME
dac.speaker_gain = SPEAKER_GAIN

audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DOUT)

# One cycle of a 440 Hz sine, played on a loop
length = RATE // 440
sine_wave = array.array("h", [0] * length)
for i in range(length):
    sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * 0.5 * (2**15 - 1))
sine_wave_sample = audiocore.RawSample(sine_wave, sample_rate=RATE)

try:
    while True:
        audio.play(sine_wave_sample, loop=True)
        time.sleep(1)
        audio.stop()
        time.sleep(1)
finally:
    # Ctrl-C lands here. Powering the amplifier down is what actually quiets
    # the chip -- deinit-ing the RESET pin does not put it back in reset,
    # because the line goes high once nothing is driving it. Releasing the pins
    # as well as the I2S still matters at the REPL: an import that dies with
    # them claimed makes the next one fail with ``ValueError: TAS_RESET in
    # use``.
    dac.speaker_output = False
    audio.stop()
    audio.deinit()
    reset_pin.deinit()
