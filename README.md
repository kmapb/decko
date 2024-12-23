This turns a decklist in popular textual formats (ManaBox, MtG Arena, etc.) into a printer-ready PDF.

First, get Python for your system: https://www.python.org/downloads/

Then install the requirements:

```pip3 install requirements.txt```

and finally fun it as:

```python3 decko.py muh_deck.decklist```

where `muh_deck.decklist` is your deck exported from ManaBox, MtG Arena, etc. By default output is in proxies.pdf, but you can direct it where you like with the `-o` option:

```python3 decko.py --scale=0.5  --output=tiny.pdf muh_deck.decklist```

will render the deck at one quarter size (0.5x in each dimension) into `tiny.pdf`.

