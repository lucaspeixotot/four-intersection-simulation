#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import Config
import sys

class Simulation:
    def __init__(self, traci, delta1, delta2, delta3, delta4):
        self.traci = traci
        self.in_deltas = [delta1, delta2, delta3, delta4]


    def initialize(self):
        # TLS Programs/Phases
        self.l2_green = 'GGrrGGrr'
        self.l2_yellow = 'yyrryyrr'
        self.l1_green = 'rrGGrrGG'
        self.l1_yellow = 'rryyrryy'
        self.program_fixed = [self.l1_green, self.l1_yellow , self.l2_green, self.l2_yellow]
        self.tls_names = {}
        self.tls_names[1] = "center"
        self.tls_names[2] = "center_2"
        self.tls_names[3] = "center_3"
        self.tls_names[4] = "center_4"

        # TLS time phases
        self.delta_fixed = 40
        self.amber_phase_fixed = 3
        self.timestep = 0


        self.tls_time_fixed = {}
        self.pid_fixed = {}
        for i in range(1, 5) :
            self.tls_time_fixed[i] = 0
            self.pid_fixed[i] = 0

        for i in range(1, 5) :
            self.traci.trafficlights.setRedYellowGreenState("%s" % (self.tls_names[i]),self.program_fixed[self.pid_fixed[1]])


        self.delta_fixed = {}
        for i in range(1, 5) :
            self.delta_fixed[i] = self.in_deltas[i-1] + self.amber_phase_fixed

        self.data = {}
        self.averages = {}
        self.name_data = ["wait_time"]
        for _ in self.name_data:
            self.data[_] = {}
            self.averages[_] = [0, 0, 0, 0, 0]
            for i in range(1, 5):
                self.data[_][i] = [[], [], [], [], []]

    def collect_wait_time(self):
        for i in range(1, 5):
            average = 0
            for j in range(1, 5):
                self.data["wait_time"][i][j].append(self.traci.lane.getWaitingTime('l{}_{}_0'.format(i, j)))
                average += (self.data["wait_time"][i][j][self.timestep]) / (max(self.timestep, 1))
            self.averages["wait_time"][i] += average


    def update_tls(self):
        # Update fixed light
        for i in range(1, 5) :
            self.tls_time_fixed[i] += 1
            if self.tls_time_fixed[i] == self.delta_fixed[i] - self.amber_phase_fixed :
                self.traci.trafficlights.setRedYellowGreenState("%s" % (self.tls_names[i]), self.program_fixed[self.pid_fixed[i] + 1])
            elif self.tls_time_fixed[i] == self.delta_fixed[i] :
                self.tls_time_fixed[i] = 0
                self.pid_fixed[i] = (self.pid_fixed[i] + 2) % len(self.program_fixed)
                self.traci.trafficlights.setRedYellowGreenState("%s" % (self.tls_names[i]),self.program_fixed[self.pid_fixed[i]])

    def run(self):
        self.initialize()
        while self.traci.simulation.getMinExpectedNumber() > 0:
            self.traci.simulationStep()
            self.collect_wait_time()
            self.update_tls()
            self.timestep += 1
        self.traci.close()
        print(self.averages)

if __name__ == "__main__":
    myConfig = Config.Config()
    print(sys.argv)
    mySimulation = Simulation(myConfig.traci, int(sys.argv[1]), int(sys.argv[2]),
            int(sys.argv[3]), int(sys.argv[4]))
    myConfig.run()
    mySimulation.run()
