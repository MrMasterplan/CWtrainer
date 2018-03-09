
"""
This library will allow me to read and write anything
that ffmpeg can handle, and do so while preserving my 
internal audio representation as here described.

For this I use ffmpeg to convert all read files to my 
internal representation as raw data on a pipe.
Similarly I pipe written data to ffmpeg as raw and have 
it convert it to the desired format.
"""

from subprocess import Popen, PIPE

samplerate = 22050
channels = 1
internal_fmt='s16le' #the Beeper uses this. ony change it if you know what you are doing
max_out_time=3600 * 10

ffmpeg = ['ffmpeg',
          '-y', #overwrite output
          '-v', '0' #shut up
]

def ffmpegFormats(select = 'E'):
    """Expects ffmpeg to output something like:
File formats:
 D. = Demuxing supported
 .E = Muxing supported
 --
 D  3dostr          3DO STR
  E 3g2             3GP2 (3GPP2 file format)
  E 3gp             3GP (3GPP file format)
 D  4xm             4X Technologies
  E a64             a64 - video for Commodore 64

"""
    if select not in ['D','E','',None]:
        raise ValueError('Must selectt D, E or nothing')
    
    p=Popen(ffmpeg+['-formats'],stdout=PIPE)
    result,stderr = p.communicate()

    lines = result.splitlines()
    if lines[3] != " --":
        #basic format check
        raise Exception('Unexpected output from ffmpeg')
        
    formats=[]
    for line in lines[4:]:
        DE = line[1:3]
        if select and select not in DE:
            continue
        
        items = line[4:].split(' ')

        formats+= items[0].split(',')
        
    return list(set(formats))

def Read(path,samplerate = samplerate):
    executable = ffmpeg[:] + ['-i', path] #input
    executable += [ '-f', internal_fmt, #format to write
                    '-t', str(max_out_time), #protect from too large times
                    '-ar',str(samplerate),
                    '-ac',str(channels),
                    'pipe:1']
    
    res = Popen(executable,stdout=PIPE)
    data,stderr=res.communicate() #get all the data
    return data

class Writer(object):
    def __init__(self,pathorfile, fmt=None, samplerate=samplerate):
        super(Writer,self).__init__()

        self.iopenedit = False
        if isinstance(pathorfile,basestring):
            #we have to open the file ourself.
            self.iopenedit = True
            self.handle = open(pathorfile,'wb')
            if not self.handle:
                raise IOError('Could not open file.')
        else:
            self.handle = pathorfile
        
        if fmt is None:
            #we have to get the format from the file name
            try:
                typeending_i = self.handle.name.rindex('.')
                fmt = self.handle.name[typeending_i+1:]
            except:
                raise Exception("Could not determine format.")

        if fmt not in ffmpegFormats('E'):
            raise ValueError('invalid format.')

                    
        self.fmt = fmt
            
        self.samplerate = samplerate
        executable = ffmpeg[:]
        executable += [ '-f', internal_fmt, #format to write
                        #'-t', str(max_out_time), #protect from too large times
                        '-ar',str(self.samplerate),
                        '-ac',str(channels),
                        '-i','pipe:0', #read from pipe
                        '-f',str(self.fmt),
                        'pipe:1'] #write to stdout

        self.proc = Popen(executable,stdin=PIPE,stdout=self.handle)

    def write(self,data):
        self.proc.stdin.write(data)

    write_raw = write
    
    def close(self):
        try:
            self.proc.communicate()
        except:
            pass
        
        if self.iopenedit:
            self.handle.close()

    def __del__(self):
        self.close()

