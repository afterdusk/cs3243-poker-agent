import math

def logistic(center, scale, k, offset):
    return lambda x: float(scale) / (1 + math.exp(-k * (x - center))) + offset

def tanh(center, scale, k, offset):
    return lambda x: scale * math.tanh(k * (x - center)) + offset
