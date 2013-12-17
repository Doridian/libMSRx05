libMSRx05
======

Pyhton library for interfacing MSRx05 and MSRx06 Magnetic Stripe Card Readers/Writers.

This fully implements the communication protocol.

Includes a simple python utility to use the Readers/Writer.

Originally forked from https://github.com/0ki/libMSRx05. Thanks!

Example
========

NOTE: 
    - default BPI is 210BPI for Track1 and Track3 and 75BPI for Track2
    - default BPC is 7BPC for Track1 and 5BPC for Track2 and Track3
    - the library supports changing these values but the user utility
    always assumes default values for simplicity

* Clone a card
./msr.py -x

NOTE: swipe the original card and then the new card)

* Save a card raw dump to a file
./msr.py -W -f card\_dump

* Load a card from a raw dump (using alternative path to the device)
./msr.py -R -f card\_dump -d /dev/ttyUSB1

* Write ISO-formatted data to the card - ISO 7813 (tracks 1 and 2) and ISO 4909 (track 3)
./msr.py -w -t 123 ABC123 657 999

NOTE: Only certain characters are supported in ISO mode

* Write ISO-formatted data to the card (overwrite only track 2)
./msr.py -w -t 2 777

* Reset the device
./msr.py --reset

NOTE: reset does not change coercivity mode

* Switch the device to High Coercivity mode
./msr.py -C

* Switch the device to Low Coercivity mode
./msr.py -c

* Erase the card
./msr.py -e

* Erase only second track on the card (using alternative path to  the device)
./msr.py -e -t 2 -d /dev/ttyUSB1

* Change BPI density the reader/writer will use (high: 210bits/inch, low: 75 bits/inch)
./msr.py -b hlh

NOTE: allowed values: h - high, l - low, d - default, x - don't change
NOTE: when changing BPI - all three values must be set

* Run a few tests on the reader/writer
./msr.py --test
