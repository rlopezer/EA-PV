#-coding:utf8 -*
"""
Manages the telegrams sent to/received from
power supplies PS2042-20B & PS2084-10B.
"""

__author__      = "Ramón López-Erauskin"
__copyright__   = "Copyright 2017"
__credits__     = ["Ramón López-Erauskin"]
__license__     = ""
__version__     = "1.0.0"
__maintainer__  = "Ramón López-Erauskin"
__email__       = "r.lopez.erauskin@gmail.com"
__status__      = "Prototype"

import buildtelegram
import serial
import struct
import signal

def float_to_hex(f):
    return float(struct.unpack('<I', struct.pack('<f', f))[0])

# Create a dictionnary with the telegrams to send
Operation = {"Query": buildtelegram.t_query(),
             "EnableRemote": buildtelegram.t_remote(True),
             "DisableRemote": buildtelegram.t_remote(False),
             "EnableOutput": buildtelegram.t_output(True),
             "DisableOutput": buildtelegram.t_output(False),
             "Limits": buildtelegram.t_limits(0),}

# Function to convert the received measurements into electrical quantities
# according to the parameters of the power supply
def conversion(type='Voltage', input=[0] * 11, V_max=42, I_max=10):
    # This is for a constant value
    gain_meas = 25600  # see manual of the power supply for the conversion
    # Nominal power supply characteristics
    #V_max = 84  # 42 for the PS2042-20B & 84 for the PS2084-10B
    #I_max = 10  # 20 for the PS2042-20B & 10 for the PS2084-10B
    P_max = 300  
    try:
        if type == 'Voltage':
            output = (input[6] + input[5] * 256.0) * V_max / gain_meas
        elif type == 'Current':
            output = (input[8] + input[7] * 256.0) * I_max / gain_meas
        else:
            output = 1
        return output
    except:
        return 0


def Communicate(serialport=serial.Serial, packet=Operation['Query'], answer=[], Vmax=42, Imax=10):
    serialport.flushOutput()
    serialport.flushInput()
    # convert the packet in decimal (e.g. [117, 0, 71, 0, 188]) into a byte
    # array (u\x00G\x00\xbc)
    array_to_send = bytearray(packet)
    serialport.write(array_to_send)  # send the array over the serial port
    # read the answered string, something like '\x00G\x00\xbc'
    reading = serialport.read(11)
    intlist = [ord(item)
               for item in struct.unpack('c' * len(reading), reading)]  # convert it into an int list
    answer[:] = []  # clear the list
    # read the answer and put it into "answer" Length 11 expected
    answer.extend(intlist)

    # if the answer is too short, the checksum may be missing
    if len(answer) < 5:
        print ('ERROR: short answer (%d bytes received)' % len(answer))
    elif len(answer) == 11:
        Vread = conversion('Voltage',answer, Vmax, Imax)
        Iread = conversion('Current',answer, Vmax, Imax)
        return Vread, Iread
    elif len(answer) == 6:
        #print "Error #", answer[3], "received"
        return 'x', 'x'
    elif len(answer) == 0:
        pass
    else:
        print "Unknown code received"
    # TODO: implement CRC check

def WriteSerialCom(serialport=serial.Serial, packet=buildtelegram.t_send(50, 84, 0)):

    serialport.flushOutput()
    serialport.flushInput()
    # convert the packet in decimal (e.g. [117, 0, 71, 0, 188]) into a byte
    # array (u\x00G\x00\xbc)
    array_to_send = bytearray(packet)
    serialport.write(array_to_send)  # send the array over the serial port

def ReadAnswer (serialport=serial.Serial, answer=[], Vmax=42, Imax=10):

    # read the answered string, something like '\x00G\x00\xbc'
    reading = serialport.read(11)
    
    intlist = [ord(item)
               for item in struct.unpack('c' * len(reading), reading)]  # convert it into an int list
    answer[:] = []  # clear the list
    # read the answer and put it into "answer" Length 11 expected
    answer.extend(intlist)

    # if the answer is too short, the checksum may be missing
    if len(answer) < 5:
        print ('ERROR: short answer (%d bytes received)' % len(answer))
    elif len(answer) == 11:
        Vnew = conversion('Voltage',answer, Vmax, Imax)
        Inew = conversion('Current',answer, Vmax, Imax)
        return Vnew, Inew
    elif len(answer) == 6:
        return 'x', 'x'
    elif len(answer)==0:
        pass
    elif len(answer) == 9:
        output = struct.unpack('>f', reading[3:-2])[0]
        return output, 'x'
    else:
        print "Unknown code received"
    # TODO: implement CRC check

# Implement a timeout function with decorator, from
# http://pguides.net/python-tutorial/python-timeout-a-function/
class TimeoutException(Exception):
    pass

def timeout(timeout_time, default):
    def timeout_function(f):
        def f2(*args):
            def timeout_handler(signum, frame):
                raise TimeoutException()
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.setitimer(signal.ITIMER_REAL,timeout_time)  # triger alarm in timeout_time seconds
            try:
                retval = f()
            except TimeoutException:
                return default
            finally:
                signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
            return retval
        return f2
    return timeout_function