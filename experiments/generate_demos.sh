#!/usr/bin/bash


#This script generates the complete audio files from the demos.

#This generates a script from a template
#../lib/ScriptGenerator.py -t demo_control.template -o demo_template_result.script

#This is how a script is converted to audio
#../lib/ScriptReader.py -o demo_manual.wav demo_manual.script

#The intermediate script does not have to be saved is used like this:
../lib/ScriptGenerator.py -t demo_control.template -o - | ../lib/ScriptReader.py -o demo_control.mp3 -  

