from __future__ import absolute_import
from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import ManagerDir
from scipy import stats

class BuildingResults :
    def __init__(self, simulation_type) :
        self.simulation_type = simulation_type
    def execute(self, val_s, val_f, k) :
        if val_s < val_f :
            return "report/results/lane{}/{}/best/".format(k, self.simulation_type)
        else :
            return "report/results/lane{}/{}/worst/".format(k, self.simulation_type)
