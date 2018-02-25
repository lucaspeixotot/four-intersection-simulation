#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import Config

class Simulation:
    def __init__(self, traci):
        self.traci = traci


    def initialize(self):
        # TLS Programs/Phases
        self.l2_green = 'GGrrGGrr'
        self.l2_yellow = 'yyrryyrr'
        self.l1_green = 'rrGGrrGG'
        self.l1_yellow = 'rryyrryy'
        self.prepare = 'rrrrrrrr'
        self.program = [self.l2_green, self.l2_yellow, self.l1_green, self.l1_yellow]
        self.program_fixed = [self.l1_green, self.l1_yellow ,self.l2_green, self.l2_yellow]

        # TLS time phases
        self.delta = [20, 45, 30, 63, 30, 63]
        self.delta_fixed = 40
        self.amber_phase = 3
        self.amber_phase_fixed = 5
        self.tls_time = 0
        self.tls_time_fixed = 0
        self.cycle_time = 0
        self.cycle_number = 1
        self.ret = []

        # Counters
        self.pid = 0
        self.pid_fixed = 0
        self.did = 0
        self.J1_Fixed = 0
        self.timestep = 0
        self.grids = list()

        # Rates/datas
        self.data = {}
        self.averages = {}
        self.name_data = ["wait_time"]
        for _ in self.name_data:
            self.data[_] = {}
            self.averages[_] = [0, 0, 0, 0, 0]
            for i in range(1, 5):
                self.data[_][i] = [[], [], [], [], []]

        self.rates = {}
        self.rates['departure'] = [0,0,0,0,0]
        self.rates['amber_departure'] = [0,0,0,0,0]
        self.rates['arrival'] = [0,0,0,0,0]
        self.last_vehicles = {}
        self.last_vehicles['departure'] = set()
        self.last_vehicles['amber_departure'] = set()
        self.last_vehicles['arrival'] = set()

    def addFlow(self, ID , begin , end , tax , typeCar , route ):

        self.flows[ID] = {}
        self.flows[ID]['qt_step'] = int(tax)
        qt = int((end-begin)*(tax-int(tax)))
        self.flows[ID]['time'] = [begin,end]
        self.flows[ID]['typeCar'] = typeCar
        self.flows[ID]['route'] = route
        self.flows[ID]['period'] = int((end-begin)+1)
        if qt != 0 : self.flows[ID]['period'] = int((end-begin)//qt)

    def removeFlow(self,ID):
        del self.flows[ID]

    def runFlow(self):
        old = set()
        for flows in self.flows:
            flow = self.flows[flows]
            if flow['time'][1] < self.flow_time:
                old.add(flows)
                continue
            elif flow['time'][0] > self.flow_time:
                continue
            else :
                for i in range(1, flow['qt_step']+1 ):
                    self.traci.vehicle.add("Veh_" + str(self.flow_time) + "_" + str(i) + "_" + flows, routeID=flow['route'], typeID=flow['typeCar'])
                if( (self.flow_time != flow['time'][0]) and (self.flow_time - flow['time'][0]) % flow['period'] == 0 ):
                    self.traci.vehicle.add("Veh_" + str(self.flow_time) + "_0_" + flows, routeID=flow['route'], typeID=flow['typeCar'])

        for e in old:
            self.removeFlow(e)
        self.flow_time+=1

    def init_flow(self, rates) :
        # Flows
        self.flows = {}
        ## Flow lane 1
        self.addFlow(ID="Car1f", begin=200,end=7400,tax=rates[0],typeCar="CarA", route="l1_-l3_f")
        self.addFlow(ID="Car1s", begin=200, end=7400, tax=rates[0], typeCar="CarA", route="l1_-l3_s")
        ## Flow lane 2
        self.addFlow(ID="Car2f", begin=200,end=7400,tax=rates[1],typeCar="CarA", route="l2_-l4_f")
        self.addFlow(ID="Car2s", begin=200, end=7400, tax=rates[1], typeCar="CarA", route="l2_-l4_s")
        ## Flow lane 3
        self.addFlow(ID="Car3f", begin=200,end=7400,tax=rates[2],typeCar="CarA", route="l3_-l1_f")
        self.addFlow(ID="Car3s", begin=200, end=7400, tax=rates[2], typeCar="CarA", route="l3_-l1_s")
        ## Flow lane 4
        self.addFlow(ID="Car4f", begin=200,end=7400,tax=rates[3],typeCar="CarA", route="l4_-l2_f")
        self.addFlow(ID="Car4s", begin=200, end=7400, tax=rates[3], typeCar="CarA", route="l4_-l2_s")


    def collect_departure(self):
        tls_state = self.traci.trafficlights.getRedYellowGreenState('center_2')
        for i in range(1,5) :
            if self.traci.lanearea.getLastStepVehicleNumber('departure_l{}'.format(i)) > 0 :
                self.actual_vehicles = self.traci.lanearea.getLastStepVehicleIDs("departure_l{}".format(i))
                if (tls_state == self.l1_yellow or tls_state == self.l2_yellow):
                    for x in self.actual_vehicles :
                        if x not in self.last_vehicles['amber_departure'] :
                            self.rates['amber_departure'][i] += 1
                            self.last_vehicles['amber_departure'].add(x)
                else :
                    for x in self.actual_vehicles :
                        if x not in self.last_vehicles['departure'] :
                            self.rates['departure'][i] += 1
                            self.last_vehicles['departure'].add(x)

    def collect_arrival(self) :
        for i in range(1,5) :
            if self.traci.lanearea.getLastStepVehicleNumber('arrival_l{}'.format(i)) > 0 :
                self.actual_vehicles = self.traci.lanearea.getLastStepVehicleIDs('arrival_l{}'.format(i))
                for x in self.actual_vehicles :
                    if x not in self.last_vehicles['arrival'] :
                        self.rates['arrival'][i] += 1
                        self.last_vehicles['arrival'].add(x)

    def collect_data(self):
        for i in range(1, 5):
            average = 0
            for j in range(1, 5):
                self.data["wait_time"][i][j].append(self.traci.lane.getWaitingTime('l{}_{}_0'.format(i, j)))
                average += self.data["wait_time"][i][j][self.timestep]
            self.averages["wait_time"][i] += average

    def reset_rates(self) :
        self.rates = {}
        self.rates['departure'] = [0,0,0,0,0]
        self.rates['amber_departure'] = [0,0,0,0,0]
        self.rates['arrival'] = [0,0,0,0,0]

    def update_tls(self):
        self.cycle_time += 1
        self.tls_time += 1
        self.tls_time_fixed += 1

        # Update fixed light
        if self.tls_time_fixed == self.delta_fixed - self.amber_phase_fixed :
            self.traci.trafficlights.setRedYellowGreenState("center", self.program_fixed[self.pid_fixed+1])
        elif self.tls_time_fixed == self.delta_fixed :
            self.tls_time_fixed = 0
            self.pid_fixed = (self.pid_fixed + 2) % len(self.program_fixed)
            self.traci.trafficlights.setRedYellowGreenState("center",self.program_fixed[self.pid_fixed])


    def start_context(self,l1_start, l2_start, l3_start, l4_start) :
        # Start context lane 1
        self.addFlow(ID="Car1fc", begin=0,end=100,tax=l1_start,typeCar="CarA", route="l1_-l3_f")
        self.addFlow(ID="Car1sc", begin=0, end=100, tax=l1_start, typeCar="CarA", route="l1_-l3_s")

        # Start context lane 2
        self.addFlow(ID="Car2fc", begin=0,end=100,tax=l2_start,typeCar="CarA", route="l2_-l4_f")
        self.addFlow(ID="Car2sc", begin=0, end=100, tax=l2_start, typeCar="CarA", route="l2_-l4_s")

        # Start context lane 3
        self.addFlow(ID="Car3fc", begin=0,end=100,tax=l3_start,typeCar="CarA", route="l3_-l1_f")
        self.addFlow(ID="Car3sc", begin=0, end=100, tax=l3_start, typeCar="CarA", route="l3_-l1_s")

        # Start context lane 4
        self.addFlow(ID="Car4fc", begin=0,end=100,tax=l4_start,typeCar="CarA", route="l4_-l2_f")
        self.addFlow(ID="Car4sc", begin=0, end=100, tax=l3_start, typeCar="CarA", route="l4_-l2_s")

    def prepare_context(self) :
        self.traci.trafficlights.setRedYellowGreenState("center_2", self.prepare)
        self.traci.trafficlights.setRedYellowGreenState("center", self.prepare)
        self.flows = {}
        self.start_context(0.20, 0.19, 0.14, 0.12)
        self.flow_time = 0
        while self.flow_time < 200:
            self.traci.simulationStep()
            self.runFlow()

        self.traci.trafficlights.setRedYellowGreenState("center_2", self.l2_green)
        self.traci.trafficlights.setRedYellowGreenState("center", self.l1_green)

    def report(self):
        # Might be useful to return .JSON
        pass

    def get_averages(self):
        for i in self.name_data:
            for j in self.name_type:
                for k in range(1,5) :
                    self.averages[i][j][k] = self.averages[i][j][k] / float(self.timestep)
        return self.averages

    def run(self, rates):
        self.initialize()
        # self.prepare_context()
        # self.init_flow(rates)
        while self.traci.simulation.getMinExpectedNumber() > 0:
            self.traci.simulationStep()
            #self.collect_arrival()
            #self.collect_departure()
            #self.update_tls()
            self.collect_data()
            self.timestep += 1
            #self.runFlow()
        # self.myPlotting.plot(self.data,self.grids)

        self.traci.close()
        print(self.averages)

if __name__ == "__main__":
    myConfig = Config.Config()
    mySimulation = Simulation(myConfig.traci)
    myConfig.run()
    mySimulation.run([1,2,3,4])

#     for i in range(1, 11, 1):
#         for j in range(1, 11 , 1):
#             for k in range(1, 11,1):
#                 for l in range(1,11,1):
#                     myConfig.run()
#                     print('{} - {} - {} - {}'.format(i, j, k, l))
#                     mySimulation.run([i/10.0,j/10.0,k/10.0,l/10.0])
#                     averages = mySimulation.get_averages()
#                     myStatistic.prepare_datas(averages)
#                     myStatistic.run_unit_result([i/10.0,j/10.0,k/10.0,l/10.0], mySimulation.data)
#     myStatistic.run_total_result()
