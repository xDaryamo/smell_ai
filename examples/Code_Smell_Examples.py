import pandas as pd
import numpy as np
import tensorflow as tf
import torch
import torch.nn.functional as F
import os as od
def pandas_lib_check():
    x = pd.DataFrame([1, 2, 3])
    y = x
    z = y.values
    c = z
