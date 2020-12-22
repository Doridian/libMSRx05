#!/usr/bin/env python2
# Simple utility to operate MSR605, MSR206 and compatible devices
#
# Lukas Vacek <lucas.vacek@gmail.com>, 
# originally written by Kirils Solovjovs, 2013
import libmsr as msr
import sys
import argparse
import serial
import json
import pprint
import time

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
coerg = parser.add_mutually_exclusive_group(required=False)
group.add_argument ('-r', '--read', action="store_true", help="RAW read magnetic tracks")
group.add_argument ('-w', '--write', action="store_true", help="RAW write magnetic tracks")
group.add_argument ('-R', '--iso-read', action="store_true", help="ISO read magnetic tracks")
group.add_argument ('-W', '--iso-write', nargs="*", help="ISO write magnetic tracks")
group.add_argument ('-e', '--erase', nargs="?", help="erase magnetic tracks",default="",const="123")
group.add_argument ('-x', '--clone', action="store_true", help="clone card")
group.add_argument ('-i', '--info', action="store_true", help="Print device information (firmware version,...)")
group.add_argument ('--reset', action="store_true", help="Reset the device")
group.add_argument ('-t','--test', action="store_true", help="Run all the tests on the device")
coerg.add_argument ('-C', '--hico', action="store_true", help="switch device to high coercivity mode")
coerg.add_argument ('-c', '--loco', action="store_true", help="switch device to low coercivity mode")
parser.add_argument('--bpc', nargs="*", help="Set BPC (5-7 for all 3 tracks)")
parser.add_argument('--bpi', nargs="*", help="Set BPI (high(1) or low(0), or as-is(None) for all 3 tracks)")
parser.add_argument('-f', '--file', help="Path to file to be used with RAW read/write")
parser.add_argument('-d', '--device', help="path to serial communication device",default="/dev/ttyUSB0")

args = parser.parse_args()

try:
    device = msr.x05(args.device, True)
except serial.serialutil.SerialException as err:
    print(ex)
    sys.exit(1)

if args.bpc is not None:
    res = device.setBPC(list(map(int, args.bpc)))
    if res:
        print("BPC set")
    else:
        print("BPC failed")
        sys.exit(1)
if args.bpi is not None:
    res = device.setBPI(list(map(int, args.bpi)))
    if res:
        print("BPI set")
    else:
        print("BPI failed")
        sys.exit(1)

if args.hico:
    res = device.setHiCo()
    if res:
        print("Hi-Co mode set")
    else:
        print("Hi-Co FAILED")
        sys.exit(1)
elif args.loco:
    res = device.setLoCo()
    if res:
        print("Lo-Co mode set")
    else:
        print("Lo-Co FAILED")
        sys.exit(1)

