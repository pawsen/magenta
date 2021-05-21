#!/usr/bin/env python3.8
import sys
import gc

"""
Examples of garbage collection and generations
Requires python => 3.8 because of the `generation` keyword in `gc.get_objects()`

https://devguide.python.org/garbage_collector/
https://github.com/c-bata/pysigdump/blob/master/sigdump.py
"""

def gc_stat():
    """print gc generation info"""
    print("  GC stat:")
    for i, generation in enumerate(gc.get_stats()):
        print(f"    Generation {i}:")
        print(f"      collections   : {generation.get('collections')}")
        print(f"      collected     : {generation.get('collected')}")
        print(f"      uncollectable : {generation.get('uncollectable')}")



# reference counting
x = object()
print(f"x-ref, {sys.getrefcount(x)}")
y = x
print(f"x-ref with y, {sys.getrefcount(x)}")
del y
print(f"x-ref del y,{sys.getrefcount(x)}")

#  container holds a reference to itself, so even when we remove our reference
#  to it (the variable “container”) the reference count never falls to 0 because
#  it still has its own internal reference. Therefore it would never be cleaned
#  just by simple reference counting
container = []
container.append(container)
print(f"con-ref, { sys.getrefcount(container) }")
del container
# a circular linked list which has one link referenced by a variable A, and one
# self-referencing object which is completely unreachable:
class Link:
   def __init__(self, next_link=None):
       self.next_link = next_link

link_3 = Link()
link_2 = Link(link_3)
link_1 = Link(link_2)
link_3.next_link = link_1
A = link_1
del link_1, link_2, link_3

link_4 = Link()
link_4.next_link = link_4
del link_4

gc_stat()
# Collect the unreachable Link object (and its .__dict__ dict).
print(f"gc.collect, { gc.collect() }")
gc_stat()

# Generations are collected when the number of objects that they contain reaches
# some predefined threshold, which is unique for each generation and is lower
# the older the generations are.
print(f"gc.get_threshold, { gc.get_threshold() }")

# The content of these generations can be examined using the
# gc.get_objects(generation=NUM) function
class MyObj:
   pass

# Move everything to the last generation so it's easier to inspect
# the younger generations.
gc.collect()

# Create a reference cycle.
x = MyObj()
x.self = x

# Initially the object is in the youngest generation.
z = gc.get_objects(generation=0)
print(f"object, gen=0,  {z}")

# After a collection of the youngest generation the object
# moves to the next generation.
print(f"gc.collect, {gc.collect(generation=0)}")
print(f"object, gen=0, {gc.get_objects(generation=0)}")
print(f"object, gen=1, {gc.get_objects(generation=1)}")


# gc generation stats
gc_stat()
