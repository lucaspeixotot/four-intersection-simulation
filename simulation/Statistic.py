from __future__ import absolute_import
from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import ManagerDir
import BuildingResults
import BuildingResultsMeanSpeeds
from scipy import stats

class Statistic :
    def __init__(self) :
        self.initialize_variables()
        self.manager = ManagerDir.ManagerDir()

    def initialize_variables(self) :
        self.simulation_type = ['f', 's']
        self.alpha = 0.05
        self.map = {}
        self.map["s"] = "Smart"
        self.map["f"] = "Fixed"
        self.map_data = {}
        self.map_data['queue'] = "Queue Length"
        self.map_data['wait_time'] = "Wait time"
        self.map_data['mean_speeds'] = "Mean speeds"
        self.name_data = ["wait_time", "queue", "mean_speeds"]
        self.name_type = ['f', 's']
        self.buildingResults = {}
        self.buildingResults["queue"] = BuildingResults.BuildingResults("Queue Length")
        self.buildingResults["wait_time"] = BuildingResults.BuildingResults("Wait time")
        self.buildingResults["mean_speeds"] = BuildingResultsMeanSpeeds.BuildingResultsMeanSpeeds()
        self.dataframe = {}
        self.dataframe_type = {}
        self.dataframe_metrics = {}
        self.flow_dataframe_metrics = {}
        for i in self.name_data :
            self.dataframe_metrics[i] = {}
            self.flow_dataframe_metrics[i] = {}
            for j in self.name_type :
                self.dataframe_metrics[i][j] = {}
                self.flow_dataframe_metrics[i][j] = {}

# UNIT RESULTS AREA
    def run_unit_result(self, lambd, distribution) :
        self.lambd = lambd
        self.generate_unit_csv_file(distribution)
        self.building_unit_dataframe()
        self.unit_hypothesis_test()

    def generate_unit_csv_file(self, distribution) :
        for k in range(1, 5) :
            pathfile = "report/csv/unit/lane{}/".format(k)
            namefile = "flow_{}_{}_{}_{}.csv".format(self.lambd[0], self.lambd[1], self.lambd[2], self.lambd[3])
            self.manager.folder_test(pathfile)
            with open("{}{}".format(pathfile, namefile), "w") as f :
                print("\"Simulation type\";\"Wait time\";\"Queue Length\";\"Mean speeds\"", file = f)
                for i in range(len(distribution["queue"]["f"][1])) :
                    for j in self.simulation_type :
                        print("\"{}\";\"{}\";\"{}\";\"{}\"".format(self.map[j], distribution["wait_time"][j][k][i], distribution["queue"][j][k][i], distribution["mean_speeds"][j][k][i]), file = f)

    def building_unit_dataframe(self) :
        for k in range(1, 5) :
            dataframe = pd.read_csv("report/csv/unit/lane{}/flow_{}_{}_{}_{}.csv".format(k, self.lambd[0], self.lambd[1], self.lambd[2], self.lambd[3]), sep=';', na_values='.')
            for i in self.name_data :
                for j in self.name_type :
                    type_dataframe = dataframe.loc[dataframe['Simulation type'] == self.map[j]]
                    self.flow_dataframe_metrics[i][j][k] = type_dataframe[self.map_data[i]]

    def unit_hypothesis_test(self) :
        for k in range(1, 5) :
            for i in self.name_data :
                recipient = "report/results/lane{}/{}/inconclusive/".format(k, self.map_data[i])
                result = stats.mannwhitneyu(self.flow_dataframe_metrics[i]["s"][k], self.flow_dataframe_metrics[i]["f"][k])
                if result[1] < self.alpha :
                    recipient = self.buildingResults[i].execute(self.flow_dataframe_metrics[i]["s"][k].mean(), self.flow_dataframe_metrics[i]["f"][k].mean(), k)
                self.write_unit_hypothesis_test(recipient, self.flow_dataframe_metrics[i]["s"][k], self.flow_dataframe_metrics[i]["f"][k], result)

    def write_unit_hypothesis_test(self, recipient, val_s, val_f, result) :
        self.manager.folder_test(recipient)
        with open("{}flow_{}_{}_{}_{}.txt".format(recipient, self.lambd[0], self.lambd[1], self.lambd[2], self.lambd[3]), "w") as f :
            print("-------------------- analysis --------------------", file = f)
            print("*** Smart summary", file = f)
            print("{}\n".format(val_s.describe()), file = f)
            print("*** Fixed summary", file = f)
            print("{}\n".format(val_f.describe()), file = f)
            print("----- Hypothesis test with Mann-Whitney U test ----", file=f)
            print("H0 : Smart average = Fixed average", file=f)
            print("HA : Smart average != Fixed average", file=f)
            print("Mann-Whitney U test = {}".format(result[0]), file=f)
            print("p-value = {}".format(result[1]), file=f)

