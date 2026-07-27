# Photoelectric effect plot displaying the cutoff frequency for different metals

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from random import choice
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
# Physical constants
e = 1.602176620898 * 1e-19
f_min = 0
f_max = 2.5 * 1e15
df = 0.01 * 1e15
h = 6.626 * 1e-34
c = 299792458

def calculate_voltage(f, W):
    first_term = h * f / e
    second_term = W
    return first_term - second_term

def return_points(W):
    f = f_min
    points = []
    while f < f_max:
        points.append([f, calculate_voltage(f, W)])
        f += df
    return points

def f_cutoff(W):
    return W * e / h

def frequency(lamda):
    return c / lamda

def find_ylim(y, ymin, ymax):
    return (y - ymin) / (ymax - ymin)

with open("work_functions.csv") as my_file:
    data = my_file.read().splitlines()

# Work functions data processed into a dictionary
work_functions = {}
elements = []
for line in data:
    line = line.split(",")
    if line[0] != "Material":
        work_functions[line[0]] = float(line[1])
        elements.append(line[0])

# Initialising the GUI
root = tk.Tk()
controls = tk.Frame(root)
controls.pack(side=tk.TOP, fill=tk.X)
root.geometry("1000x800")

# Initialising the axes
plt.rcParams["toolbar"] = "none"
plt.rcParams["mathtext.fontset"] = "cm"
plt.style.use("dark_background")
fig = Figure(figsize=(5, 4), dpi=200)
fig.subplots_adjust(bottom=0.15)

ax = fig.add_subplot()
ax.grid(True, alpha=0.17)
ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0), useMathText=True)

ax.set_xlabel("Frequency /Hz")
ax.set_ylabel("Stopping voltage /V")
ax.autoscale(enable=True, axis="x", tight=True)
ax.autoscale(enable=True, axis="y", tight=True)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()

# Initialising the plot that first appears when opened
length = len(work_functions)
element = "Sodium"
while element == "Sodium":
    element = choice(elements)
work_func = work_functions[element]
points = np.array(return_points(work_func))

# Adding arrow and a box displaying f_cutoff
box_color="#FA3C28"
line, = ax.plot(points[:,0], points[:,1], color='white')
f_c = f_cutoff(work_func)
cutoff_point, = ax.plot(f_c, 0, marker="+", markersize=6.5, color='orange')
ax.set_title(f"Photoelectric Effect: W = {work_func} eV")
ymin, ymax = ax.get_ylim()
cutoff_ylim = 0
y_limit = find_ylim(cutoff_ylim, ymin, ymax)
cutoff_line = ax.axvline(x=f_c, linestyle=(0, (1,0.5)), color='orange', linewidth=2, ymin=0, ymax=y_limit, alpha=0.8)
annotation = ax.annotate(rf'$f_{{\mathrm{{cutoff}}}} = {round(f_c / 1e15, 2)}\times 10^{{15}}\ \mathrm{{Hz}}$', xy=(f_c,0), xytext = (0.95,0.05), textcoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color=box_color), bbox=dict(facecolor='white', edgecolor=box_color, linewidth=0.8), color = 'black', ha="right", va="bottom")

# Plotting lines of visible light
visible_light = {"red": ("#ff3000", 637), "yellow": ("#fff900", 582), "green": ("#4eff00", 526), "blue": ("#00a0ff", 468)}
for color, tuple in visible_light.items():
    color = tuple[0]
    lamda = tuple[1]
    f = frequency(lamda * (1e-9))
    color_line = ax.axvline(x=f, color=color, linewidth=1, linestyle=(0, (1,1)))

# Adjusting axes limits
ax.relim()
bottom, top = ax.get_ylim()
range = top - bottom
const = 0.02
ax.set_ylim(bottom=bottom - const*range, top=top + const*range)
canvas.draw()

def update_plot(element):
    # Replotting points for the new element
    work_function = work_functions[element]
    points = np.array(return_points(work_function))
    line.set_data(points[:,0], points[:,1])

    f_c = f_cutoff(work_function)
    cutoff_point.set_data([f_c], [0])
    annotation.xy = (f_c, 0)
    ax.set_title(f"Photoelectric Effect: W = {work_function}eV")
    annotation.set_text(rf'$f_{{\mathrm{{cutoff}}}} = {round(f_c / 1e15, 2)}\times 10^{{15}}\ \mathrm{{Hz}}$')

    bottom = points[:,1].min()
    top = points[:,1].max()
    y_range = top - bottom
    ax.set_ylim(bottom=bottom - const * y_range, top=top + const * y_range)

    ymin, ymax = ax.get_ylim()
    cutoff_ylim = 0
    y_limit = (cutoff_ylim - ymin) / (ymax - ymin)
    cutoff_line.set_xdata([f_c, f_c])
    cutoff_line.set_ydata([0, y_limit])

    canvas.draw_idle()

# Managing the GUI layout (grid and dropdown menu)
var1 = tk.StringVar()
var1.set(element)
drop = tk.OptionMenu(controls,var1,*elements, command=update_plot)
drop_label = tk.Label(controls, text="Material: ")
drop_label.grid(row=0, column=0, sticky="e")
drop.grid(row=0, column=1, sticky="w")

#toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
#toolbar.update()

canvas.mpl_connect(
    "key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tk.Button(master=root, text="Quit", command=root.destroy)

#toolbar.pack(side=tk.BOTTOM, fill=tk.X)
button_quit.pack(side=tk.BOTTOM)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.wm_title("Photoelectric Effect")
root.mainloop()
