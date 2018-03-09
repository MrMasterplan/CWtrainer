#!/usr/bin/env python

import random
import os.path
import yaml
import sys

def RandCallSign(Nmin,Nmax,charset):
    """Generate random Call Signs"""
    length = random.randint(Nmin,Nmax)
    call_sign = ''.join([random.choice(charset) for i in range(length)])
    return (call_sign,)
    #the braces are doubly encloes because the whole document is also a format string

class ScriptGenerator(object):
    def __init__(self,out,templ):
        super(ScriptGenerator,self).__init__()
        self.out = out
        self.templ = templ.read() #all in memory. This is the master copy.
        self.algorithms={'RandCallSign':RandCallSign}

    def execute(self):
        #print >>self.out, self.templ
        
        controllines = []
        for line in self.templ.splitlines():
            line=line.strip()
            if line.startswith('##'):
                controllines.append(line)
        prefix = os.path.commonprefix(controllines)
        control = '\n'.join(line[len(prefix):] for line in controllines)
        
        control = yaml.load(control)
        try:
            random.seed(control['rand_seed'])
            #print 'seeded'
        except KeyError:
            pass
            
        #execute the algorithms:
        try:
            algos = control['generate']
        except KeyError,e:
            algos=[]

        if not algos:
            print >>sys.stderr, 'no algoritms specified.'
            return

        generated={}
        #here I give up on ganling all the errors individually.
        for algo in algos:
            generated[algo['name']]=''
            func = self.algorithms[algo['name']]
            for repeat_i in xrange(algo['repeat']):
                generated[algo['name']] +="# reapeat {0} of {repeat} of {name}\n".format(repeat_i,**algo)
                generated[algo['name']] +=algo['template'].format().format(*func(**algo['params']))
        
        print >>self.out, self.templ.format(**generated)

#standard
import argparse,sys


def main():
    description = "This program's funtion is to generate scrpts for the ScriptReader."
    epilog="""
This program is controlled from a template and some settings."""
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-o',metavar='out.script', dest='script', type=argparse.FileType('w'), 
                        default='-',
                        help='the path of the output file. (default -)')
    parser.add_argument('-t',metavar='control.template', dest='template', type=argparse.FileType('r'), 
                        default='-',
                        help='the template to use. (default -)')
    
    args = parser.parse_args()

    args.script
    
    generator = ScriptGenerator(out=args.script,templ=args.template )
    generator.execute()

    args.script.close()

if __name__=="__main__":
    main()
