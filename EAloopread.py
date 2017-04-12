#-coding:utf8 -*
"""
Read and control the available parameters of the EA PS200B series
power supplies, PS2042-20B & PS2084-10B.
"""

__author__      = "Ramón López-Erauskin"
__copyright__   = "Copyright 2017"
__credits__     = ["Ramón López-Erauskin"]
__license__     = "GNU General Public License v3.0"
__version__     = "1.0.0"
__maintainer__  = "Ramón López-Erauskin"
__email__       = "r.lopez.erauskin@gmail.com"
__status__      = "Prototype"

import os
import sys
import time
import serial
from datafunctions import *
from EA_VAR import *
import lookup


print BAUDRATE

try:
	if os.name == 'nt':
		ser = serial.Serial('COM5', BAUDRATE)
	else:
		ser = serial.Serial('/dev/ttyACM0', BAUDRATE)
except serial.serialutil.SerialException:
	print "Error: Could not connect to the serial port."
else: # if no exception, we can continue
	ser.bytesize = serial.EIGHTBITS
	ser.parity = serial.PARITY_ODD
	ser.stopbits = serial.STOPBITS_ONE
	print "Using serial port ", ser.name
	ser.timeout = 0.01 #11*10/115200.0  # set read timeout.
	ser.isOpen()

	time.sleep(1)

#-----------------------------------------------------------------------------#
# Get the nominal values

# Nominal voltage
answer = []
WriteSerialCom(ser, buildtelegram.t_limits(GET_NOM_V))
Vmax, x = ReadAnswer (ser, answer, 0, 0)
Vmax = int(Vmax)

# Nominal current
answer = []
WriteSerialCom(ser, buildtelegram.t_limits(GET_NOM_I))
Imax, x = ReadAnswer (ser, answer, 0, 0)
Imax = int(Imax)

# Nominal power
answer = []
WriteSerialCom(ser, buildtelegram.t_limits(GET_NOM_P))
Pmax, x = ReadAnswer (ser, answer, 0, 0)
Pmax = int(Pmax)
print 'Nominal values: %d V, %d A, %d W ' % (Vmax, Imax, Pmax)
time.sleep(2)

answer = [] # new answer
Vread, Iread = Communicate(ser, Operation['Query'], answer, Vmax, Imax)
print 'Voltage and current preset values: V = %d V and I = %d A' % (Vread, Iread)
time.sleep(2)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# Switch device to remote mode
answer = []
Vread, Iread = Communicate(ser, Operation['EnableRemote'], answer, Vmax, Imax)
print 'Device in REMOTE mode'
time.sleep(2)

# Set the parameters to safe values
# Voltage:
answer = []
WriteSerialCom(ser, buildtelegram.t_send(SET_VOLT_VAL, Vmax, 0))
V, I = ReadAnswer (ser, answer, Vmax, Imax)
# Current:
answer = []
WriteSerialCom(ser, buildtelegram.t_send(SET_CURR_VAL, Imax, Imax))
V, I = ReadAnswer (ser, answer, Vmax, Imax)

# Output ON
answer = []
Vread, Iread = Communicate(ser, Operation['EnableOutput'], answer, Vmax, Imax)
print 'Voltage and current changed to: V = %s V and I = %s A' % (Vread, Iread)
print 'Device output is ON'
time.sleep(2)
#-----------------------------------------------------------------------------#

for t in reversed (rng):
	os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
	print 'Device will go in LOOP, Vpv=fcn(Ipv) in %d secs.' % t
	time.sleep(1)

# Start the loop
while True:
	try:
		answer = []
		Vread, Iread = Communicate(ser, Operation['Query'], answer, Vmax, Imax)
		#print 'Current V and I: ', Vread, Iread
		Vpv, Ipv = lookup.PVcur().ipv(Iread)
		print 'V and I references: ', Vpv, Ipv
		WriteSerialCom(ser, buildtelegram.t_send(SET_VOLT_VAL, Vmax, Vpv))
		V, I = ReadAnswer (ser, answer, Vmax, Imax)

		answer = []
		Vnew, Inew = Communicate(ser, Operation['Query'], answer, Vmax, Imax)
		print 'New V and I: ', Vnew, Inew
		print ''
		#time.sleep(2)
	except KeyboardInterrupt:
		# Output OFF
		answer = []
		Vread, Iread = Communicate(ser, Operation['DisableOutput'], answer, Vmax, Imax)
		# Switch device to local mode
		answer = []
		Vread, Iread = Communicate(ser, Operation['DisableRemote'], answer, Vmax, Imax)
		print 'interrupted\n\n'
		ser.close()
		break
	except:
		print 'unknown error!'

sys.exit() # ? also useful in a KeyboardInterrupt exception
