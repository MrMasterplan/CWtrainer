# CWtrainer
Generator for audio language lessons to learn CW (audible morse code)

# Build Instructions
0. build in ubuntu.
1. make sure that you have all the dependencies as listed in install_prerequisites.sh
2. source reinstall.sh (only the first time. next time just source setup.sh)
3. If there are no errors everything should work now. Go into experiments and run ./generate_demos.sh

# Usage
The basic premise is that there is a reader program that can read a script and speak and morse as necessary to put together a training program. It tunred out that I wanted a simple way of generating long random lessons so I added the Generator later.

There are two main entry points for the user: lib/ScriptGenerator.py and lib/ScriptReader.py
The usage is best explored by diving a bit down into the demos contained in experiments/

# Explore
The results of the demos and the production runs can be found here:
https://clyp.it/user/smcqcyac

