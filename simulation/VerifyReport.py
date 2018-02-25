# -*- coding:utf-8 -*-

import sys
import os

class VerifyReport :
    def __init__(self) :
        self.metrics_name = ["Queue Length", "Wait time", "Mean speeds"]
        self.result_names = ["best", "inconclusive", "worst"]
        self.path = os.getcwd()
        self.bigset = set()

    def initialize(self) :
        for i in self.metrics_name :
            for j in xrange(1,5) :
                for k in self.result_names :
                    path = self.path + "/report/results/lane{}/{}/{}/".format(j,i,k)
                    getfiles = set(os.listdir(path))
                    self.bigset = self.bigset.union(getfiles)

    def run(self) :
        for i in xrange(1,17) :
            for j in xrange(1,17) :
                for k in xrange(i, 17) :
                    for l in xrange(j, 17) :
                        cur_flow = [str(i/10.0),str(j/10.0),str(k/10.0),str(l/10.0)]
                        name_flow = "flow_" + "_".join(map(str, cur_flow)) + ".txt"
                        if name_flow not in self.bigset :
                            print(name_flow, "Was not in simulation!")


verify = VerifyReport()
verify.initialize()
verify.run()
