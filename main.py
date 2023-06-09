import numpy as np
import pandas as pd
from util import get_S, all_start_times, calculate_required_staff
from model import solve_ip
from plots import plot_all

def optimize(n_time_intervals, shift_length_abc, shift_length_ef, minimum_staff, maximum_staff,
             maximum_ef_abc_proportions, proportion_absent, predicted_calls, required_service_level, 
             acceptable_waiting_time, average_call_time, interval_length, maximum_utilization, 
             first_start_times=None, restricted_times=None, total_unique_start_times=None):
    '''
    Find the minimum number of staff to roster and how they should be rostered
    '''
    # requirements for given service level
    required_staff, erlangs = zip(*[calculate_required_staff(
        n_calls, awt=acceptable_waiting_time, aht=average_call_time, interval=interval_length, 
        service_level=required_service_level, max_utilization=maximum_utilization
        ) for n_calls in predicted_calls])
    
    if len(required_staff) == 24:
        required_staff = [a for a in required_staff for _ in range(n_time_intervals // 24)]
        erlangs = [a for a in erlangs for _ in range(n_time_intervals // 24)]

    # initialize set of start times
    start_times = all_start_times(n_time_intervals, shift_length_abc, shift_length_ef, first_start_times, restricted_times)
    n_start_times = [[len(start_times[0][0]), len(start_times[0][1])], 
                     [len(start_times[1][0]), len(start_times[1][1])]]
    S_ = get_S(n_time_intervals, shift_length_abc, shift_length_ef, start_times)

    # solve and get metrics
    obj, x1, y1, x2, y2, n_staff = solve_ip(N=n_time_intervals, T=n_start_times, S=S_, d=required_staff, 
                                   a=proportion_absent, l=minimum_staff, u=maximum_staff, 
                                   alpha=maximum_ef_abc_proportions, tust=total_unique_start_times)
    
    metrics = [
        (erlangs[i].achieved_occupancy(n), erlangs[i].service_level(n), erlangs[i].waiting_probability(n)) 
        for i, n in enumerate(n_staff)
        ]

    return obj, x1, y1, x2, y2, list(zip(*metrics)), n_staff, required_staff, start_times

if __name__ == "__main__":

    ############## parameters (indexed by platoon type) ##############
    n_time_intervals = 48
    shift_length_abc = 17
    shift_length_ef = 24
    minimum_staff = [11, 11]
    maximum_staff = [31, 30]
    maximum_ef_abc_proportions = [0.5, 0.5]
    proportion_absent = [0.1, 0.1]

    # encoded as indices (e.g. 14 means 7.30am)
    first_start_times = [ 
        [[13, 14, 15, 16, 17, 18, 19], [13, 14, 15, 16, 17, 18, 19]],   # PSAC 1
        [[13, 14, 15, 16, 17, 18, 19], [13, 14, 15, 16, 17, 18, 19]]    # PSAC 2
    ] # columns are platoon type (A/B/C and E/F, resp.)
    restricted_times = [ 
        [[14, 18], [16, 17]],   # PSAC 1
        [[18, 19], [13, 14]]    # PSAC 2
    ]
    total_unique_start_times = np.array([[3], [3]]) # np.array([[3, 3],[3, 3]])
    
    # queuing model
    required_service_level = 0.9
    predicted_calls = np.array(pd.read_csv("data/Call_prediction_new_service_level.csv")["Prediction_Calls"])
    acceptable_waiting_time = 36/60 # minutes
    average_call_time = 3
    interval_length = 60
    maximum_utilization = 0.85
    ##################################################################
    
    total, x1, y1, x2, y2, (utilizations, service_levels, delay_probabilities), \
        staff_rostered, required_staff, start_times = optimize(
        n_time_intervals, shift_length_abc, shift_length_ef, minimum_staff, maximum_staff,
        maximum_ef_abc_proportions, proportion_absent, predicted_calls,
        required_service_level, acceptable_waiting_time, average_call_time, interval_length,
        maximum_utilization, first_start_times, restricted_times, total_unique_start_times
        )

    plot_all(n_time_intervals, start_times, staff_rostered, required_staff, utilizations, x1, y1, x2, y2)