# libMSRx05.py
#
# Library for accesing MSR205, MSR206, MSR505, MSR605, MSR606 and compatible MagStripe RW devices
#
# Copyright Kirils Solovjovs, 2013
# based on work by Louis Bodnar, end of september 2012
#
# slightly modified by Lukas Vacek


import serial
import binascii
import time

ESC = '\x1B'
ACK = '\x1B\x30'

class x05:
    def __init__(self, port, safetywarnings=False):
        # open port
        self.__safetywarnings=safetywarnings
        self.__s = serial.Serial(port, 9600)
        self.reset()
        self.testComm()

    def __s_write(self, s):
        return self.__s.write(s.encode())

    def __s_read(self, len = 1):
        return self.__s.read(len).decode()

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.__s.close

    def __status(self,c):
        if (c=='0'): return "OK"
        if (c=='1'): return "Read or write error"
        if (c=='2'): return "Command misaligned"
        if (c=='4'): return "Command invalid"
        if (c=='9'): return "Card swiped too fast or too slow"

    def __expect(self, stri, nonfatal=False):
        a = self.__s_read(len(stri))
        if nonfatal:
            return (a == stri)
        if (a != stri):
            raise Exception("communication error; expected [" + binascii.hexlify(stri) + "] got [" + binascii.hexlify(a) + "]")

    def __read_until(self, byte):
        b = ""
        d = ""
        while True:
            b = self.__s_read()
            if (b == byte):
                return d
            d += b

    def __warn(self):
        if(self.__safetywarnings):
            print("WARNING! NEXT SWIPE WILL WRITE TO CARD WITH "+ ("HIGH" if self.getCo() else "LOW") + " COERCIVITY")

    def getFirmwareVersion(self):
        self.__s_write('\x1B\x76')
        time.sleep(.1)
        self.__expect(ESC)
        version = ""
        while (self.__s.inWaiting()):
            version += self.__s_read()
        return version

    def getDeviceModel(self):
        self.__s_write('\x1B\x74')
        time.sleep(.1)
        self.__expect(ESC)
        version = ""
        while (self.__s.inWaiting()):
            version += self.__s_read()
        if (version[-1:] != 'S'):
            raise Exception("communcation error")
        return version[:-1]
        
    def reset(self):
        self.__s_write('\x1B\x61')

    def test(self):
        return self.testComm() and self.testRAM() and self.testSensor()

    def testComm(self):
        self.__s_write('\x1B\x65')
        return self.__expect(ESC+'y',True)

    def testSensor(self):
        self.__s_write('\x1B\x86')
        return self.__expect(ACK,True)

    def testRAM(self):
        self.__s_write('\x1B\x87')
        return self.__expect(ACK,True)

    def setLED(self,bits): # R3 Y2 G1
        if ( bits not in [0,1,2,4,7]):
            raise Exception("Hardware does not support having 2 lights on");
        if ( bits == 7 ): self.__s_write('\x1B\x82')
        if ( bits == 0 ): self.__s_write('\x1B\x81')
        if ( bits == 1 ): self.__s_write('\x1B\x83')
        if ( bits == 2 ): self.__s_write('\x1B\x84')
        if ( bits == 4 ): self.__s_write('\x1B\x85')

    def setLZ(self,track):
        try:
            if(track[2] != track[0]):
                raise Exception('Track3 must have the same Leading Zero count as Track1')
        except IndexError:
            pass
        self.__s_write('\x1B\x7A'+chr(track[0])+chr(track[1]))
        return self.__expect(ACK,True)

    def getLZ(self):
        self.__s_write('\x1B\x6C')
        self.__expect('\x1B')
        tr13=ord(self.__s_read(1))
        tr2=ord(self.__s_read(1))
        return [tr13,tr2,tr13]

    def eraseTracks(self, tracks, coerc=1):
        select = 0
        try:
            for i in [0,1,2]:
                select += (tracks[i]>0)*(2**i)
        except IndexError:
            pass
        if (select == 0):
            return False
        self.__warn()
        # [sic] writing \x01 works as well as \x00 to erase only Track1
        self.__s_write('\x1B\x63'+chr(select))
        return self.__expect(ACK,True)*select

    def setBPC(self, bpc):
        # fixed this. now it works
        failed=False
        try:
            for i in [0,1,2]:
                if (bpc[i] < 5 or bpc[i] > 8):
                    failed=True
        except IndexError:
            failed=True
        if (failed):
            raise Exception ("Please specify BPC (5-8) for all 3 tracks")

        self.__s_write('\x1B\x6F'+chr(bpc[0])+chr(bpc[1])+chr(bpc[2]))
        self.__expect(ACK)
        return self.__expect(chr(bpc[0])+chr(bpc[1])+chr(bpc[2]),True)


    def setBPI(self, bpi):
        failed=False
        try:
            for i in [0,1,2]:
                if (bpi[i] is not None and bpi[i] != 0 and bpi[i] != 1):
                    failed=True
        except IndexError:
            failed=True
        if (failed):
            raise Exception ("Please specify BPI (high(1) or low(0), or as-is(None)) for all 3 tracks")
        result=True
        for i in [0,1,2]:
            if (bpi[i] is not None):
                result &= self.__setBPI(i+1,bpi[i])
        return result


    def __setBPI(self, track, bpi):
        if(track==1 and bpi==0): code='\xA0'
        elif(track==1 and bpi==1): code='\xA1'
        elif(track==2 and bpi==0): code='\x4B'
        elif(track==2 and bpi==1): code='\xD2'
        elif(track==3 and bpi==0): code='\xC0'
        elif(track==3 and bpi==1): code='\xC1'
        else: code='\xFF'

        self.__s_write('\x1B\x62'+code)
        return self.__expect(ACK,True)


    # you should hear a click when changing coercivity
    def setHiCo(self):
        self.__s_write('\x1B\x78')
        return self.__expect(ACK,True)

    def setLoCo(self):
        self.__s_write('\x1B\x79')
        return self.__expect(ACK,True)

    def getCo(self):
        self.__s_write('\x1B\x64')
        r = self.__s_read(2)
        if (r == ESC+'h'):
            return 1
        if (r == ESC+'l'):
             return 0
        raise Exception('communcation error')


    def readISO(self):
        self.reset()
        self.__s_write('\x1B\x72')
        data = ['','','']
        status = [0,0,0]
        
        self.__expect('\x1B\x73')
        self.__expect(ESC)
        for track in [0,1,2]:
            self.__expect(chr(track+1))
            data[track] = self.__read_until(ESC)
            if (len(data[track])==0):
                status[track] = self.__s_read()
                if (track == 2):
                    self.__expect('\x3F\x1C');
                self.__expect(ESC)

        if(status[2] == 0):
            data[2] = data[2][:-2]

        # check status
        result=self.__s_read();
        if (result== '0'):
            return data
        else:
            status.insert(0,result)
            status.insert(0,self.__status(result))
            status.extend(data)
            return status # ERRORCODE, ERRORSTRING, eTR1, eTR2, eTR3 ( '+' empty track, '*' error reading), TR1, TR2, TR3


    def writeISO(self, data):
        self.__warn()
        fcount = 0
        while(len(data)<3):
            data.append('')

        for i in [0,1,2]:
            if data[i] is None: data[i]=''
            if (len(data[i])>0):
                fcount += 1
                if (len(data[i])<2 or data[i][0] != (';' if i else '%') or data[i][-1] != '?'):
                    raise Exception("Track"+chr(0x30+1+i)+" is not ISO formatted")
                else:
                    data[i] = data[i][1:-1]

        if not fcount:
            raise Exception("Nothing to write")


        #checking for ISO chars
        #track1 = 0x20 - x05f except ?
        #track2 or 3 = 0x30 - 0x3f except ?
        str1 = []
        str23 = []
        for c in filter(lambda x:x!=0x3f,range(0x20,0x60)):
            str1.append(chr(c))
        for c in range (0x30,0x3f):
            str23.append(chr(c))

        for i in [0,1,2]:
         if not set(data[i]).issubset(str23 if i else str1):
             raise Exception("Track"+chr(0x30+1+i)+" contains illegal characters")

        command = ESC+'\x77'+ESC+'\x73'
        for i in [0,1,2]:
            command += ESC+chr(i+1)+data[i]
        command += '?\x1C'

        self.__s_write(command)
        self.__expect(ESC)

        # check status
        status=self.__s_read()
        if (status ==    '0'):
            return True
        else:
            return self.__status(status)


    def readRaw(self):
        self.__s_write('\x1B\x6D')
        self.__expect('\x1B\x73')

        data=['','','']
        for track in [0,1,2]:
            self.__expect(ESC+chr(track+1))
            length = ord(self.__s_read())
            if length>0:
                data[track] = self.__s_read(length)

        self.__expect('\x3F\x1C\x1B');

        result=self.__s_read();
        if (result== '0'):
            return data
        else:
            data.insert(0,result)
            data.insert(0,self.__status(result))
            return data # ERRORCODE, ERRORSTRING, TR1, TR2, TR3

    def __reverseStringBits(self,text):
     rev = ""
     for ti in range(len(text)):
         rev += chr(sum(1<<(7-i) for i in range(8) if ord(text[ti])>>i&1))
     return rev

    def writeRaw(self,data,reversed=True):
        self.__warn()
        fcount = 0
        while(len(data)<3):
            data.append('')

        for i in [0,1,2]:
            if data[i] is None: data[i]=''
            if (len(data[i])>0):
                fcount += 1

        if not fcount:
            raise Exception("Nothing to write")

        command = ESC+'\x6E'+ESC+'\x73'
        for i in [0,1,2]:
            command += ESC+chr(i+1)+chr(len(data[i]))+(self.__reverseStringBits(data[i]) if reversed else data[i])
        command += '?\x1C'

        self.__s_write(command)
        self.__expect(ESC)

        # check status
        status=self.__s_read()
        if (status == '0'):
            return True
        else:
            return self.__status(status)
