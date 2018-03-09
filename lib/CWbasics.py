
from FormatException import FormatException


def Compile(phrase):
    sequence = ''
    lastletter=None
    for rawletter in phrase:
        letter=rawletter.lower()
        if letter in CW_alphabet:
            if letter != ' ' or  lastletter != ' ': #ignore multi space
                sequence += CW_alphabet[letter] + ' '
            
            lastletter = letter
        else:
            raise FormatException("Symbol %s has no CW code point."%rawletter)
    return sequence

class Dummy:
    pass
units = Dummy()
units.dit = 1
units.dah = 3
units.inter_symbol = 1
units.inter_letter = 3
units.inter_word = 7

class CWletter(list):
    """
    .length is the length in units
    len() is the number of symbols
    iterate to get each symbol
    .letter is plain text.
    """
    def __init__(self,letter,didah):
        super(CWletter, self).__init__()
        self.letter=letter
        
        symlengths = {".":units.dit, "-":units.dah} #with pause
        
        self.unit_length = -units.inter_symbol
        #the pause after the last symbol 
        #is not part of the letter
        
        for symbol in didah:
            if symbol not in ".-":
                raise ValueError("Invalid use of CWletter")
            self.append(symbol)

            self.unit_length+=symlengths[symbol]
            self.unit_length+=units.inter_symbol
        
        

class CW_inter_word(object):
    def __init__(self):
        super(CW_inter_word,self).__init__()
        self.unit_length = units.inter_word
        self.letter = " "

#source: http://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1677-1-200910-I!!PDF-E.pdf
CW_alphabet = {
#letters
    "a" : ".-",
    "b" : "-...",
    "c" : "-.-.",
    "d" : "-..",
    "e" : ".",
    "f" : "..-.",
    "g" : "--.",
    "h" : "....",
    "i" : "..",
    "j" : ".---",
    "k" : "-.-",
    "l" : ".-..",
    "m" : "--",
    "n" : "-.",
    "o" : "---",
    "p" : ".--.",
    "q" : "--.-",
    "r" : ".-.",
    "s" : "...",
    "t" : "-",
    "u" : "..-",
    "v" : "...-",
    "w" : ".--",
    "x" : "-..-",
    "y" : "-.--",
    "z" : "--..",
#numbers
    "0" : "-----",
    "1" : ".----",
    "2" : "..---",
    "3" : "...--",
    "4" : "....-",
    "5" : ".....",
    "6" : "-....",
    "7" : "--...",
    "8" : "---..",
    "9" : "----.",
#punctuation
    "." : ".-.-.-",
    "," : "--..--",
    ":" : "---...",
    "?" : "..--..",
    "'" : ".----.",
    "-" : "-....-",
    "/" : "-..-.",
    "(" : "-.--.",
    ")" : "-.--.-",
    '"' : ".-..-.",
    "=" : "-...-",
    "+" : ".-.-.",
    "@" : ".--.-.",
#break
    " " : "" #this makes sense for the compiler
}


def Unit_Length_of_Repeating_Sequence(phrase):
    #Warning! This only works for space-free phrases
    signs = Compile(phrase.strip(" ")+" ") #the space makes it repeat
    symlengths = {".":units.dit, "-":units.dah}

    total=0
    lastitem = None
    for item in signs:
        if item in '.-':
            #print item.letter, item, item.unit_length
            total += symlengths[item]
            total += units.inter_symbol # a letter_space after
            lastitem = item
        elif item == ' ':
            if lastitem in '.-':
                total -= units.inter_symbol # the last space was a mistake
                total += units.inter_letter # a letter_space after
                lastitem = ' '
            elif lastitem == ' ':
                total -= units.inter_letter # the last space was a mistake
                total += units.inter_word # double space means word break
                lastitem = '  '
            elif lastitem == '  ':
                pass
                #more than two spaces have no meaning
            else:
                assert(1==0) #this cannot be reached

        else:
            raise TypeError("invalid type of symbol")
    
    return total
    
##############
#Tests below here
if __name__ == "__main__":
    result = Unit_Length_of_Repeating_Sequence("PARIS")
    print 'Unit_Length_of_Repeating_Sequence("PARIS") =',result
    assert(result==50)
    result = Unit_Length_of_Repeating_Sequence("CODEX")
    print 'Unit_Length_of_Repeating_Sequence("CODEX") =',result
    assert(result==60)
    r=Compile("ee e   e")
    print 'Compile("ee e   e") = "%s"'%r
    assert(r=='. .  .  . ')

    print "All tests passed."
