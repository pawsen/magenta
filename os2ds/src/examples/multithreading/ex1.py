#!/usr/bin/env python3

import multiprocessing as mp
import os

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name):
    info('function f')
    print('hello', name)

def foo(q):
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    q.put(['hello', 42, None])

def append_to_shared_mem(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

def modify_mem_using_manager_proxy(d, l):
    d[1] = '1'
    d['2'] = 2
    d[0.25] = None
    l.reverse()

if __name__ == '__main__':
    # XXX there should only be one set_start_method in a program
    mp.set_start_method('fork')  # fork is default on Unix
    # parent id: id of shell
    info('main line')
    # now: parent id: id of this python process
    p = mp.Process(target=f, args=('bob',))
    # start: prepare the Process.run(). Must be called once and only once
    p.start()
    # join: blocks until Process terminates. Can be called multiple times
    p.join()


    q2 = mp.Queue()
    p2 = mp.Process(target=foo, args=(q2,))
    p2.start()
    print(q2.get())
    p2.join()

    # XXX instead of using set_start_program, we get a context object and use
    # multiple start_methods per program
    ctx = mp.get_context('spawn')
    q3 = ctx.Queue()
    p3 = ctx.Process(target=foo, args=(q3,))
    p3.start()
    print(q3.get())
    p3.join()


    print("share memory between processes")
    num = mp.Value('d', 0.0)
    arr = mp.Array('i', range(10))
    p4 = mp.Process(target=append_to_shared_mem, args=(num, arr))
    p4.start()
    p4.join()
    print(num.value)
    print(arr[:])

    # Managers provide a way to create data which can be shared between
    # different processes,
    print(
        """use Manager to allow other processes to manipulate with the memory
Manager holds""")
    with mp.Manager() as manager:
        d = manager.dict()
        l = manager.list(range(10))

        p = mp.Process(target=modify_mem_using_manager_proxy, args=(d, l))
        p.start()
        p.join()

        print(d)
        print(l)
