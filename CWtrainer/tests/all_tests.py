#!/usr/bin/env python
import sys, traceback

import CWtrainer

#TRAINER TESTS

b=CWtrainer.Beeper(volume=0.5)
print b.params()
#print repr(b.beep_sequence([(0.01,0),(0.01,1),(0.01,0),]))

#try:
#    print repr(b.beep_sequence([(3,),(3,)]))
#except:
#    traceback.print_exc(file=sys.stdout)

import ffmpegIO, CWbasics, CWkeying

t_seq=CWkeying.Beep_Timing_From_Sequence(CWbasics.Compile("e"))

w=ffmpegIO.Writer("e.wav")
w.write(b.beep_sequence([(0.1,0)]+t_seq))
w.close()
