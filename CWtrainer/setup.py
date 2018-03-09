#!/usr/bin/env python
from distutils.core import setup, Extension

module1 = Extension('CWtrainer',
                    define_macros = [],#('MAJOR_VERSION', '1'),
                                       #('MINOR_VERSION', '0')],
                    include_dirs = ['./include'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['src/CWtrainer.c',
                               'src/array_functions.c',
                               'src/Beeper.c',])

import sys
if len(sys.argv) <2:
    sys.argv.append('install')

setup (name = 'CWtrainer',
       version = '0.1',
       description = 'Compiled aspects of the CWtrainer',
       author = 'Simon Heisterkamp',
#       author_email = '',
#       url = 'https://docs.python.org/extending/building',
#       long_description = '''
#This is really just a demo package.
#''',
       ext_modules = [module1])
