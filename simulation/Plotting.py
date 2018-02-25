import matplotlib.pyplot as plt
import ManagerDir
class Plotting:

    def __init__(self):
        print("Iniciou o plot")
        self.manage = ManagerDir.ManagerDir()
        self.manage.create("report/imgs")
        self.color = {}
        self.names = {}
        self.color['f'] = 'b'
        self.color['s'] = 'r'
        self.names['f'] = "Fixed"
        self.names['s'] = "Smart"

    def plot(self,data,grides):
        figs = {}
        plots = {}
        for i in data:
            figs[i] = plt.figure()

        for i in figs:
            value = figs[i]
            plots[i] = {}
            for j in range(1,5):
                plots[i][j] = value.add_subplot(2, 2, j)

        for key in data:
            type = data[key]
            for id in type:
                value = type[id]
                for j in range(1,5):
                    plots[key][j].plot([_ for _ in range(len(value[j]))], value[j], self.color[id], label=self.names[id])

        for key in plots:
            for id in range(1,5):
                plots[key][id].set_title('Lane {}'.format(id))
                plots[key][id].set_xlabel('Tempo')
                plots[key][id].set_xticks(grides)
                plots[key][id].xaxis.grid()
                plots[key][id].legend()

        self.manage.create("report/imgs/")
        for key in figs:
            figs[key].suptitle(key, fontsize=20)
            figs[key].set_size_inches(15,10)
            figs[key].savefig("report/imgs/Grafico_{}.png".format(key))


    def boxplot_plotting(self, data):
        figs = {}
        plots = {}
        colors = ['none','none']
        dashs = ['/','.']
        legends = ["Fixed", "Smart"]
        for i in data:
            figs[i] = plt.figure()
            figs[i].suptitle(i)

        for i in figs:
            value = figs[i]
            plots[i] = {}
            for j in range(1,5):
                plots[i][j] = value.add_subplot(2, 2, j)

        for key in data:
            type = data[key]
            for j in range(1,5):
                box1 = type["Fixed"][j]
                box2 = type["Smart"][j]
                box = plots[key][j].boxplot([box1,box2],patch_artist=True,labels=["Fixed", "Smart"])
                for patch,color,dash,legend in zip(box['boxes'],colors,dashs, legends):
                    patch.set_facecolor(color)
                    patch.set_hatch(dash)
                    patch.set_label(legend)

                plots[key][j].grid()
                plots[key][j].set_title('Lane {}'.format(j))
        
        plt.show()
