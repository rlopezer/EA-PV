# EA-PV #
Little description: PV simulation control for EA-PS 2000B series power supply
#----------------------------------------------------------------------------#

EAloopread: Main file.

- Initialize main parameters
- Run the PV loop, Vpv=fcn(Ipv)

- ctrl + 'C' to break the loop and exit the system

Notes:

- By creating new copies of EAloopread.py and changing the comm ports, several sources could be controlled "simultaneously".
- If running in Windows, drivers are needed. Please, contact Elektro Automatik and have a look in: http://www.elektroautomatik.de/en/ps2000b.html
