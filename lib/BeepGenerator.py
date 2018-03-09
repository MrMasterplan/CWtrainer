#!/usr/bin/env python

import math
from math import cos, sin, pi
import CWtrainer
from CWkeying import Merge_Equal_Levels

class BufferedBeeper(CWtrainer.Beeper):
    def __init__(self, frequency=800.0, volume=1.0, bandwidth=100., samprate=22050):
        CWtrainer.Beeper.__init__(self,frequency=frequency, volume=volume, bandwidth=bandwidth, samprate=samprate)
        #super(BeepGenerator,self).__init__()
        self.cache={}

    def beep_sequence(self,seq):
        seq=Merge_Equal_Levels(seq)
        
        res=''
        
        #do we start on a zero?
        if seq[0][1]==0:
            res+=self._get_sub_sequence(seq[0:1])
            seq.pop(0)

        while len(seq)>=2:
            res+=self._get_sub_sequence(seq[0:2])
            seq.pop(0)
            seq.pop(0)

        if len(seq):
            res+=self._get_sub_sequence(seq[0:1])
            seq.pop(0)

        assert(seq==[])
        return res
        
    
    def _get_sub_sequence(self,seq):
        try:
            return self.cache[tuple(seq)]
        except KeyError:
            #worth a try
            pass
        res = CWtrainer.Beeper.beep_sequence(self,seq)
        self.cache[tuple(seq)]=res
        return res

#the following has been commmented out. It is unmaintained and untested.
# class BeepGenerator(object):
#     def __init__(self, freq=800.0, bandwidth=100.0, volume=1.0, out=None):
#         super(BeepGenerator,self).__init__()
#         self.freq = freq
#         self.bandwidth=bandwidth
#         self._set_out(out)
#         self.lastamp=0
#         self.volume = volume
    
#     def _set_out(self,out):
#         #import WAVBase
#         #if not isinstance(out,WAVBase.WaveWrite):
#         #    raise IOError()
#         # no check. let it fail if it is not complying
#         self.out=out

#     def _beep_level(self,duration,level):
#         """
#         add a beep of the specified duration and level.
#         if the previous command was of a different level,
#         ramp first.
#         """
#         if self.out is None:
#             raise IOError("outfile must be set")
#         now = self.out.getTime()
#         beep_start = now
#         beep_end = now + duration
#         newamp = self.volume * level

#         if self.lastamp !=newamp:
#             #we need to ramp
#             ramp_end = beep_start + 1./self.bandwidth
#             if ramp_end > beep_end:
#                 raise Error("bandwith is too low or pulse too short.")
            
#             oldamp = self.lastamp
            
#             while now < ramp_end:
#                 now=self.out.getTime()
#                 ramp = (1-cos(pi  * self.bandwidth * (now-beep_start)))/2
#                 #the following will ramp the amplitude 
#                 # from one level to the other
#                 amp = newamp * ramp + oldamp * (1-ramp) 
#                 frame = amp * sin(2*pi*self.freq*now)
#                 self.out.write1(frame)
            
#             self.lastamp=newamp
#         #possible ramp is done.
        
#         if newamp!=0.:
#             while now < beep_end:
#                 now=self.out.getTime()
#                 frame = newamp * sin(2*pi*self.freq*now)
#                 self.out.write1(frame)
#         else:
#             while now < beep_end:
#                 now=self.out.getTime()
#                 self.out.write1(0.)


#     def beep(self,duration):
#         """
#         add a beep of the specified duration.
#         if the previous command was a beep, continue.
#         otherwise, ramp up first.
#         """
#         self._beep_level(duration, 1.)

#     def pause(self,duration):
#         """
#         add a pause of the specified duration.
#         if the previous command was a pause, continue.
#         otherwise, ramp down first.
#         """
#         self._beep_level(duration, 0.)
    
#     def beep_sequence(self,sequence):
#         """sequence shall be a list of (duration,level) tuples"""
#         for item in sequence:
#             self._beep_level(*item)
        
#         return sum(item[0] for item in sequence)
        