# END UNIT RESULTS AREA

# TOTAL RESULTS AREA

    def run_total_result(self) :
        # self.generate_csv_total_file()
        self.building_total_dataframes()
        self.total_hypothesis_test()

    def generate_csv_total_file(self) :
        for k in range(1,5) :
            with open("report/csv/lane_{}.csv".format(k), "w") as csv :
                print("\"Flow\";\"Simulation type\";\"Wait time\";\"Queue Length\";\"Mean speeds\"", file = csv)
                for i in range(len(data_distribution["queue"]["f"][k])) :
                    for stype in self.simulation_type :
                        print("\"{}\";\"{}\";\"{}\";\"{}\";\"{}\"".format((i+1)*0.025, self.map[stype], data_distribution["wait_time"][stype][k][i], data_distribution["queue"][stype][k][i], data_distribution["mean_speeds"][stype][k][i]), file = csv)

    def building_total_dataframes(self):
        for i in range(1, 5) :
            self.dataframe[i] = pd.read_csv("report/csv/lane_{}.csv".format(i), sep=';', na_values=".")
            for j in self.name_data :
                for k in self.name_type :
                    self.dataframe_type[k] = self.dataframe[i].loc[self.dataframe[i]['Simulation type'] == self.map[k]]
                    self.dataframe_metrics[j][k][i] = self.dataframe_type[k][self.map_data[j]]

    def total_hypothesis_test(self) :
        for k in range(1,5) :
            with open("report/results/average_lane_{}.txt".format(k), "w") as f :
                for i in self.name_data :
                    print("-------------------- {} analysis --------------------".format(self.map_data[i]), file=f)
                    for j in self.name_type :
                        print("*** {} summary".format(self.map[j]), file=f)
                        print("{}\n".format(self.dataframe_metrics[i][j][k].describe()), file=f)
                    result = stats.mannwhitneyu(self.dataframe_metrics[i]["s"][k], self.dataframe_metrics[i]["f"][k])
                    print("----- Hypothesis test with Mann-Whitney U test ----", file=f)
                    print("H0 : Smart average {} = Fixed average {}".format(self.map_data[i], self.map_data[i]), file=f)
                    print("HA : Smart average {} != Fixed average {}".format(self.map_data[i], self.map_data[i]), file=f)
                    print("Mann-Whitney U test = {}".format(result[0]), file=f)
                    print("p-value = {}".format(result[1]), file=f)
                    if result[1] >= 0.05 :
                        print("The p-value is larger than alpha={}, so with 95% confidence level we cannot reject the null hypothesis.".format(0.05), file=f)
                    else :
                        print("The p-value is smaller than alpha={}, so with 95% confidence level we can reject the null hypothesis.".format(0.05), file=f)
                    print("-------------------- end analysis --------------------\n\n\n", file=f)

    def box_plotting(self) :
        for i in range(1, 5) :
            dataframe = pd.read_csv("report/csv/lane_{}.csv".format(i), sep=';', na_values=".")
            type_data = dataframe.groupby('Simulation type')
            type_data.boxplot(column=['Queue Length', 'Wait time'])
            # plot.show()
