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

def call_process(process, pipe, stdin):
  process = Popen(["sed", pipe], stdout=PIPE, stdin=PIPE, stderr=PIPE) 
  ret = process.communicate(stdin)
  if(process.returncode is not 0):
    return (ret[1], 1)
  else:
    return (ret[0], 0)
  return

def call_pipes(a, pipe_array):

  # start first one with input buffer
  ret = call_process("sed", pipe_array[0], input_buffer)

  if(len(pipe_array) == 1):
    if(ret[1] != 0):
        error = "Error on line 0:" + ret[0][:-1]
        screen.addstr(error.ljust(cols), curses.color_pair(4));
    else:
      screen.addstr(ret[0])
    return

  p = ret[0];
  for i in range(1, len(pipe_array)):
    ret = call_process("sed", pipe_array[i], p);
    if(ret[1] != 0):
        error = "Error on line " + str(i) + ":" + ret[0][:-1]
        screen.addstr(error.ljust(cols), curses.color_pair(4));
    else:
      p = ret[0];
  
  screen.addstr(p)

def update(pipe_array, current_pipe):
  draw_pipes(pipe_array, current_pipe)
  call_pipes("sed", pipe_array)
  screen.addstr("EOF")

def draw_pipes(pipe_array, current_pipe):

  for pipe, num in map(None, pipe_array, range(0, len(pipe_array))):
    color = 1
    if(num == current_pipe):
      color = 3

    screen.addstr(num, 0, str(num), curses.color_pair(2)) 
    screen.addstr(num, len(str(num)), " " + pipe.ljust(cols - len(str(num)) - 1), curses.color_pair(color))


def main(argv):

  pipe_array = [];
  command_array = [];
  enable_array = [];
  pipe_array.append("");
  current_pipe = 0;
  key = 0
  
  global cols
  global rows 
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

  screen.addstr(rows - 1, 0, argv[1] + " " + str(key) + " " + str(current_pipe))
  try: 
    while 1:
      key = screen.getch()
      screen.clear()
      screen.addstr(rows - 1, 0, argv[1] + " " + str(key) + " " + str(current_pipe))
      if(key == 410):
        cols = int(subprocess.check_output(["tput", "cols"]))
        rows = int(subprocess.check_output(["tput", "lines"]))
      # ENTER
      if(key == 10):
        pipe_array.insert(current_pipe+1, "")
        current_pipe = current_pipe + 1
        update(pipe_array, current_pipe)
        continue 
      # UP
      if(key == 259):
        if(current_pipe is not 0):
          current_pipe = current_pipe - 1;
        update(pipe_array, current_pipe)
        continue;
      # DOWN
      if(key == 258):
        if(current_pipe == len(pipe_array) -1):
          pipe_array.append("");
        current_pipe = current_pipe + 1;
        update(pipe_array, current_pipe);
        continue;
      # BACKSPACE
      if(key == 263):
        if(len(pipe_array[current_pipe]) is not 0):
          pipe_array[current_pipe] = pipe_array[current_pipe][:-1]
        else:
          if(current_pipe is not 0):
            del pipe_array[current_pipe]
            current_pipe = current_pipe - 1
        update(pipe_array, current_pipe)
        continue;
      else:
        if(key < 256):
          pipe_array[current_pipe]+=chr(key)
        update(pipe_array, current_pipe);
  finally:
    curses.endwin()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

