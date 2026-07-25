# 2D random walks GUI with sliders to adjust step number, step size and number of walks using Tkinter and Matplotlib

from random import uniform, choice
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

# Setting default parameters for graph that appears when GUI is opened
orig_step_number = 2500
orig_step_size = 1
orig_walk_number = 50

# Random walk with n steps of size s - returns a list of a list of x,y positions
def random_walk(n: int, s: int):
    angle = np.random.uniform(0, 2*np.pi, n)
    x = s * np.cos(angle)
    y = s * np.sin(angle)
    return [np.cumsum(x),np.cumsum(y)]

# Creating an array of colours from the matplotlib library, specifically the gist_ncar type.
def choose_colors(iteration_number):
    colors = plt.cm.gist_ncar(np.linspace(0, 1, iteration_number))
    return colors

# Initialising the GUI
root = tk.Tk()
controls = tk.Frame(root)
controls.pack(side=tk.TOP, fill=tk.X) # Allows me to use grid as well as pack
root.wm_title("Random Walks GUI")
root.geometry("1040x910")

plt.style.use("dark_background")
fig = Figure(figsize=(5,5), dpi=100)
ax = fig.add_subplot()

# Creating the default plot when the GUI is opened
orig_colors = choose_colors(orig_walk_number)
for i in range(orig_walk_number):
    default_list = random_walk(orig_step_number, orig_step_size)
    line, = ax.plot(default_list[0], default_list[1], marker = "o", markersize = 0.2, markeredgecolor='none', linewidth = 0.35, color = orig_colors[i])

ax.set_xlabel("x")
ax.set_ylabel("y")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw_idle()

toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.mpl_connect(
    "key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tk.Button(master=root, text="Quit", command=root.destroy)

# Function that is called whenever the sliders are updated
def update_plot(new_value):
    # Reset the axes
    ax.clear()
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    walk_number = int(walk_number_slider.get())
    step_size = int(step_size_slider.get())
    step_number = int(step_number_slider.get())

    colors = choose_colors(walk_number)
    for i in range(walk_number):
        lst = random_walk(step_number, step_size)
        line, = ax.plot(lst[0], lst[1],  marker = "o", markersize = 0.1, markeredgecolor='none', linewidth = 0.35, color = colors[i])

    canvas.draw_idle()

# Creating the sliders
step_number_slider = tk.Scale(controls, from_=10, to=5000, orient=tk.HORIZONTAL,
                              command=update_plot)

walk_number_slider = tk.Scale(controls, from_=10, to=200, orient=tk.HORIZONTAL,
                              command=update_plot)

step_size_slider = tk.Scale(controls, from_=1, to=100, orient=tk.HORIZONTAL,
                              command=update_plot)

# Initialising the values of the sliders
step_size_slider.set(orig_step_size)
step_number_slider.set(orig_step_number)
walk_number_slider.set(orig_walk_number)

# Configuring the grid setup
for i in range(3):
    controls.columnconfigure(i, weight=1)

# Creating labels for grid, as default labels aren't centered (visually offputting)
label_walk_no = tk.Label(controls, text="Number of walks", anchor="center")
label_walk_no.grid(row=0, column=0, sticky="ew")

label_step_no = tk.Label(controls, text="Number of steps", anchor="center")
label_step_no.grid(row=0, column=1, sticky="ew")

label_step_size = tk.Label(controls, text="Step size", anchor="center")
label_step_size.grid(row=0, column=2, sticky="ew")

walk_number_slider.grid(row=1, column=0, sticky="ew")
step_number_slider.grid(row=1, column=1, sticky="ew")
step_size_slider.grid(row=1, column=2, sticky="ew")

toolbar.pack(side=tk.BOTTOM, fill=tk.X)
button_quit.pack(side=tk.BOTTOM)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

tk.mainloop()