# -*-coding:utf8 -*

"""
Building telegrams depending on the operation to be executed.
Documentation (Elektro-Automatik): 
# ps2000b_programming.pdf 
# object_list_ps2000b_de_en.pdf
"""

__author__      = "Ramón López-Erauskin"
__copyright__   = "Copyright 2017"
__credits__     = ["Ramón López-Erauskin"]
__license__     = "GNU General Public License v3.0"
__version__     = "1.0.0"
__maintainer__  = "Ramón López-Erauskin"
__email__       = "r.lopez.erauskin@gmail.com"
__status__      = "Prototype"

def t_limits(byteOBJquery):
    # SD byte. It determines that data are queried 113 01
    byteSDquery = 115 # '011100110: query data, broadcast, telegram from pc to device, length = 4-1. We can also use 112 !!

    byteDNquery = 0  # For Single model the DN is ignored but recommended to be left zero

    # data field not used since it is a query

     # The checksum of the telegram follows directly after byte 2
    temp = hex(byteSDquery + byteDNquery + byteOBJquery)[2:].zfill(4)
    byteCS1query = int(temp[0:2], 16)
    byteCS2query = int(temp[2:4], 16)

    # Put the succesive telegram in decimal into a column vector
    telegram_query = [byteSDquery, byteDNquery,
                      byteOBJquery, byteCS1query, byteCS2query]
    return telegram_query

# To send the query to receive the actual values
def t_query():
    # SD byte. It determines that data are queried
    byteSDquery = 117 # '01110101': query data, broadcast, telegram from pc to device, length = 6-1

    byteDNquery = 0  # For Single model the DN is ignored but recommended to be left zero

    # The object determines what the device will do
    byteOBJquery = 71  # Query device state, actual values

    # data field not used since it is a query

     # The checksum of the telegram follows directly after byte 2
    temp = hex(byteSDquery + byteDNquery + byteOBJquery)[2:].zfill(4)
    byteCS1query = int(temp[0:2], 16)
    byteCS2query = int(temp[2:4], 16)

    # Put the succesive telegram in decimal into a column vector
    telegram_query = [byteSDquery, byteDNquery,
                      byteOBJquery, byteCS1query, byteCS2query]
    return telegram_query


# Telegrams for power supply control
# SD byte = 'send data' (C0) + 'singlecast' (00) + 'direction from PC'
# (10) + 'data length=2' (01)
def t_remote(activate=False):
    byteSD_control = 241  # byteSD_activate = int('F1',16);
    byteDN_control = 0  # For Single model the DN is ignored but recommended to be left zero
    byteOBJ_control = 54  # object number for power supply control
    # Bytes selected according to the action wanted
    # Mask to say which bit of object 54 should be treated
    byteMask_remotecontrol = int('10', 16)  # Remote control, bit 4
    
    if activate is True:
        # Activate remote= put 1 in the bit corresponding to
        byteControl = int('10', 16)# the mask (bit 4 so 0x10 or 0b10000 or
                                            # 0d16)
    else:
        # Deactivate remote= put 0 in the bit corresponding to
        byteControl = int('00', 16) # the mask (bit 4, 0 in any base)

    temp = hex(byteSD_control + byteDN_control + byteOBJ_control +
               byteMask_remotecontrol + byteControl)[2:].zfill(4)
    byteCS1_activate = int(temp[0:2], 16)
    byteCS2_activate = int(temp[2:4], 16)
    telegram_remote = [byteSD_control, byteDN_control, byteOBJ_control,
                         byteMask_remotecontrol, byteControl, byteCS1_activate, byteCS2_activate]
    return telegram_remote


def t_output(on=False):
    byteSD_control = 241  # byteSD_activate = int('F1',16);
    byteDN_control = 0  # For Single model the DN is ignored but recommended to be left zero
    byteOBJ_control = 54  # object number for power supply control
    byteMask_poweroutput = int('01', 16)   # Power output, bit 0
    
    if on is True:
        # Power output ON
        byteControl = int('01', 16)
    else:
        # Power output OFF
        byteControl = int('00', 16)

    temp = hex(byteSD_control + byteDN_control + byteOBJ_control +
               byteMask_poweroutput + byteControl)[2:].zfill(4)
    byteCS1 = int(temp[0:2], 16)
    byteCS2 = int(temp[2:4], 16)
    telegram_output = [byteSD_control, byteDN_control, byteOBJ_control,
                   byteMask_poweroutput, byteControl, byteCS1, byteCS2]
    return telegram_output


# To send the voltage reference
# The last 4 telegram are adjusted in the Simulink model in function of the
# actual voltage reference


def t_send(byteOBJsend=50, max_value=84, value=0):
    gain_meas = 25600
    # SD byte. It determines that data are sent to the device
    SDsend = [0] * 8
    SDsend[0:2] = [1, 1]  # send data
    SDsend[2] = 1  # telegram broadcast to all device nodes (there is only 1)
    SDsend[3] = 1  # telegram direction: "1"-> from PC to device
    # 1 because the voltage reference is an int -> 2 bytes -> 2-1=1
    SDsend[4:8] = bin(1)[2:].zfill(4)
    SDsend = [int(item) for item in SDsend]
    bindata = ''.join([str(item) for item in SDsend])
    byteSDsend = int(bindata, 2)

    byteDNsend = 0  # For Single model the DN is ignored but recommended to be left zero

    value_to_send = int(round(value*gain_meas/max_value))

    conv = hex(value_to_send)[2:].zfill(4)
    byteVal1send = int(conv[0:2], 16)
    byteVal2send = int(conv[2:4], 16)
    temp1 = hex(byteSDsend + byteDNsend + byteOBJsend +
                byteVal1send + byteVal2send)[2:].zfill(4)
    byteCS1send = int(temp1[0:2], 16)
    byteCS2send = int(temp1[2:4], 16)
    telegram_send = [byteSDsend, byteDNsend, byteOBJsend, byteVal1send, byteVal2send, byteCS1send, byteCS2send]
    return telegram_send
