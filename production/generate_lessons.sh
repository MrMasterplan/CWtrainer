#!/bin/bash

for i in {1..6}; do
    ../lib/ScriptGenerator.py -t lesson$i.template -o - | ../lib/ScriptReader.py -o lesson$i.mp3 - & 
done

wait
echo Done!
