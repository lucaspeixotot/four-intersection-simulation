from __future__ import absolute_import
from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import ManagerDir
from scipy import stats

class BuildingResultsMeanSpeeds :
    def __init__(self) :
        pass
    def execute(self, val_s, val_f, k) :
        if val_s > val_f :
            return "report/results/lane{}/Mean speeds/best/".format(k)
        else :
            return "report/results/lane{}/Mean speeds/worst/".format(k)
