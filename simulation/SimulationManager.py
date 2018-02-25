from __future__ import absolute_import
from __future__ import print_function

import time
import os
import sys
from multiprocessing import Process, Value, Lock
import Simulation
import Config
import ManagerDir

class SimulationManager :

    def __init__(self, thread_limit = 8) :
        self.count = Value('i', thread_limit)
        self.lock = Lock()
        self.name_data = ["Queue Length", "Wait time", "Mean speeds"]
        self.data_type = ["queue", "wait_time", "mean_speeds"]
        self.simulation_type = ['f', 's']
        self.mapping = {}
        self.mapping['f'] = "Fixed"
        self.mapping['s'] = "Smart"
        self.metric_results = ["inconclusive", "best", "worst"]
        self.ordem_simulations = []
        self.simulations = {}
        self.managerdir = ManagerDir.ManagerDir()
        self.managerdir.create("report/csv")
        for k in range(1, 5) :
            with open("report/csv/lane_{}.csv".format(k), "w") as csv :
                print("\"Simulation type\";\"Wait time\";\"Queue Length\";\"Mean speeds\"", file = csv)
        self.managerdir.create("report/results")
        self.data_distribution = {}
        for i in self.data_type :
            self.data_distribution[i] = {}
            for j in self.simulation_type :
                self.data_distribution[i][j] = {}
                for k in range(1,5) :
                    self.data_distribution[i][j][k] = list()
        for i in range(1,5) :
            self.managerdir.create("report/csv/unit/lane{}/".format(i))
            for j in self.name_data :
                for k in self.metric_results :
                    self.managerdir.create("report/results/lane{}/{}/{}".format(i, j, k))

    def increment(self):
        with self.lock:
            self.count.value += 1
    def decrement(self):
        with self.lock:
            self.count.value -= 1
    def available(self):
        with self.lock:
            return self.count.value >= 2

    def prepare(self) :

        finish_simulations = set()
        try:
            fileKeys = open("history.txt", 'r')
            for k in fileKeys.read().split():
                finish_simulations.add(k)
        except :
            pass
        for i in range(1,2,1):
            for j in range(1,2,1):
                for k in range(i,2,1):
                    for l in range(j,2,1):
                        flow = [i/10.0,j/10.0,k/10.0,l/10.0]
                        name = str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l)
                        if name in finish_simulations :
                            continue
                        self.simulations[name] = Process(target=self.my_thread, args=(name, flow,))
                        self.ordem_simulations.append(name)

    def prepare_total_result(self, datas) :
        for k in range(1, 5) :
            with open("report/csv/lane_{}.csv".format(k), "a") as csv :
                for j in self.simulation_type :
                    print("\"{}\";\"{}\";\"{}\";\"{}\"".format(self.mapping[j], datas["wait_time"][j][k], datas["queue"][j][k], datas["mean_speeds"][j][k]), file = csv)

    def my_thread(self,threadID, flow) :
        self.decrement()
        with open("progress.txt", "a") as files:
            print("Iniciando a thread", threadID, file=files)
        cur_config = Config.Config()
        simulation = Simulation.Simulation(self.plotting, cur_config.traci, self.managerdir)
        cur_config.run()
        simulation.run(flow)
        averages = simulation.get_averages()
        self.prepare_total_result(averages)
        self.statistic.run_unit_result(flow, simulation.data)
        with open("progress.txt", "a") as files:
            print("A thread", threadID, "acabou.", file=files)
        with open("history.txt", "a") as files:
            print(threadID, end=" ", file=files)
        self.increment()

    def run(self) :
        start = time.time()
        with open("progress.txt", "w") as files:
            print("#################################################################", file=files)
            print("A quantidade de simulacoes eh:", len(self.simulations) , file=files)
            print("#################################################################", file=files)

        for k in self.ordem_simulations:
            while( not self.available() ):
                pass
            self.simulations[k].start()

        for k in self.simulations:
            self.simulations[k].join()
        self.statistic.run_total_result()
        print("Finalizacao de todas as threads.")
        with open("progress.txt", "a") as files:
            print("Tempo total de simulacao:", time.time() - start, file=files)

simulation_manager = SimulationManager()
simulation_manager.prepare()
simulation_manager.run()
