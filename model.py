import numpy as np
import gurobipy as gp
from gurobipy import GRB 

def solve_ip(N, T, S, d, a, l, u, alpha):
    '''
    Solve IP and return objective and solution

    Parameters
    ----------
    N : int
        Number of time intervals.
    T : (2, 2) np.array of ints
        Number of starting times at each PSAC for each platoon type.
    S : (2, 2, N, ) list
        Indices of starting times with rostered staff currently working, at each time interval n.
    d : (N, 1) np.array of floats
        Minimum number of call dispatchers required at every time interval n.
    a : (2, 1) np.array of floats
        Proportion of absent staff at each PSAC (e.g. 10%).
    l : (2, 1) np.array of floats
        Minimum number of call dispatchers required at each PSAC.
    u : (2, 1) np.array of floats
        Maximum number of call dispatchers that can be stationed at each PSAC.
    alpha : (2, 1) np.array of floats
        Maximum proportion of E/F staff relative to A/B/C staff at each PSAC.
    '''
    model = gp.Model("IP")

    x1 = model.addVars(T[0][0], vtype=GRB.INTEGER, name="x1") # PSAC 1, Platoon A/B/C
    y1 = model.addVars(T[0][1], vtype=GRB.INTEGER, name="y1") # PSAC 1, Platoon E/F
    x2 = model.addVars(T[1][0], vtype=GRB.INTEGER, name="x2") # PSAC 2, Platoon A/B/C
    y2 = model.addVars(T[1][1], vtype=GRB.INTEGER, name="y2") # PSAC 2, Platoon E/F

    m1 = model.addVars(T[0][0], vtype=GRB.INTEGER, name="m1")
    n1 = model.addVars(T[0][1], vtype=GRB.INTEGER, name="n1")
    m2 = model.addVars(T[1][0], vtype=GRB.INTEGER, name="m2")
    n2 = model.addVars(T[1][1], vtype=GRB.INTEGER, name="n2")
    
    # set objective
    model.setObjective(x1.sum() + x2.sum() + y1.sum() + y2.sum(), GRB.MINIMIZE)
    working = [None for _ in range(N)]
    # set constraints
    for n in range(N):
        p1n = gp.quicksum(x1[t] for t in S[0][0][n]) + gp.quicksum(y1[t] for t in S[0][1][n])
        p2n = gp.quicksum(x2[t] for t in S[1][0][n]) + gp.quicksum(y2[t] for t in S[1][1][n])
        working[n] = p1n + p2n
        model.addConstr(0.75 * ((1 - a[0]) * p1n + (1 - a[1]) * p2n) >= d[n])
        model.addConstr(p1n <= u[0])
        model.addConstr(p1n >= l[0])
        model.addConstr(p2n <= u[1])
        model.addConstr(p2n >= l[1])
    
    model.addConstr(y1.sum() <= alpha[0] * x1.sum())
    model.addConstr(y2.sum() <= alpha[1] * x2.sum())

    model.addConstrs((x1[t] == 4 * m1[t] for t in range(T[0][0])))
    model.addConstrs((y1[t] == 4 * n1[t] for t in range(T[0][1])))
    model.addConstrs((x2[t] == 4 * m2[t] for t in range(T[1][0])))
    model.addConstrs((y2[t] == 4 * n2[t] for t in range(T[1][1])))
    
    return solve(model, T, working)

def solve(m, T, working):
    ''' 
    Return solution to integer program
    '''
    # m.Params.MIPGap = 0.0001   # 0.01%
    m.Params.TimeLimit = 1 * 3600  # 1 hour

    m.optimize()
    print('Obj: %g' % m.objVal)
    x1 = np.array(m.getAttr("X", m.getVars()[:T[0][0]]), dtype=int)
    y1 = np.array(m.getAttr("X", m.getVars()[T[0][0]:T[0][0]+T[0][1]]), dtype=int)
    x2 = np.array(m.getAttr("X", m.getVars()[T[0][0]+T[0][1]:T[0][0]+T[0][1]+T[1][0]]), dtype=int)
    y2 = np.array(m.getAttr("X", m.getVars()[T[0][0]+T[0][1]+T[1][0]:np.sum(T)]), dtype=int)
    
    return m.objVal, x1, y1, x2, y2, [int(expr.getValue()) for expr in working]