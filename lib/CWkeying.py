
import CWbasics
from FormatException import FormatException

class CWtiming(object):
    def __init__(self, WPM=12, Farnsworth=15, WPM_phrase="PARIS"):
        super(CWtiming,self).__init__()
        if WPM < Farnsworth:
            Farnsworth = WPM
        self.WPM = WPM
        self.Farnsworth = Farnsworth
        self.WPM_phrase = WPM_phrase
        self.Calculate()
    
    def Calculate(self):
        #find out what to divide by
        length = CWbasics.Unit_Length_of_Repeating_Sequence(self.WPM_phrase)
        self.key_unit_time = 60./(self.WPM*length)
        self.pause_unit_time = 60./(self.Farnsworth*length)
        self.Farnsworth_extra_pause = self.pause_unit_time - self.key_unit_time

default_timing = CWtiming()

def Beep_Timing_From_Sequence(sequence,timing = default_timing,units=CWbasics.units):
    #To be filled with pairs of (duration, level)
    time_list = []
    key_unit = timing.key_unit_time

    lastitem = ''
    letterlength=0
    for item in sequence:
        if item in '.-':
            lastitem=item
            
            #get them here bacause an imperfect keyer may vary them randomly
            if item == '.':
                sym_length = units.dit
            else:
                sym_length = units.dah
            break_length = units.inter_symbol

            time_list+=[(sym_length * key_unit, 1.)] #the symbol
            time_list+=[(break_length * key_unit, 0.)] #the break

            letterlength += sym_length + break_length

        elif item == ' ':
            if lastitem in '.-':
                #letter break
                lastitem = ' '
                
                # pop the last sym break.
                time_list.pop() 
                #if this has varied, we'll make a mistake:
                letterlength -= CWbasics.units.inter_symbol

                #extend the letter to how long it would be in farnsworth
                if timing.Farnsworth_extra_pause > 0.: 
                    #don't append an empty pause
                    time_list.append((timing.Farnsworth_extra_pause 
                                      * letterlength, 0. ))
                letterlength = 0 #ready for next letter
            
                #now we need a letter break.
                time_list.append((timing.pause_unit_time *
                                  CWbasics.units.inter_letter, 0. ))

            elif lastitem == ' ':
                #word break
                lastitem = '  '
                
                # remove the inter_letter space, it was a mistake.
                time_list.pop() # pop the last break.

                time_list.append((timing.pause_unit_time * 
                                  CWbasics.units.inter_word, 0. ))
            elif lastitem == '  ':
                pass
                #more than two spaces have no meaning
            else:
                assert(1==0) #this cannot be reached
        else:
            raise FormatException("invalid symbol in sequence: '%s'"%item)

    return Merge_Equal_Levels(time_list)

def Merge_Equal_Levels(seq):
    newseq=[]
    for item in seq:
        #first item
        if not newseq:
            newseq.append(item)
            continue

        #add the durations of identical levels
        if item[1] == newseq[-1][1]:
            newseq[-1] = (item[0] + newseq[-1][0], item[1])
        else:
            newseq.append(item)
    return newseq


def Beep_Timing_From_Phrase(phrase,timing = default_timing):
    return Beep_Timing_From_Sequence(CWbasics.Compile(phrase.strip()),timing)


##############
#Tests below here
if __name__ == "__main__":
    timing = CWtiming(1/50.,1/100.)
    print 'unit time at 1/50. :', timing.key_unit_time
    print 'farn time at 1/50. :', timing.pause_unit_time
    assert(timing.key_unit_time==1.)
    assert(timing.pause_unit_time==2.)
    #print Beep_Timing_From_Sequence('.. .   -',CWtiming(1/50.))
    print Beep_Timing_From_Sequence('.. .-   -',timing)
    
