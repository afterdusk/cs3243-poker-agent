import ctypes
import os

omp_eval = ctypes.CDLL(os.path.dirname(__file__) + '/lib/ompeval.so')
omp_eval.argtypes = [
        ctypes.c_ulonglong,
        ctypes.c_ubyte,
        ctypes.c_ubyte,
        ctypes.c_ubyte,
        ctypes.c_byte,
        ctypes.c_byte,
        ctypes.c_byte,
        ctypes.c_byte,
        ctypes.c_byte]
omp_eval.restype = ctypes.c_ulonglong

def evaluate(n_sim, hole, community):
    a = [n_sim] + hole + [len(community)] + community + ([-1] * (5 - len(community)))
    return omp_eval.evaluate(*a)
