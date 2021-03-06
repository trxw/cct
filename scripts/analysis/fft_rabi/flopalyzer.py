'''
flopalyzer.py

Take the FFT of a Rabi flop for finding the laser projection.
May be updated later to do more stuff.
'''

import numpy as np
from numpy import fft
import matplotlib.pyplot as plt
import labrad
from labrad import units as U
from labrad.units import hbar, amu

class Flopalyzer:

    def __init__(self, date, datasetname):
        self.date = date
        self.datasetname = datasetname
        data = self.get_data()
        self.time = data[:,0]
        self.excitation = data[:,1]
        self.freq, self.pos_freq_components = self.do_fft()
    
    def get_data(self):
        cxn = labrad.connect()
        self.context = cxn.context()
        self.dv = cxn.data_vault
        dv = self.dv
        self.directory = ['', 'Experiments', 'RabiFlopping', self.date, self.datasetname]
        
        dv.cd(self.directory, context=self.context)
        dv.open(1, context=self.context)
        data = dv.get(context=self.context)
        
        sideband_selection = dv.get_parameter('RabiFlopping.sideband_selection', context=self.context)
        print sideband_selection
        try:
            sideband_number = sideband_selection.index(1)
            print sideband_number
        except:
            print "Not a first order blue sideband! I can't figure out eta for you!"
            sideband_number = None

        if sideband_number is not None:
            sideband_list = [                         
                             'TrapFrequencies.radial_frequency_1',
                             'TrapFrequencies.radial_frequency_2',
                             'TrapFrequencies.axial_frequency', 
                             'TrapFrequencies.rf_drive_frequency']

            sideband = sideband_list[sideband_number]
            print sideband
            self.trap_frequency = dv.get_parameter(sideband, context=self.context)
            print dv.get_parameter(sideband, context=self.context)
        return data.asarray

    def do_fft(self):
        tf = self.time[-1]*1e-6
        n = len(self.excitation)
        x = fft.fft(self.excitation)
        pos_freq_components = [U.WithUnit(j, 'Arb') for j in np.abs(x[1:n/2])]
        freq = [ U.WithUnit(j, 'kHz') for j in (np.arange(1,n/2)/tf)/1e3] # freq in kHz
        
        return freq, pos_freq_components
    
    def make_plots(self):
        plt.figure(1)
        plt.subplot(211)
        plt.plot(self.time,self.excitation)
        plt.subplot(212)
        plt.plot(self.freq,np.abs(self.pos_freq_components))
        plt.show()
    
    def compute_projection(self, bareRabi):
        '''
        May need a better peak detection algorithm in future
        '''
        
        wavelength = U.WithUnit(729.0, 'nm')
        m = 40*amu
        chi =  2*np.pi/wavelength['m']*np.sqrt(hbar['J*s']/(2.*m['kg']*2.*np.pi*self.trap_frequency['Hz']))
        freq_data = list(np.abs(self.pos_freq_components))        
        maxElemIndex = freq_data.index(max(freq_data))
        peakFreq = self.freq[maxElemIndex]*1e3 # freq in Hz
        theta = U.WithUnit( np.arccos(peakFreq/(chi*bareRabi['Hz']))*180.0/np.pi , 'deg' )
        return theta

    def save_to_data_vault(self):
        '''
        Save the fft data to datavault
        '''
        dv = self.dv
        dv.cd(self.directory, context=self.context)
        dv.new('Rabi Flopping FFT', [('Frequency', 'Arb')], [('FFT', 'Arb','Arb')], context=self.context)
        dv.add_parameter('plotLive', True, context=self.context)
        dv.add_parameter('Window', 'Rabi FFT', context=self.context)
        data = np.transpose(np.vstack((self.freq, self.pos_freq_components)))
        dv.add( data, context=self.context)

    def compute_lines(self, bareRabi):
        wavelength = U.WithUnit(729.0, 'nm')    
        m = 40*amu
        chi =  2*np.pi/wavelength['m']*np.sqrt(hbar['J*s']/(2.*m['kg']*2.*np.pi*self.trap_frequency['Hz']))
        print chi
        first = np.cos(np.pi/4)*chi*bareRabi
        second = np.sqrt(2)*first
        print self.freq
        print first
        print second 

if __name__ == "__main__":

    bareRabi = U.WithUnit(101372.0, 'Hz')

    date = '2013Jul18'
    #datasetname = '1550_25'
    datasetname = '1756_09'
    #datasetname = '1744_17'
    f = Flopalyzer(date, datasetname)
    #print "Projection: " + str(f.compute_projection(bareRabi))
    f.compute_lines(bareRabi)

    #f.make_plots()

    f.save_to_data_vault()
