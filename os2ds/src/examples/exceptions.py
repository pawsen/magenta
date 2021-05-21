#!/usr/bin/env python3

class ReprException(Exception):
   def __str__(self):
      return repr(self)

class NoreprException(Exception):
   pass

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


try:
   raise NoreprException('My Useful Error Message!')
except Exception as e:
    print(f"{e}")

try:
   raise ReprException('My Useful Error Message!')
except Exception as e:
    print(f"{e}")
