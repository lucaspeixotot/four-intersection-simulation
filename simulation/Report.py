# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import prints
import ManagerDir
from scipy import stats
import pandas as pd
import Plotting

class Report :
    def __init__(self) :
        self.metrics_name = ["Queue Length", "Wait time", "Mean speeds"]
        self.result_names = ["best", "inconclusive", "worst"]
        self.simulation_type = ["Fixed", "Smart"]
        self.map = {}
        self.map["s"] = "Smart"
        self.map["f"] = "Fixed"
        self.map_data = {}
        self.map_data['queue'] = "Queue Length"
        self.map_data['wait_time'] = "Wait time"
        self.name_data = ["wait_time", "queue"]
        self.name_type = ['f', 's']
        self.manager = ManagerDir.ManagerDir()
        self.path = os.getcwd()
        self.flows = {}
        self.results = {}
        self.result_order = {}
        self.geral_results = {}
        self.a = {}
        self.best_boxplot_data = {}
        self.geral_results_data = {}
        self.total_results = {}
        self.mapping = {}
        self.flow_scenario = {}
        self.mapping["Queue Length"] = 1
        self.mapping["Wait time"] = 0
        self.geral_results = list()

    def initialize(self) :
        for i in self.result_names :
            self.flows[i] = {}
            self.results[i] = {}
            self.total_results[i] = {}
            self.result_order[i] = {}
            for j in self.metrics_name :
                self.flows[i][j] = list()
                self.total_results[i][j] = {}
                for k in xrange(5) :
                    self.total_results[i][j][k] = 0

        for i in xrange(1,10) :
            self.flow_scenario[i] = list()

        for i in self.metrics_name :
            for j in range(1,5) :
                for k in self.result_names :
                    path = self.path + "/report/results/lane{}/{}/{}/".format(j,i,k)
                    getfiles = set(os.listdir(path))
                    self.flows[k][i].append(getfiles)

        for i in self.metrics_name:
            self.a[i] = {}
            self.best_boxplot_data[i] = {}
            self.geral_results_data[i] = {}
            for w in self.simulation_type :
                self.best_boxplot_data[i][w] = {}
                self.geral_results_data[i][w] = {}
                for k in range(1,5) :
                    self.best_boxplot_data[i][w][k] = list()
                    self.geral_results_data[i][w][k] = list()
            for j in self.result_names:
                self.a[i][j] = list()

    def build_scenario(self) :
        set_scenarios = set()
        scenarios = {}
        for i in xrange(1,9) : scenarios[i] = {}
        scenarios[1][1] =  [ [6,8],[6,8],[-1,-1],[-1,-1] ]
        scenarios[2][1] =  [ [11,14],[11,14],[-1,-1],[-1,-1] ]
        scenarios[3][1] =  [ [1,3],[1,3],[-1,-1],[-1,-1] ]
        scenarios[4][1] =  [ [1, 5],[1, 5],[-1, 6],[11,17] ]
        scenarios[4][2] =  [ [1, 5],[1, 5],[11, 17],[-1,6] ]
        scenarios[5][1] =  [ [1, 5],[1, 5],[11, 17],[11,17] ]
        scenarios[6][1] =  [ [1, 5], [1, 13], [-1, 5], [-1, -1] ]
        scenarios[6][2] =  [ [1, 13], [1, 5], [-1, -1], [-1, 5] ]
        scenarios[7][1] =  [ [1, 5],[1, 5],[-1, 5],[11,17] ]
        scenarios[7][2] =  [ [1, 5],[1, 5],[11, 17],[-1, 5] ]
        scenarios[8][1] =  [ [6, 8],[1, 5],[-1, -1],[11,17] ]
        scenarios[8][2] =  [ [1, 5],[6, 8],[11, 17],[-1, -1] ]
        print("A")
        for w in xrange(1,9) :
            for t in xrange(1,3) :
                if t not in scenarios[w] : continue

                for i in xrange( scenarios[w][t][0][0] , scenarios[w][t][0][1]) :

                    for j in xrange( scenarios[w][t][1][0] , scenarios[w][t][1][1]) :
                        kk = i
                        kkk = i+3
                        if(  scenarios[w][t][2][0]!= -1 ) :
                            kk = scenarios[w][t][2][0]
                        if( scenarios[w][t][2][1] != -1 ) :
                            kkk = scenarios[w][t][2][1]

                        for k in xrange( kk , kkk) :
                            ll = j
                            lll = j+3
                            if(  scenarios[w][t][3][0]!= -1 ) : ll = scenarios[w][t][3][0]
                            if( scenarios[w][t][3][1] != -1 ) : lll = scenarios [w][t][3][1]

                            for l in xrange(ll, lll) :
                                for lane in xrange(1,5) :
                                    ar = list(map(str, [i/10.0, j/10.0, k/10.0, l/10.0]))
                                    cur_flow = "flow_" + '_'.join(ar) + ".csv"
                                    if cur_flow == "flow_0.4_0.3_0.4_1.4.csv" : continue
                                    self.flow_scenario[w].append(cur_flow)
                                    set_scenarios.add(cur_flow)

            print(len(self.flow_scenario[w]))
        print("B")
        print("Com os 8 cenários resultaram {} fluxos diferentes".format(len(set_scenarios)))

    def reset_boxplot(self) :
        self.scenario_boxplot_data = {}
        self.lane_dataframe = {}
        for i in self.name_data :
            self.lane_dataframe[i] = {}
            for j in self.name_type :
                self.lane_dataframe[i][j] = {}
        for i in self.metrics_name:
            self.scenario_boxplot_data[i] = {}
            for w in self.simulation_type :
                self.scenario_boxplot_data[i][w] = {}
                for k in range(1,5) :
                    self.scenario_boxplot_data[i][w][k] = list()


    def building_best_results(self) :
        for i in range(1, 17) :
            for j in range(1, 17) :
                for k in range(i, 17) :
                    for l in range(j, 17) :
                        cur_flow = [str(i/10.0),str(j/10.0),str(k/10.0),str(l/10.0)]
                        name_flow = "flow_" + "_".join(map(str, cur_flow)) + ".txt"
                        for result_name in self.result_names :
                            self.result_order[result_name][name_flow] = 0
                            self.results[result_name][name_flow] = {}
                            for metric in self.metrics_name :
                                lanes = []
                                for lane in range(4) :
                                    if name_flow in self.flows[result_name][metric][lane] :
                                        lanes.append(lane+1)
                                if (metric != "Mean speeds"):
                                    self.result_order[result_name][name_flow] += len(lanes)
                                self.results[result_name][name_flow][metric] = lanes
                                self.total_results[result_name][metric][len(lanes)] += 1
                                if( len(lanes) == 4 ):
                                    self.a[metric][result_name].append(name_flow)

    def building_total_results(self):
        print("Gerando nome dos flows")
        for i in range(1, 17) :
            for j in range(1, 17) :
                for k in range(i, 17) :
                    for l in range(j, 17) :
                        total_flow = [str(i/10.0),str(j/10.0),str(k/10.0),str(l/10.0)]
                        name_flow = "flow_" + "_".join(map(str, total_flow)) + ".csv"
                        if name_flow == 'flow_0.4_0.3_0.4_1.4.csv': continue
                        self.geral_results.append(name_flow)
        print("Flows gerados com sucesso")

    def best_boxplot_simulations_data(self) :
        print("Preparando os dados")
        for metric in ["Queue Length", "Wait time"] :
            for cur_flow in self.a[metric]["best"] :
                cur_flow = cur_flow[:cur_flow.rfind(".")] + ".csv"
                for lane in range(1,5) :
                    path = "report/csv/unit/lane%d/%s" % (lane, cur_flow)
                    data_flow = pd.read_csv(path, sep=";", na_values=".")
                    for simulation_type in self.simulation_type :
                        flow_data_type = data_flow.loc[data_flow["Simulation type"] == simulation_type]
                        array_describe = flow_data_type.describe().get_values()
                        self.best_boxplot_data[metric][simulation_type][lane].append(array_describe[1][self.mapping[metric]])
        print("Fim da preparação os dados")

    def getting_total_results_data(self) :
        print("Preparando dados gerais")
        for metric in ["Queue Length", "Wait time"] :
            for cur_flow in self.geral_results :
                for lane in range(1,5) :
                    path = "report/csv/unit/lane%d/%s" % (lane, cur_flow)
                    print("Lendo %s" % (cur_flow))
                    data_flow = pd.read_csv(path, sep=";", na_values=".")
                    print("%s lido com sucesso!" % (cur_flow))
                    for simulation_type in self.simulation_type :
                        print("Pegando a media")
                        flow_data_type = data_flow.loc[data_flow["Simulation type"] == simulation_type]
                        array_describe = flow_data_type.describe().get_values()
                        self.geral_results_data[metric][simulation_type][lane].append(array_describe[1][self.mapping[metric]])
                        print("Media encontrada com sucesso!")
        print("Fim da preparação dos dados gerais")

    #source = scenario/csv/1/
    def generate_unit_csv_file(self, distribution, source) :
        print("Criando arquivo csv")
        for k in range(1, 5) :
            pathfile = "{}lane{}/".format(source, k)
            namefile = "lane_simulations.csv"
            self.manager.folder_test(pathfile)
            with open("{}{}".format(pathfile, namefile), "w") as f :
                print("\"Simulation type\";\"Wait time\";\"Queue Length\";\"Mean speeds\"", file = f)
                for i in range(len(distribution["Queue Length"]["Fixed"][1])) :
                    for j in ['Fixed', 'Smart'] :
                        print("\"{}\";\"{}\";\"{}\";\"{}\"".format(j, distribution["Wait time"][j][k][i], distribution["Queue Length"][j][k][i], 0), file = f)
        print("Arquivo csv criado com sucesso!")


    def building_unit_dataframe(self, source) :
        print("Criando dataframe")
        for k in range(1, 5) :
            dataframe = pd.read_csv("{}lane{}/lane_simulations.csv".format(source, k), sep=';', na_values='.')
            for i in self.name_data :
                for j in self.name_type :
                    type_dataframe = dataframe.loc[dataframe['Simulation type'] == self.map[j]]
                    self.lane_dataframe[i][j][k] = type_dataframe[self.map_data[i]]
        print("Dataframe criado com sucesso")

    #source = scenario/result/1/
    def unit_hypothesis_test(self, source) :
        print("Realizando o teste de hipótese")
        for k in range(1, 5) :
            for i in self.name_data :
                recipient = "{}lane{}/{}/".format(source, k, self.map_data[i])
                result = stats.mannwhitneyu(self.lane_dataframe[i]["s"][k], self.lane_dataframe[i]["f"][k])
                self.manager.folder_test(recipient)
                with open("geral/result/lane{}/{}/lane_result.txt".format(k,self.map_data[i]), "w") as f :
                    print("-------------------- analysis --------------------", file = f)
                    print("*** Smart summary", file = f)
                    print("{}\n".format(self.lane_dataframe[i]["s"][k].describe()), file = f)
                    print("*** Fixed summary", file = f)
                    print("{}\n".format(self.lane_dataframe[i]["f"][k].describe()), file = f)
                    print("----- Hypothesis test with Mann-Whitney U test ----", file=f)
                    print("H0 : Smart average = Fixed average", file=f)
                    print("HA : Smart average != Fixed average", file=f)
                    print("Mann-Whitney U test = {}".format(result[0]), file=f)
                    print("p-value = {}".format(result[1]), file=f)
        print("Teste de hipótese finalizado")

    def scenario_boxplot(self, scenario_type) :
        self.reset_scenario_data()
        print("Preparando os dados")
        for metric in ["Queue Length", "Wait time"] :
            for cur_flow in self.flow_scenario[scenario_type]:
                for lane in range(1,5) :
                    path = "report/csv/unit/lane%d/%s" % (lane, cur_flow)
                    data_flow = pd.read_csv(path, sep=";", na_values=".")
                    for simulation_type in self.simulation_type :
                        flow_data_type = data_flow.loc[data_flow["Simulation type"] == simulation_type]
                        array_describe = flow_data_type.describe().get_values()
                        self.scenario_boxplot_data[metric][simulation_type][lane].append(array_describe[1][self.mapping[metric]])
        print("Fim da preparação os dados")



    def run(self) :
        self.initialize()
        self.building_best_results()
        prints.generate_result(self.results, "final", sorted(self.result_order["best"].iteritems(), key = lambda (k,v): (-v,k)))
        prints.generate_total_result(self.total_results["best"],  "best")

report = Report()
report.run()
#report.building_total_results()
report.build_scenario()
'''
for i in xrange(4,9) :
    print("Começo da simulação do", i)
    print(len(report.flow_scenario[i]))
    report.scenario_boxplot(i)
    plotting = Plotting.Plotting()
    plotting.boxplot_plotting(report.best_boxplot_data)
    print("Fim da simulação do", i)
'''

for i in range(1, 2) :
    print("Começo do teste de hipótese dos cenários")
    print("Cenário %d" % i)
    report.scenario_boxplot(i)
    source_csv = "scenario/csv/%d/" % i
    source = "scenario/result/%d/" % i
    report.generate_unit_csv_file(report.scenario_boxplot_data, source_csv)
    report.building_unit_dataframe(source_csv)
    report.unit_hypothesis_test(source_results)
#print(len(report.a["Queue Length"]["best"]))
#report.getting_total_results_data()
#report.generate_unit_csv_file(report.geral_results_data)
#report.building_unit_dataframe()
#report.unit_hypothesis_test()
#report.best_boxplot_simulations_data()
#plotting = Plotting.Plotting()
#plotting.boxplot_plotting(report.geral_results_data)