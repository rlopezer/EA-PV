#-coding:utf8 -*

"""
# Load CSV files into arrays, LookUp Tables (LUT)
# Voltage and current loops: The LUT's closest value and position
to the sensed variable is considered and both variables are taken as reference
"""

__author__      = "Ramón López-Erauskin"
__copyright__   = "Copyright 2017"
__credits__     = ["Ramón López-Erauskin"]
__license__     = "GNU General Public License v3.0"
__version__     = "1.0.0"
__maintainer__  = "Ramón López-Erauskin"
__email__       = "r.lopez.erauskin@gmail.com"
__status__      = "Prototype"

import csv
import bisect

#def curve():
class PVcur:

    def __init__(self):
        # Get the limit values from the table
        with open('PVcurve.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            # Limiting values
            temp = []
            temp2 = []
            for row in reader:
                temp += float(row[0]),
                temp2 += float(row[1]),
            self.Vmax = max(temp)
            self.Vmin = min(temp)
            self.Imax = max(temp2)
            self.Imin = min(temp2)
        #print self.Vmax
        with open('PVcurve.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            self.VIcurve = []
            self.IVcurve = []
            for row in reader:
                self.VIcurve += [float(row[0]), float(row[1])],
                self.IVcurve += [float(row[1]), float(row[0])],
        self.VIcurve.sort()
        self.IVcurve.sort()


    def vpv(self, Vpv):
        if Vpv > self.Vmax: Vpv = self.Vmax
        elif Vpv < self.Vmin: Vpv = self.Vmin

        pos = bisect.bisect(self.VIcurve, [Vpv,])
        [V,I] = self.VIcurve[pos]
        [Vpre,Ipre] = self.VIcurve[pos-1]
        if abs(V-Vpv) > abs(Vpv-Vpre):
            pos = pos-1
        #print 'Lookup Table references. For %s V -> %s' % (Vpv, self.VIcurve[pos])
        [V,I] = self.VIcurve[pos]
        return V, I

    def ipv(self, Ipv):
        if Ipv > self.Imax: Ipv = self.Imax
        elif Ipv < self.Imin: Ipv = self.Imin
        
        pos = bisect.bisect(self.IVcurve, [Ipv,])
        [I,V] = self.IVcurve[pos]
        [Ipre,Vpre] = self.IVcurve[pos-1]
        if abs(I-Ipv) > abs(Ipv-Ipre):
            pos = pos-1
        #print 'Lookup Table references. For %s A-> %s' % (Ipv, self.IVcurve[pos])
        [I,V] = self.IVcurve[pos]
        return V, I
