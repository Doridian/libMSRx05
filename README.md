libMSRx05
======

Pyhton library for interfacing MSRx05 and MSRx06 Magnetic Stripe Card Readers/Writers.

This fully implements the communication protocol.

Includes a simple python utility to use the Readers/Writer.

Originally forked from https://github.com/0ki/libMSRx05. Thanks!

## Examples ##

NOTE: 
- default BPI is 210BPI for Track1 and Track3 and 75BPI for Track2
- default BPC is 7BPC for Track1 and 5BPC for Track2 and Track3
- the library supports changing these values but the user utility
always assumes default values for simplicity

### Clone a card ###
```
./msr.py -x
```

NOTE: swipe the original card and then the new card

### Save a raw dump of a card to a file ###
```
./msr.py -r -f card\_dump
```

### Read a card in raw mode and show the result on stdout ###
```
./msr.py -r
```

### Load a card from a raw dump (using alternative path to the device) ###
```
./msr.py -w -f card\_dump -d /dev/ttyUSB1
```

NOTE:
The raw dump is a human-readable JSON file with keys "track1", "track2", "track3".
If a key is missing, the track is not touched. If the value for a key is an empty string,
the track is erased.

### Write ISO-formatted data to the card ###
```
./msr.py -W "%ABC123?" ";657?" ";999?"
```

NOTE: Only certain characters are allowed in ISO mode

### Write ISO-formatted data to the card (overwrite only track 2) ###
```
./msr.py -W "" ";777?"
```

### Write ISO-formatted data to the card (only track3 should contain data) ###
```
./msr.py -e
./msr.py -W "" "" ";333?"
```

### Save an ISO dump of a card to a file ###
```
./msr.py -R -f iso\_dump
```

### Read a card in ISO mode and show the result on stdout ###
```
./msr.py -R
```

### Load a card from an ISO dump ###
```
./msr.py -W -f iso\_dump
```

NOTE:
The ISO dump is a human-readable JSON file with keys "iso\_track1", "iso\_track2", "iso\_track3".
If a key is missing, the track is not touched. If the value for a key is an empty string,
the track is erased.

### Reset the device ###
```
./msr.py --reset
```

NOTE: reset does not change coercivity mode

### Switch the device to High Coercivity mode ###
```
./msr.py -C
```

### Switch the device to Low Coercivity mode ###
```
./msr.py -c
```

### Erase the card ###
```
./msr.py -e
```

### Erase only second track on the card (using alternative path to the device) ###
```
./msr.py -e 2 -d /dev/ttyUSB1
```

### Run a few tests on the reader/writer ###
```
./msr.py --test
```
