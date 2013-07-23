#!/usr/bin/python
import curses
import os
import sys
import StringIO

from subprocess import *
import subprocess

# our screen
screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
curses.start_color()
screen.keypad(True);

# default entry color
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_CYAN)

# default error color
curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED) 

# current entry color
curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)

# line number color, invert of entry 
curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_WHITE)

# our stdin input
input_buffer = ""

# rows and columns of our screen
cols = int(subprocess.check_output(["tput", "cols"]))
rows = int(subprocess.check_output(["tput", "lines"]))

def call_process(process, string):
  process = Popen(["sed", "-e", string], stdout=PIPE, stdin=PIPE, stderr=PIPE) 
  ret = process.communicate(input_buffer)
  if(process.returncode is not 0):
    screen.addstr(ret[1][:-1].ljust(cols), curses.color_pair(2));
  else:
    screen.addstr(ret[0]);
  return


def main(argv):

  input_string = ""
  global input_buffer

  try:
    input_fh = open(argv[1], "r")
    for line in input_fh:
      input_buffer = input_buffer + line
  except:
    curses.endwin()
    sys.exit("please specify a file")
  
  # init our screen
  screen.addstr("".ljust(cols), curses.color_pair(1));
  screen.addstr(input_buffer)
  screen.addstr("EOF")

  try: 
    while 1:
      key = screen.getch()
      screen.clear()
      if(key > 256):
        continue;
      if(key == 127):
        input_string = input_string[:-1]
        screen.addstr(input_string.ljust(cols), curses.color_pair(1));
        screen.addstr(input_buffer)
        screen.addstr("EOF")
        continue;
      elif(key == 13 or key == 10):
        screen.addstr(input_string.ljust(cols), curses.color_pair(1));
        call_process("sed", input_string)
        screen.addstr("EOF")
        continue;
      else:
        input_string+=chr(key)
        screen.addstr(input_string.ljust(cols), curses.color_pair(1));
        screen.addstr(input_buffer)
        screen.addstr("EOF")
  finally:
    curses.endwin()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

