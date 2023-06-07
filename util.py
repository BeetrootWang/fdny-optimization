import numpy as np
from pyworkforce.queuing import ErlangC

def S_table(n, l):
    '''
    Return table of whether staff is working or not at every time interval
    '''
    table = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(l):
            table[i][(i+j) % n] = 1
    return table

def all_start_times(n, s1, s2, st):
    '''
    '''
    return [
        [
            [(s + int(s1) * i) % n for i in range(3) for s in st[0][0]],    # Platoon A/B/C
            [(s + int(s2) * i) % n for i in range(2) for s in st[0][1]]     # Platoon E/F
        ],  # psac 1
        [
            [(s + int(s1) * i) % n for i in range(3) for s in st[1][0]], 
            [(s + int(s2) * i) % n for i in range(2) for s in st[1][1]]
        ]   # psac 2
    ]

def get_S(n, s1, s2, st):
    '''
    '''
    S_abc, S_ef = S_table(n, s1), S_table(n, s2)
    
    S = [
        [S_abc[st[0][0]].T, S_ef[st[0][1]].T],
        [S_abc[st[1][0]].T, S_ef[st[1][1]].T]
    ]
    S[0][0] = [np.asarray(S[0][0][i]).nonzero()[0] for i in range(n)]
    S[0][1] = [np.asarray(S[0][1][i]).nonzero()[0] for i in range(n)]
    S[1][0] = [np.asarray(S[1][0][i]).nonzero()[0] for i in range(n)]
    S[1][1] = [np.asarray(S[1][1][i]).nonzero()[0] for i in range(n)]
    
    return S

def calculate_required_staff(n_calls, awt=36/60, aht=3, interval=60, service_level=0.9, max_utilization=0.85):
    '''
    '''
    erlang = ErlangC(transactions=n_calls, asa=awt, aht=aht, interval=interval, shrinkage=0.)
    requirements = erlang.required_positions(service_level=service_level, max_occupancy=max_utilization)
    return requirements['raw_positions'], erlang

if __name__ == "__main__":
    print(S_table(48, 17))