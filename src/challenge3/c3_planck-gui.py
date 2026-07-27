# GUI - takes input as temperature and plots Planck Spectrum at that temperature

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from random import random
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

# Physical constants
k_B = 1.381 * (10 ** -23)
h = 6.626 * (10 ** -34)
c = 2.998 * (10 ** 8)
d_lamda = 0.1

# Planck's radiation law
def B(lamda, T):
    global k_B, h, c
    first_term = 2 * h * (c ** 2) / (lamda ** 5)
    exponential = np.exp(h * c / (lamda * k_B * T))
    return (first_term * (1 / (exponential - 1)))

# Returns points to plot for lamda between 100 and 2500nm
def return_points(d_lamda, T):
    lamda = 100
    points = []
    while lamda < 2500:
        points.append([lamda, (B(lamda * 10 ** -9, T) * np.pi / 10 ** 9)])
        lamda += d_lamda
    return points

# Choosing colours uniformly from autumn colormap
def choose_colors(n):
    colors = plt.cm.autumn(np.linspace(0, 1, n))
    return colors

# Determining if an item is in a list of lists
def item_in(item, lst):
    for sub_list in lst:
        if item in sub_list:
            return True
    return False

# Initialising the GUI
root = tk.Tk()
controls = tk.Frame(root)
controls.pack(side=tk.TOP, fill=tk.X)
root.wm_title("Planck Spectrum plot")
root.geometry("800x700")

# Setting up the initial plot when the GUI is opened
plt.style.use("dark_background")
fig = Figure(figsize=(5, 5), dpi=150)
ax = fig.add_subplot()
ax.set_title("Planck Spectrum - B(λ, T)")
fig.subplots_adjust(left=0.15, right=0.95)
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)

# temperatures is a list of lists. In each list, index 0 is the temperature, and index 1 is the corresponding line
original_temps = [[4000], [5000], [6000]]
colors = choose_colors(len(original_temps))[::-1]

# Plotting the intial points for T = 4000, 5000 and 6000K
for i, item in enumerate(original_temps):
    item = item[0]
    points = np.array(return_points(d_lamda, item))
    line, = ax.plot(points[:, 0], points[:, 1], label=f"{item} K", color=colors[i])
    original_temps[i].append(line)

for i in range(2):
    controls.columnconfigure(i, weight=1)

ax.set_xlabel("Wavelength / nm")
ax.set_ylabel("Irradiance / $Wm^{-2}/nm$")
ax.autoscale(enable=None, axis="x", tight=True)
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()

# Setting up the widget for user entry of a new temperature to plot
temp_label = tk.Label(controls, text="New temperature:")
temp_label.grid(row=0, column=0, sticky="e")
entry = tk.Entry(controls)
entry.grid(row=0, column=1, sticky="w")

has_started = False
temperatures = []
middle_color = plt.cm.autumn(0.5)

# Function called when user input changes
def update_plot(event):
    global has_started, temperatures
    # If the return key is pressed, there is a new temperature to plot
    if event.keysym == "Return":
        temp = entry.get()
        entry.delete(0, tk.END)
        try:
            new_temp = int(temp)
            if new_temp <= 0:
              return
        except ValueError:
            return
        points = np.array(return_points(d_lamda, new_temp))

        # This is the first time the input has been updated
        if has_started == False:
            has_started = True

            for lst in original_temps:
                line = lst[1]
                line.remove()

            new_line, = ax.plot(points[:, 0], points[:, 1], label=f"{new_temp} K", color=middle_color)
            temperatures.append([new_temp, new_line])
            ax.legend()

        else:
            if item_in(new_temp, temperatures) == True:
                return

            new_line, = ax.plot(points[:, 0], points[:, 1], label=f"{new_temp} K", color=middle_color)
            temperatures.append([new_temp, new_line])
            length = len(temperatures)

            temperatures = sorted(temperatures, key=lambda x: x[0])
            colors = choose_colors(length)[::-1]

            for i, lst in enumerate(temperatures):
                lst[1].set_color(colors[i])

            ax.autoscale(enable=None, axis="x", tight=True)

            h, l = plt.gca().get_legend_handles_labels()
            new_h = []
            new_l = []
            for lst in temperatures:
                current_temp = lst[0]
                label = f"{current_temp} K"
                current_line = lst[1]
                new_h.append(current_line)
                new_l.append(label)

            ax.legend(new_h, new_l)
        canvas.draw()

entry.bind("<KeyRelease>", update_plot)

toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.mpl_connect(
    "key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tk.Button(master=root, text="Quit", command=root.destroy)

toolbar.pack(side=tk.BOTTOM, fill=tk.X)
button_quit.pack(side=tk.BOTTOM)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

tk.mainloop()
