import numpy as np
import matplotlib.pyplot as plt

def plot_roster_start(n_time_intervals, start_times, x1, y1, x2, y2):

    s = list(range(n_time_intervals))
    # s = np.arange(np.datetime64("2023-06-06"), np.datetime64("2023-06-07"), np.timedelta64(30, "m"))
    sx1, sx2, sy1, sy2 = np.zeros(n_time_intervals), np.zeros(n_time_intervals), \
        np.zeros(n_time_intervals), np.zeros(n_time_intervals)
    sx1[start_times[0][0]] = x1
    sy1[start_times[0][1]] = y1
    sx2[start_times[1][0]] = x2
    sy2[start_times[1][1]] = y2

    plt.bar(s, sx1, label="PSAC 1, Platoon A/B/C", color="lightblue")
    plt.bar(s, sy1, bottom=sx1, label="PSAC 1, Platoon E/F", color="darkblue")
    plt.bar(s, sx2, bottom=sx1+sy1, label="PSAC 2, Platoon A/B/C", color="lightcoral")
    plt.bar(s, sy2, bottom=sx1+sy1+sx2, label="PSAC 2, Platoon E/F", color="darkred")
    plt.legend()
    plt.title("Staff Rostered at Different Starting Times")
    plt.xlabel("Time Interval")
    plt.ylabel("Count")
    plt.show()

def plot_staff_required_working(staff_rostered, required_staff):

    plt.plot(staff_rostered, label="Staff Working")
    plt.plot(required_staff, label="Required Dispatchers Seated")
    plt.ylabel("Count")
    plt.xlabel("Time Interval") 
    plt.title("Rostered Staff over Time (w.r.t. absences and 4-staff-3-seat rule)")
    plt.legend()
    plt.show()

def plot_utilizations(utilizations):

    plt.plot(utilizations)
    plt.ylabel("Proportion")
    plt.xlabel("Time Interval")
    plt.title("Utilization over Time")
    plt.show()

def plot_all(n_time_intervals, start_times, staff_rostered, required_staff, utilizations, x1, y1, x2, y2):

    plot_staff_required_working(staff_rostered, required_staff)
    plot_roster_start(n_time_intervals, start_times, x1, y1, x2, y2)
    plot_utilizations(utilizations)