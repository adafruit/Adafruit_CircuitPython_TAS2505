Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-tas2505/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/tas2505/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_TAS2505/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_TAS2505/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython driver library for TI TAS2505 audio amplifier


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing from PyPI
=====================
On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-tas2505/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-tas2505

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-tas2505

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-tas2505

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_tas2505

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import array
    import math
    import time

    import audiobusio
    import audiocore
    import board
    import digitalio

    import adafruit_tas2505

    RATE = 44100

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
        dac.speaker_output = False
        audio.stop()
        audio.deinit()
        reset_pin.deinit()


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/tas2505/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_TAS2505/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
