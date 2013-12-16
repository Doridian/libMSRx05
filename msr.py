#!/usr/bin/env python2
# Program for testing libMSRx05
#
# Copyright Kirils Solovjovs, 2013
import libMSRx05 as msr
import sys
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument ('-r', '--read', action="store_true", help="RAW read magnetic tracks")
group.add_argument ('-w', '--write', action="store_true", help="RAW write magnetic tracks")
group.add_argument ('-R', '--iso-read', action="store_true", help="ISO read magnetic tracks")
group.add_argument ('-W', '--iso-write', action="store_true", help="ISO write magnetic tracks")
group.add_argument ('-e', '--erase', action="store_true", help="erase magnetic tracks")
group.add_argument ('-x', '--clone', action="store_true", help="clone card")
group.add_argument ('--reset', action="store_true", help="Reset the device")
group.add_argument ('--test', action="store_true", help="Run all the tests on the device")
group.add_argument ('-C', '--hico', action="store_true", help="switch device to high coercivity mode")
group.add_argument ('-c', '--loco', action="store_true", help="switch device to low coercivity mode")
group.add_argument ('-b', '--bpi', help="Set bits per inch density for each track ((h)igh,(l)ow,(d)efault,(x)dont change)")
parser.add_argument('-f', '--file', help="Path to file to be used with RAW read/write")
parser.add_argument('-d', '--device', help="path to serial communication device",default="/dev/ttyUSB0")
parser.add_argument('-B', '--bpc', help="bit per characters for each track (5 to 8)")
parser.add_argument('-t', '--tracks', default="123", help="select tracks (1, 2, 3, 12, 23, 13, 123)")
parser.add_argument('data', nargs="*", help="(ISO write only) 1, 2 or 3 arguments, matching --tracks")

arga = parser.parse_args()

device = msr.x05('/dev/ttyUSB0',True)

device.setLED(7)

print "Firmware Version: " + device.getFirmwareVersion()
print "Device Model: " + device.getDeviceModel()
print "Coercivity: " + ("High" if device.getCo() else "Low")
lz=device.getLZ()
border=str(round(lz[0]*25.4/210,1))
middle=str(round(lz[1]*25.4/75,1))
print "[LeadingZeros] Track1&3: "+border+"mm, Track2: "+middle+"mm"

#print "Full self test (please swipe a card until green light blinks):",
#sys.stdout.flush()
#if device.test():
#  print 'OK'
#else:
#  print 'FAILED'

#print device.setBPC([7,5,5]);
#print device.setBPI([1,1,1]);
#print device.setLZ([61,22]);

#print device.writeISO(['%34XX%23_4?',None,';01234567890:;<=>0123?'])
#print device.eraseTracks([1,1,1]);

#a=device.readISO()
#print a
#print device.writeISO(a)
#exit(0)

print "Please swipe the original to clone..."
a = device.readRaw()

print "Please swipe the card to be written...",
sys.stdout.flush()

#this erases the tracks which are empty on the original
if (device.eraseTracks(map(lambda x: len(x)==0,a))):
  print "again...",
  sys.stdout.flush()
if device.writeRaw(a): print 'ok'
else: print 'failed'

print "Please swipe the newly written card again to verify contents..."
print device.readISO()

#print device.writeRawText(['123','123','123'],[1,1,1],[5,5,5],[0,0,0])

device.close()

