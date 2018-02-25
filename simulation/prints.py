# -*- coding:utf-8 -*-
from __future__ import print_function

metrics_name = ["Queue Length", "Wait time", "Mean speeds"]
minified_metric = {"Queue Length": "QL", "Wait time": "WT", "Mean speeds": "MS"}
results_name = ["best", "inconclusive", "worst"]
minifed_results = {"best": 'B', "inconclusive": 'I', "worst": 'W'}
def generate_result(result, name, a) :
    with open("report/final/{}.csv".format(name), "w") as  f :
        #print("------------------------------ Relatório final dos resultados {} ------------------------------".format(name), file=f)
        print("\"Flow\"", end='', file=f)
        for metric in metrics_name:
            for r in results_name :
                print(",\"", minified_metric[metric], minifed_results[r], "\"", sep='', end='', file=f)
        print(",\"Quantity\"", file=f)
        for item in a :
            flow, quantity = str(item[0]), int(item[1])
            print("\"", flow_name_parser(flow), "\"", sep='', end='', file=f)
            for metric in metrics_name :
                for r in results_name :
                    #print(metric, end='')
                    #print(result[r][flow][metric])
                    gg = "; ".join([str(_) for _ in result[r][flow][metric]])
                    print(",\"", gg, "\"", sep='', end='', file=f)
            print(",\"", quantity, "\"", file=f)

def generate_total_result(result, name) :
    with open("report/final/{}".format(name + ".txt"), "w") as  f :
        print("------------------------------ Relatório final dos resultados {} ------------------------------".format(name), file=f)
        for i in metrics_name :
            print("***** \t\tResultados referentes a métrica \"{}\"\t\t *****\n".format(i), file=f)
            for j in range(1,5) :
                if result[i][j] == 0: continue
                print("Tivemos {} configuração(ões) onde o resultado foi {} em {} lane(s)".format(result[i][j]*4 ,name, j), file=f)

def flow_name_parser(flow_name):
    new_flow_name = flow_name[5:len(flow_name)]
    new_flow_name = new_flow_name[0:len(new_flow_name) - 4]
    new_flow_name, aux = " ", new_flow_name.split('_')
    for i in aux :
        new_flow_name += i + " "
    return(new_flow_name)