try:
    if args.read:
        res = device.readRaw()
        if len(res) == 3:
            if args.file:
                try:
                    with open(args.file,"wb") as f:
                        res_dict = {'track1':res[0],'track2':res[1],'track3':res[2]}
                        json.dump(res_dict,f,indent=4,encoding='latin1')
                        f.write("\n")
                except IOError as ex:
                    print(ex)
                    sys.exit(1)
            else:
                print("track1: %r" % res[0])
                print("track2: %r" % res[1])
                print("track3: %r" % res[2])
                print("")
        else:
            print("FAILED")
            print(data[1])
    elif args.write:
        if not args.file:
            print("argument --write requires --file")
            sys.exit(1)
        try: 
            with open(args.file,"rb") as f:
                data_dict = {'track1':'','track2':'','track3':''}
                try:
                    json_data = json.load(f,encoding="latin1")
                    erase_tracks_str = ""
                    erase_tracks = [0,0,0]
                    if "track1" in json_data and json_data["track1"] == "":
                        erase_tracks[0] = 1
                    if "track2" in json_data and json_data["track2"] == "":
                        erase_tracks[1] = 1
                    if "track3" in json_data and json_data["track3"] == "":
                        erase_tracks[2] = 1
                    if ("track1" not in json_data and "track2" not in json_data and
                        "track3" not in json_data and ("iso_track1" in json_data or
                        "iso_track2" in json_data or "iso_track3" in json_data) ):
                        print("FAILED - Trying to write an ISO dump file as RAW (use -W to write ISO dump instead)")
                        sys.exit(1)
                    data_dict.update(json_data)
                except (ValueError, TypeError):
                    print("FAILED - Invalid input data.")
                    print('Data must be in json dictionary with keys "track1","track2","track3" - just like returned by --read')
                    sys.exit(1)
                data = [ data_dict['track1'], data_dict['track2'], data_dict['track3'] ]
                overwrite_tracks_str = ""
                if data[0] != '': overwrite_tracks_str += "1"
                if data[1] != '': overwrite_tracks_str += "2"
                if data[2] != '': overwrite_tracks_str += "3"
                if erase_tracks[0] == 1: erase_tracks_str + "1"
                if erase_tracks[1] == 1: erase_tracks_str + "2"
                if erase_tracks[2] == 1: erase_tracks_str + "3"
                print("Track(s) %s will be overwritten" %  overwrite_tracks_str)
                try:
                    res = device.writeRaw(data)
                except Exception as ex:
                    print(ex)
                    sys.exit(1)
                if res == True:
                    print("OK")
                else:
                    print("FAIL: %s" % res)
                    sys.exit(1)
                if any(erase_tracks):
                    print("Please swipe again to erase track(s) %s." % erase_tracks_str)
                    device.eraseTracks(erase_tracks)
        except IOError as ex:
            print(ex)
            sys.exit(1)
    elif args.iso_read:
        res = device.readISO()
        if len(res) == 3:
                if args.file:
                    try:
                        with open(args.file,"wb") as f:
                            res_dict = {'iso_track1':res[0],'iso_track2':res[1],'iso_track3':res[2]}
                            json.dump(res_dict,f,indent=4,encoding='latin1')
                            f.write("\n")
                    except IOError as ex:
                        print(ex)
                        sys.exit(1)
                else:
                    print("track1: %r" % res[0])
                    print("track2: %r" % res[1])
                    print("track3: %r" % res[2])
                    print("")
        else:
            print("FAIL")
            print(res[0])
            sys.exit(1)
    elif args.iso_write is not None:
        if ( (args.iso_write == [] and not args.file) or
             (args.iso_write != [] and args.file) ):
            print("Tracks to be written must be supplied as arguments to -W OR -f must be provided")
            sys.exit(1)
        if len(args.iso_write) > 3:
            print("-W takes at max 3 arguments. Usage: %s -W <track1> <track2> <track3>" % sys.argv[0])
            sys.exit(1)
        if args.file:
            try:
                with open(args.file,"rb") as f:
                    data_dict = {'iso_track1':'','iso_track2':'','iso_track3':''}
                    try:
                        json_data = json.load(f,encoding="latin1")
                        erase_tracks_str = ""
                        erase_tracks = [0,0,0]
                        if "iso_track1" in json_data and json_data["iso_track1"] == "":
                            erase_tracks[0] = 1
                            erase_tracks_str += "1"
                        if "iso_track2" in json_data and json_data["iso_track2"] == "":
                            erase_tracks[1] = 1
                            erase_tracks_str += "2"
                        if "iso_track3" in json_data and json_data["iso_track3"] == "":
                            erase_tracks[2] = 1
                            erase_tracks_str += "3"
                        if ("iso_track1" not in json_data and "iso_track2" not in json_data and
                            "iso_track3" not in json_data and ("track1" in json_data or
                            "track2" in json_data or "track3" in json_data) ):
                            print("FAILED - Trying to write a RAW dump file as ISO (use -w to write RAW dump instead)")
                            sys.exit(1)
                        data_dict.update(json_data)
                    except (ValueError, TypeError):
                        print("FAILED - Invalid input data.")
                        print('Data must be in json dictionary with keys "iso_track1","iso_track2","iso_track3" - just like returned by -R')
                        sys.exit(1)
                    data = [ data_dict['iso_track1'], data_dict['iso_track2'], data_dict['iso_track3'] ]
            except IOError as ex:
                print(ex)
                sys.exit(1)
        else:
            data = args.iso_write
            while(len(data)<3):
                data.append('')
            erase_tracks = [0,0,0]
        overwrite_tracks_str = ""
        if data[0] != '': overwrite_tracks_str += "1"
        if data[1] != '': overwrite_tracks_str += "2"
        if data[2] != '': overwrite_tracks_str += "3"
        if erase_tracks[0] == 1: erase_tracks_str + "1"
        if erase_tracks[1] == 1: erase_tracks_str + "2"
        if erase_tracks[2] == 1: erase_tracks_str + "3"
        # validate data and provide nice err msgs
        # track 1 must be in format "%DATA?", tracks 2 and 3 must be in format ";DATA?"
        track1 = data[0]; track2 = data[1]; track3 = data[2]
        if (track1 !="" ) and ( (not track1.startswith("%")) or (not track1.endswith("?")) ):
            print("Invalid ISO track1 - track1 must be in format \"%DATA?\"")
            sys.exit(1)
        if (track2 !="" ) and ( (not track2.startswith(";")) or (not track2.endswith("?")) ):
            print("Invalid ISO track2 - track2 must be in format \";DATA?\"")
            sys.exit(1)
        if (track3 !="" ) and ( (not track3.startswith(";")) or (not track3.endswith("?")) ):
            print("Invalid ISO track3 - track3 must be in format \";DATA?\"")
            sys.exit(1)
        track1_allowed = " !\"#$%&'()*+`,./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_"
        track23_allowed = "0123456789:;<=>?"
        for c in track1:
            if c not in track1_allowed:
                print("Invalid ISO track1 - invalid character - only \"%s\" allowed" % track1_allowed)
                sys.exit(1)
        for c in track2:
            if c not in track23_allowed:
                print("Invalid ISO track2 - invalid character - only \"%s\" allowed" % track23_allowed)
                sys.exit(1)
        for c in track3:
            if c not in track23_allowed:
                print("Invalid ISO track3 - invalid character - only \"%s\" allowed" % track23_allowed)
                sys.exit(1)
        # write data to the card
        print("Track(s) %s will be overwritten" %  overwrite_tracks_str)
        try:
            res = device.writeISO(data)
        except Exception as ex:
            print(ex)
            sys.exit(1)
        if res == True:
            print("OK")
        else:
            print("FAIL: %s" % res)
            sys.exit(1)
        if any(erase_tracks):
            print("Please swipe again to erase track(s) %s." % erase_tracks_str)
            device.eraseTracks(erase_tracks)
    elif args.erase:
        tracks = [0,0,0]
        if "1" in args.erase:
            tracks[0] = 1
        if "2" in args.erase:
            tracks[1] = 1
        if "3" in args.erase:
            tracks[2] = 1
        if not any(tracks):
            print("Invalid tracks specified for --erase.")
            print("Use --erase without an argument to erase the whole card.")
            print("Use --erase 1 to delete track 1, --erase 23 to delete tracks 2 and 3, ...")
            sys.exit(1)
        device.eraseTracks(tracks)
    elif args.clone:
        print("Please swipe the original to clone...")
        orig_data = data = device.readRaw()
        if len(data) == 3:
            print("track1: %r\ntrack2: %r\ntrack3: %r" % ( data[0],data[1],data[2] ) )
        else:
            pprint.pprint(data)
        print("")

        # 0 - dont erase, 1 - erase
        erase_tracks = [1 if len(x)==0 else 0 for x in data]

        print("Please swipe the card to be written...")
        res = device.writeRaw(data)
        if res: 
            print('OK')
        else: 
            print('FAILED')
            sys.exit(1)

        if any(erase_tracks):
            print("Please swipe again (to erase tracks which are empty on the original card ...)")
            device.eraseTracks(erase_tracks)

        time.sleep(0.2)
        print("Please swipe the newly written card again to verify contents...")
        data = device.readRaw()
        if len(data) == 3:
            print("track1: %r\ntrack2: %r\ntrack3: %r" % ( data[0],data[1],data[2] ) )
        else:
            pprint.pprint(data)
        if [x.rstrip("\x00") for x in orig_data] == [x.rstrip("\x00") for x in data]:
            print("YAAAY!")
        else:
            print("Argh! The original and the newly written do not match!!")
        print("")

    elif args.info:
        print("Firmware Version: " + device.getFirmwareVersion() )
        print("Device Model: " + device.getDeviceModel() )
        print("Coercivity: " + ("High" if device.getCo() else "Low") )
        lz=device.getLZ()
        border=str(round(lz[0]*25.4/210,1))
        middle=str(round(lz[1]*25.4/75,1))
        print("[LeadingZeros] Track1&3: "+border+"mm, Track2: "+middle+"mm")
    elif args.reset:
        device.reset()
    elif args.test:
        print("Full self test (please swipe a card)")
        if device.test():
            print('OK')
        else:
            print('FAILED')
except KeyboardInterrupt:
    print("Received KeyboardInterrupt. Exiting.")
