# Contains parameters and functions for numerical integration engine
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Curve parameters
d_lamda_curve = 0.5
lamda_min_curve = 100
lamda_max_curve = 4500

# Integration parameters
d_lamda_integrate = 10
lamda_min_integrate = 15
lamda_max_integrate = 1e5

# Trapezium parameters
d_lamda_trap = 100
lamda_min_trap = 200
lamda_max_trap = 4500

# Simpson's rule parameters
d_lamda_simp = 100
lamda_min_simp = 200
lamda_max_simp = 4500

# Adaptive Simpson's rule parameters
d_lamda_adap = 3500
lamda_min_adap = 100
lamda_max_adap = 4500

# Physical constants
k_B = 1.381 * (10**-23)
h = 6.626 * (10**-34)
c = 2.998 * (10**8)
sigma_const = 5.670374419 * 1e-8

# Plank's radiation law
def B(lamda, T, is_adap_plot=False, is_adap_integrate=False):
    first_term = 2 * h * (c ** 2) / (lamda ** 5)
    exponential = np.exp(h * c / (lamda * k_B * T))

    if is_adap_plot == True:
        return (first_term * (1 / (exponential - 1))) / 1e9

    if is_adap_integrate == True:
        return (first_term * (1 / (exponential - 1)))

    return [lamda, ((first_term * (1 / (exponential - 1)))) / 1e9]

def return_points(d_lamda, T, lamda_min, lamda_max, is_adap_plot=False):
    lamda = np.arange(lamda_min, lamda_max, d_lamda)
    # Prevent going outside limits
    if lamda[-1] != lamda_max:
        lamda = np.append(lamda, lamda_max)

    if is_adap_plot == True:
        return lamda

    points = B(lamda * 1e-9, T)
    return points

def percent_error(measured, actual):
    return (np.abs(measured - actual) * 100 ) / actual

def sci_notation(num):
    n, exponent = f"{num:.3e}".split("e")
    return rf"${n} \times 10^{{{int(exponent)}}}$"

def trapezium_rule(points):
    # points is a 2D array [[x1,y1], [x2,y2] etc.]
    x = points[:, 0]
    y = points[:, 1]
    n_strips = len(x) - 1
    h = (x[-1] - x[0]) / (2 * n_strips)
    y_sum = 2 * np.sum(points, axis = 0)[1]
    y_sum -= y[0]
    y_sum -= y[-1]
    return h * y_sum

def simpsons_rule(points):
    x = points[:, 0]
    y = points[:, 1]
    n_strips = len(x) - 1
    h = (x[-1] - x[0]) / (3 * n_strips)

    y_first = y[0]
    y_last = y[-1]
    y_odd = y[1:-1:2]
    y_even = y[2:-1:2]
    y_sum = np.sum(y_odd * 4) + np.sum(y_even * 2) + y_first + y_last

    return h * y_sum

# Simpson's rule on only one interval
def simpson_basic(f, T, x1, y1, x2, y2):
    h = (x2 - x1) / 6
    m = (x1 + x2) / 2
    f_m = f(m, T, is_adap_integrate=True)
    return h * (y1 + y2 + 4 * f_m)

# If the new difference is below 15 * tolerance, accept the interval, else split again
def is_acceptable_adaptive(delta, tolerance):
    if np.abs(delta) <= 15 * tolerance:
        return True
    return False

def adaptive_simpson(f, a, b, T, tolerance=1e-8):
    f_a = f(a, T, is_adap_integrate=True)
    f_b = f(b, T, is_adap_integrate=True)
    whole = simpson_basic(f, T, a, f_a, b, f_b)

    m = (a + b) / 2
    f_m = f(m, T, is_adap_integrate=True)

    area_a = simpson_basic(f, T, a, f_a, m, f_m)
    area_b = simpson_basic(f, T, m, f_m, b, f_b)
    delta = area_a + area_b - whole

    if is_acceptable_adaptive(delta, tolerance):
        return area_a + area_b + delta / 15

    return adaptive_simpson(f, a, m, T, tolerance/2) + adaptive_simpson(f, m, b, T, tolerance/2)

def fill_interval(interval, T):
    a, b = interval

    mid = (a + b) / 2

    f_a = B(a * 1e-9, T, is_adap_plot=True)
    f_mid = B(mid * 1e-9, T, is_adap_plot=True)
    f_b = B(b * 1e-9, T, is_adap_plot=True)

    x = [a, mid, b]
    y = [f_a, f_mid, f_b]

    coeffs = np.polyfit([x[0], x[1], x[2]], [y[0], y[1], y[2]], deg=2)
    poly = np.poly1d(coeffs)

    x_curve = np.linspace(x[0], x[2], 100)
    y_curve = poly(x_curve)

    return (x_curve, y_curve)