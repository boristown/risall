# -*- coding: utf-8 -*-
# filename: Console.py

import ZeroAI
import sys

while True:
  print ('input :')
  value = sys.stdin.readline()
  print (ZeroAI.chat(value))
