#!/usr/bin/env python

#standard
import subprocess
import os, wave

#custom
import CWtrainer
import ffmpegIO

#The following four methods are what needs to be changed if one wishes
#to use a different text to speech reader.
#The beeper uses 16 bit singed audio encoding and it is therefore
# important that the files are read this way also.
#if a different encoding is used by the text 2 speech program,
# the ffmpegIO Reader should be used to transcode it.
def CompletePath(path):
    if not path.endswith('.wav'):
        path+='.wav'
    return path

def ReadContents(path, samplerate, channels=1):
    path = CompletePath(path)
    #return ffmpegIO.Read(path) #this adds 0.9s to a typical program run
    
    #context manager would be nice: https://bugs.python.org/issue17616
    # im running 2.7.6, ubuntu default
    wavefile = wave.open(path,"r")
    
    if (wavefile.getframerate() != samplerate or 
        wavefile.getnchannels() != channels):
        wavefile.close()
        raise IOError("file has unexpected format.")
        
    nframes = wavefile.getnframes()
    data = CWtrainer.NonZeroSubArray(wavefile.readframes(nframes))
    wavefile.close()
    return data


def GetSamplerate(path):
    path = CompletePath(path)
    #return ffmpegIO.samplerate  #for ffmpegIO
    
    #context manager would be nice: https://bugs.python.org/issue17616
    wav = wave.open(path,'r') 
    rate = wav.getframerate()
    wav.close()
    return rate

def Text2Speech(path,phrase):
    path = CompletePath(path)

    exe = ["espeak",
           "-s", "175", #-s <integer>  Speed in words per minute, 80 to 450, default is 175
           "-p", "50", #-p <integer> Pitch adjustment, 0 to 99, default is 50
           "-g0", #-g <integer> Word gap. Pause between words, units of 10mS at the default speed
           "-w"]#output wav
    exe +=[path,phrase]
    
    #print 'Calling >$', ' '.join(exe)
    subprocess.call(exe)
    return 

class Speaker(object):
    """
    use this to get wav files with spoken stuff.
    """
    def __init__(self,cachedir):
        super(Speaker,self).__init__()
        
        #define where to write stuff
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        self.cachedir = cachedir

        self.samplerate=self.getSamplerate()

        #the followin will hold references to previously rendered files.
        self.library={}
    
    def getSamplerate(self,testphrase='a'):
        cachefile = CompletePath(os.path.join(self.cachedir,str(hash(testphrase))))
        if not os.path.isfile(cachefile):
            Text2Speech(cachefile,testphrase)
        return GetSamplerate(cachefile)

    def speak(self,phrase):
        #see if we have run this before
        try:
            return self.library[phrase]
        except KeyError, e:
            #worth a try
            pass
        
        #see if this phrase is in the cache.
        #the following block allows one to "speak" any file, 
        #even music if the phrase is a valid path
        cachefile = os.path.join(self.cachedir,phrase)
        if not os.path.isfile(CompletePath(cachefile)):
            #see if we have hashed it before:
            cachefile = os.path.join(self.cachedir,str(hash(phrase)))
            if not os.path.isfile(CompletePath(cachefile)):
                #we have to speak it
                Text2Speech(cachefile,phrase)

        self.library[phrase]=ReadContents(cachefile,samplerate=self.samplerate)
        return self.library[phrase]
