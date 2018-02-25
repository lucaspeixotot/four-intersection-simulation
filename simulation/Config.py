import os
import sys
import optparse

class Config:
    def __init__(self):
        try :
            if 'SUMO_HOME' in os.environ:
                self.tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
                sys.path.append(self.tools)
                from sumolib import checkBinary
                self.checkBinary = checkBinary
            else :
                sys.exit("please declare environment variable 'SUMO_HOME'")
        except ImportError:
            sys.exit(
                "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")
        import traci
        self.traci = traci

    def get_options(self):
        optParser = optparse.OptionParser()
        optParser.add_option("--nogui", action="store_true",
                             default=False, help="run the commandline version of sumo")
        options, args = optParser.parse_args()
        return options

    def run(self):
        self.options = self.get_options()

        if self.options.nogui:
            self.sumoBinary = self.checkBinary('sumo')
        else:
            self.sumoBinary = self.checkBinary('sumo')
        self.traci.start([self.sumoBinary, "-c", "data/schutter.sumocfg", "--additional-files", "data/schutter_add.xml",
                     "--tripinfo-output", "tripinfo.xml", "--step-length", "1"])
