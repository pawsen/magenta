#!/usr/bin/env python3



class customException(Exception):
   def __init__(self, value):
      self.parameter = value

   # def __str__(self):
   #    return repr(self.parameter)
   def __str__(self):
      return repr(self)
try:
   raise customException('My Useful Error Message!')
except customException as e:
    print(f"{e}")
    print('Caught: ' + e.parameter)
