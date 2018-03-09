#!/usr/bin/env python

import speak
from BeepGenerator import BufferedBeeper
import CWtrainer
import CWkeying, CWbasics
#import WAVBase
import ffmpegIO
from FormatException import FormatException

samplerate = ffmpegIO.samplerate

from copy import deepcopy
import os

class ScriptReader(object):
    def __init__(self, cachedir=None):
        super(ScriptReader,self).__init__()

        self.speaker = speak.Speaker(cachedir=cachedir)

        self.default_settings = {'WPM':12.,
                         'Farnsworth':500.,
                         'freq':800.,
                         'bandwidth':100.,
                         'volume':0.5
                         }
        self.user_settings={}
        self.UpdateFromSettings()

    def UpdateFromSettings(self,additions={}):
        """re-initialize all that has changable settings"""
        news = deepcopy(self.default_settings)
        news.update(self.user_settings)
        
        #apply settings
        news.update(additions)
        
        #parse values
        for setting in self.default_settings.iterkeys():
            try:
                news[setting]=float(news[setting])
            except ValueError:
                raise FormatException("Unable to parse value '%s'."%news[setting])
        #use the settings
        self.beeper=BufferedBeeper(frequency=news['freq'],
                                     volume=news['volume'],
                                     bandwidth=news['bandwidth'],
                                     samprate=self.speaker.samplerate)
        self.timing = CWkeying.CWtiming(WPM=news['WPM'],
                                        Farnsworth=news['Farnsworth'])   
        
        #we got this far so the input must be ok.
        self.user_settings.update(additions)

    def speak(self, phrase):
        self.out.write(self.speaker.speak(phrase))

    def pause(self,duration):
        self.out.write(self.beeper.beep_sequence([(float(duration),0)]))

    def spell(self,phrase):
        for l in phrase:
            self.speak(l)
            self.pause(0.1)

    def morse(self, phrase):
        self.key_sequence(CWbasics.Compile(phrase))

    def key_sequence(self,sequence):
        t_seq=CWkeying.Beep_Timing_From_Sequence(sequence,self.timing)
        self.out.write(self.beeper.beep_sequence(t_seq))

    def process(self,script, out):
        self.out = out
        
        for lineno, line in enumerate(script):
            try:
                line = line.strip(' \t\n')

                #empty
                if not line:
                    continue
                    
                #comment
                if line.startswith('#'):
                    continue
            
                #command : argument
                command,sep,argument = line.partition(':')
                if not sep:
                    raise FormatException('Invalid line format.')
                command = command.strip(' \t\n')
                argument = argument.strip(' \t\n')

                if command =='speak':
                    self.speak(argument)
                elif command == 'spell':
                    self.spell(argument)
                elif command == 'pause':
                    try:
                        dur = float(argument)
                    except ValueError:
                        raise FormatException("invlaid duration '%s'"%argument)
                    self.pause(dur)
                elif command == 'morse':
                    self.morse(argument)
                elif command =='set':
                    self.process_setting(argument)
                elif command == 'key':
                    self.key_sequence(argument)
                else:
                    raise FormatException("invlaid command '%s'"%command)
                
            except FormatException,e:
                print >>sys.stderr, 'Error on line %i: %s'%(lineno, line)
                print >>sys.stderr, '    ', e
            #except BaseException, e:
             #   print >>sys.stderr, 'Unknown error on line %i: %s'%(lineno, line)
              #  continue

    def process_setting(self,argument):
        key,sep,value = argument.partition(':')
        if not sep:
            raise FormatException("Invlaid setting format.")
        key = key.strip(' \t\n')
        value = value.strip(' \t\n')
        
        if key not in self.default_settings:
            raise FormatException("Invlaid setting '%s'."%key)
        self.UpdateFromSettings({key:value})


#standard
import argparse,sys

def main():
    description = "This program's funtion is to output CW learning audio files."
    epilog="""This program is contolled from a script file which shall follow 
the following format. A line starting with # is a comment. 
Every line shall be of the form "command: argument".

Possible commands are:

speak
    the argument text is spoken freely
pause
    the duration in seconds will be paused
spell
    the argument will be spelled letter for letter
morse
    the argument will be morsed.
set
    to adjust parameters

"""
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--profile', dest='profile', 
                        action='store_true', 
                        help='profile the program')
    parser.add_argument('script', type=argparse.FileType('r'), 
                        help='the path of the script')
    parser.add_argument('-o',metavar='out.mp3', dest='output', 
                        type=argparse.FileType('w'), 
                        default='out.mp3',
                        help='the path of the output file.')
    parser.add_argument('-c','--cache', metavar='cachedir',dest='cache', 
                        type=str, default="./CW_speak_cache/",
                        help='location to store and read audio.') 
    parser.add_argument('-f', metavar='fmt',dest='fmt', 
                        type=str, default=None,
                        help='output format for ffmpeg.')
   
    
    args = parser.parse_args()
    
    pr=None
    if args.profile:
        import cProfile
        
        pr = cProfile.Profile()
        pr.enable()
    
    reader = ScriptReader(cachedir=args.cache)

    if args.fmt == 'raw':
        #this is mostly for performance analysis
        outputter = args.output
    else:
        outputter = ffmpegIO.Writer(args.output,
                                    fmt=args.fmt,
                                    samplerate = reader.speaker.samplerate)
    
    reader.process(args.script, outputter)

    outputter.close()
    

    if pr:
        pr.disable()
        pr.print_stats(sort='cumtime')        

if __name__=="__main__":
    main()
