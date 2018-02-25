from pulp import*
class Solve:

    def __init__(self, cycle, start_context, x_max, lane_weight, lambd, mi, ka, light_time_limits):
        # type: (object, object, object, object, object, object, object, object) -> object

        # Setting variables
        self.start_context = start_context
        self.x_max = x_max
        self.light_time_limits = light_time_limits
        self.lane_weight = lane_weight
        self.lambd = lambd
        self.mi = mi
        self.ka = ka
        self.delta_amb = light_time_limits['amber']
        self.delta = []
        self.cycle = cycle
        self.function = pulp.LpProblem("Traffic light", pulp.LpMinimize)
        self.matrices = {}

        for i in range(cycle):
            self.delta.append(LpVariable("delta_{}".format(i), lowBound=0))

        self.function.addVariables(self.delta)

    def create_matrices(self):

        self.matrices[1] = [self.lambd[1], self.lambd[2] - self.mi[2], self.lambd[3], self.lambd[4] - self.mi[4]]
        self.matrices[2] = [self.lambd[1] - self.mi[1], self.lambd[2], self.lambd[3] - self.mi[3], self.lambd[4]]
        self.matrices[3] = [0, (self.mi[2] - self.ka[2]) * self.delta_amb, 0, (self.mi[4] - self.ka[4]) * self.delta_amb]
        self.matrices[4] = [(self.mi[1] - self.ka[1]) * self.delta_amb, 0, (self.mi[3] - self.ka[3]) * self.delta_amb, 0]
        self.matrices[5] = [0, max((self.lambd[2] - self.ka[2]) * self.delta_amb, 0), 0, max((self.lambd[4] - self.ka[4]) * self.delta_amb, 0)]
        self.matrices[6] = [max((self.lambd[1] - self.ka[1]) * self.delta_amb, 0), 0, max((self.lambd[3] - self.ka[3]) * self.delta_amb, 0), 0]

    def lane_length(self,lane, cycle):
        if cycle == 0:
            return self.start_context[lane]
        else:
            return (self.lane_length(lane, int(cycle) - 1) + \
                    (self.matrices[1][int(lane)] * (self.delta[cycle - 1]) + self.matrices[3][int(lane)]) * (int(cycle) % 2) + \
                    (self.matrices[2][int(lane)] * (self.delta[cycle - 1]) + self.matrices[4][int(lane)]) * (int(cycle + 1) % 2))

    def integrate(self,lane):
        ans = 0
        for cycle in range(self.cycle):
            ans += self.lane_length(lane, cycle)
        return ans

    def J_1(self):
        ans = 0
        for i in range(4):
            ans += self.lane_weight[i] * self.integrate(i)
        return ans

    def set_constraint(self):

        self.create_matrices()
        for i in range(self.cycle):
            self.function.addConstraint(self.light_time_limits['min'][i%2] + self.delta_amb <= self.delta[i])
            self.function.addConstraint(self.light_time_limits['max'][i%2] + self.delta_amb >= self.delta[i])

        ## Set constraint to length lane
        for cycle in range(1, self.cycle):
            for lane in range(4):
                self.function.addConstraint(LpAffineExpression(self.lane_length(lane, cycle) - \
                                                          self.x_max[lane] - self.matrices[5][lane] * (int(cycle) % 2) - self.matrices[6][lane] * (int(cycle + 1) % 2)) <= 0)
    def setting_functions(self) :
        self.set_constraint()
        self.function.setObjective(self.J_1())

    def try_solve(self) :
        self.function.solve(pulp.GLPK(options=['--nopresol']))  # Command to try solve problem
        self.function.writeLP("report/out/Traffic light.lp")  # Write file with caracteristic of problem
        print ("Status:", self.function.status)
        return self.function.status

    def get_answer(self):
        print(str(self.J_1()) + " = " + str(value(self.J_1())))
        ans = []
        print(self.function.variables())
        for v in self.function.variables():
            if v.name == "__dummy":
                continue
            print(v.name, "=", v.varValue)
            ans.append( int(v.varValue) )
        return ans

debug = 0
if debug:
    ### Start context
    startcontext = [ 6 , 9 , 5 , 2 ]
    ## Limits
    x_max = [25, 20, 25, 20] # Lenght max of lanes
    delta_min_green_1 = delta_min_green_2 = 6 # Time min of traffic light
    delta_max_green_1 = delta_max_green_2 = 60 # Time max of traffic light
    weight = [2,1,2,1] # Weight of lanes
    delta_amb = 3 # Traffic Light in amber always 3 times
    lambd = {}
    lambd[1] = 0.29166
    lambd[2] = 0.125
    lambd[3] = 0.2916
    lambd[4] = 0.111
    mi = {}
    mi[1] = 0.125
    mi[2] = 0.125
    mi[3] = 0.125
    mi[4] = 0.11111

    ka = {}
    ka[1] = 0.0277
    ka[2] = 0.0277
    ka[3] = 0.0416
    ka[4] = 0.0416

    light_time = {}

    light_time['amber'] = 3

    light_time['min'] = [6,6]
    light_time['max'] = [60,60]

    print ("-----------------------------------------------------------------")

    solve = Solve(cycle=8, start_context=startcontext, x_max=x_max, lane_weight=weight, lambd=lambd, mi=mi, ka=ka, light_time_limits=light_time)

    solve.setting_functions()
    solve.try_solve()
    solve.get_answer()
