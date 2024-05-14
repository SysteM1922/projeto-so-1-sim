import matplotlib.pyplot as plt
import numpy as np


euler_kutta = 1     # 1 for Euler, 0 for Runge-Kutta

S0 = 0.8            # fraction of the population that is susceptibe
I0 = 0.1            # fraction of the population that is infected
R0 = 0.1            # fraction of the population that is recovered
BETA = 0.5          # infection rate
K = 0.1             # recovery rate
DELTA_T = 0.1       # time step
T_FINAL = 100       # final time

def ds_dt(s, i):
    return -BETA * s * i

def di_dt(s, i):
    return BETA * s * i - K * i

def dr_dt(i):
    return K * i

def initialize():
    global s0, i0, r0, results_s, results_i, results_r, t_list
    s0 = S0
    i0 = I0
    r0 = R0

    results_s = [s0]
    results_i = [i0]
    results_r = [r0]
    t_list = [0]

def observe():
    global s0, i0, r0, results_s, results_i, results_r, t_list
    results_s.append(s0)
    results_i.append(i0)
    results_r.append(r0)
    t_list.append(t_list[-1] + DELTA_T)

def update():
    global s0, i0, r0, euler_kutta

    if euler_kutta:         # Euler Forward
        s0 += ds_dt(s0, i0) * DELTA_T
        i0 += di_dt(s0, i0) * DELTA_T
        r0 += dr_dt(i0) * DELTA_T
    else:                   # Runge-Kutta
        k1_s = ds_dt(s0, i0) * DELTA_T
        k1_i = di_dt(s0, i0) * DELTA_T
        k1_r = dr_dt(i0) * DELTA_T

        k2_s = ds_dt(s0 + k1_s / 2, i0 + k1_i / 2) * DELTA_T
        k2_i = di_dt(s0 + k1_s / 2, i0 + k1_i / 2) * DELTA_T
        k2_r = dr_dt(i0 + k1_i / 2) * DELTA_T

        k3_s = ds_dt(s0 + k2_s / 2, i0 + k2_i / 2) * DELTA_T
        k3_i = di_dt(s0 + k2_s / 2, i0 + k2_i / 2) * DELTA_T
        k3_r = dr_dt(i0 + k2_i / 2) * DELTA_T

        k4_s = ds_dt(s0 + k3_s, i0 + k3_i) * DELTA_T
        k4_i = di_dt(s0 + k3_s, i0 + k3_i) * DELTA_T
        k4_r = dr_dt(i0 + k3_i) * DELTA_T

        s0 += (k1_s + 2 * k2_s + 2 * k3_s + k4_s) / 6
        i0 += (k1_i + 2 * k2_i + 2 * k3_i + k4_i) / 6
        r0 += (k1_r + 2 * k2_r + 2 * k3_r + k4_r) / 6

def main():
    
    initialize()
    for _ in range(0, int(T_FINAL/DELTA_T)):
        update()
        observe()

    global results_s, results_i, results_r, t_list, euler_kutta

    euler_result_s = results_s
    euler_result_i = results_i
    euler_result_r = results_r

    """
    euler_kutta = 0

    initialize()
    for _ in range(0, int(T_FINAL/DELTA_T)):
        observe()
        update()

    runge_kutta_result_s = results_s
    runge_kutta_result_i = results_i
    runge_kutta_result_r = results_r
    """

    #plt.plot(t_list, runge_kutta_result_s, label='Susceptible_RK')
    plt.plot(t_list, euler_result_s, label='Susceptible_Euler')
    #plt.plot(t_list, runge_kutta_result_i, label='Infected_RK')
    plt.plot(t_list, euler_result_i, label='Infected_Euler')
    #plt.plot(t_list, runge_kutta_result_r, label='Recovered_RK')
    plt.plot(t_list, euler_result_r, label='Recovered_Euler')
    plt.xlabel('Time')
    plt.ylabel('Number of people')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()